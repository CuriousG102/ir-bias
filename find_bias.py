import csv
from functools import lru_cache

import gensim
from gensim.models import Word2Vec
import numpy as np
from sklearn import svm, model_selection
from sklearn.decomposition import PCA

from explore import judge_model_quality
from model_data import DataManager
from settings import settings

class BiasExplorer:
    '''
    Probably not thread safe
    '''
    def __init__(self, train_cutoff=50000,
                 dm_temp_path=settings['temp_path'],
                 dm_save_path=settings['save_path'],
                 svm_class_cost={'positive': 1,
                                 'negative': 1},
                 svm_C=1, svm_kernel='linear',
                 kfold_n_splits=10,
                 accuracy_cutoff=.4,
                 golden_model_path=settings['golden_model_path'],
                 positive_words_path=settings['positive_words_path'],
                 word_filter=lambda w: w.isalpha() and len(w) <= 20,
                 word_pairs_path=settings['word_pairs_path']):
        self.train_cutoff = train_cutoff
        self.data_manager = DataManager(dm_temp_path, dm_save_path)
        self.svm_class_cost = svm_class_cost
        self.svm_C = svm_C
        self.svm_kernel = svm_kernel
        self.kfold_n_splits=kfold_n_splits
        self.accuracy_cutoff = accuracy_cutoff
        self.golden_model_path = golden_model_path
        self.positive_words_path = positive_words_path
        self.word_filter = word_filter
        self.word_pairs_path = word_pairs_path

    def normalize(self, vector):
        return vector/np.linalg.norm(vector)

    @lru_cache()
    def get_eligible_sources(self):
        sources = []
        for source in self.data_manager.get_available_source_models():
            print('Judging accuracy for %s' % source)
            model = self.data_manager.get_model_for_source(source)
            _, accuracy = judge_model_quality(model)
            print('Accuracy: %f' % accuracy)
            if accuracy >= self.accuracy_cutoff:
                sources.append(source)
        return sources

    def top_words_by_count(self, model, use_train_cutoff=False):
        if use_train_cutoff:
            words_by_count = sorted(model.vocab.items(),
                                    key=lambda x: x[1].count,
                                    reverse=True)
        else:
            words_by_count = model.vocab.items()
        if use_train_cutoff:
            top_words = words_by_count[:self.train_cutoff]
        else:
            top_words = words_by_count
        top_words = [w for w, attr in top_words if self.word_filter(w)]
        return top_words

    @lru_cache()
    def top_words_by_source(self, source, use_train_cutoff):
        print('Getting top words for %s' % source)
        source_model = self.data_manager.get_model_for_source(source)
        return self.top_words_by_count(source_model,
                                       use_train_cutoff=use_train_cutoff)

    @lru_cache()
    def top_words_golden(self, use_train_cutoff):
        print('Getting top words for Golden')
        golden_model = Word2Vec.load_word2vec_format(self.golden_model_path,
                                                     binary=True)
        top_words = self.top_words_by_count(golden_model, 
                                            use_train_cutoff=use_train_cutoff)
        top_words = set([w.lower() for w in top_words])
        return top_words

    @lru_cache()
    def get_positive_words(self):
        with open(self.positive_words_path) as f:
            return [row[0].strip() for row in csv.reader(f)]

    @lru_cache()
    def get_common_positive_words(self):
        top_golden_words = self.top_words_golden(True)
        
        positive_words = self.get_positive_words()
        positive_words = set(top_golden_words) & set(positive_words)

        for source in self.get_eligible_sources():
            positive_words &= set(self.top_words_by_source(source, False))

        return positive_words

    @lru_cache()
    def get_common_neutral_words(self):
        top_golden_words = self.top_words_golden(True)
        neutral_words = top_golden_words - set(self.get_common_positive_words())

        for source in self.get_eligible_sources():
            neutral_words &= set(self.top_words_by_source(source, False))

        return neutral_words

    def get_gendered_word_prediction_model(self, source):
        """
        Precondition: source must be in the list of eligible sources
        """
        assert(source in self.get_eligible_sources())
        w2v_model = self.data_manager.get_model_for_source(source)
        # positive - gendered
        positive_words = self.get_common_positive_words()   
        print('normalizing positive embeds: %i exist' % len(positive_words))
        positive_embeds = [self.normalize(w2v_model[word]) for word in positive_words]
        # negative - not gendered
        neutral_words = self.get_common_neutral_words()
        print('normalizing neutral embeds: %i exist' % len(neutral_words))
        neutral_embeds = [self.normalize(w2v_model[word]) for word in neutral_words]

        training_embeds = positive_embeds + neutral_embeds
        training_results = np.concatenate((np.ones(len(positive_embeds)),
                                          np.zeros(len(neutral_embeds))))
        
        X = np.array(training_embeds)
        Y = training_results
        kfold = model_selection.KFold(n_splits=self.kfold_n_splits, 
                                      shuffle=True)
        def get_pred_model():
            return svm.SVC(C=self.svm_C, kernel=self.svm_kernel,
                           class_weight={0:self.svm_class_cost['negative'],
                                         1:self.svm_class_cost['positive']})
        print('running kfold validation')
        scores = []
        for i, (train_idx, test_idx) in enumerate(kfold.split(X)):
            print('running fold %i' % i)
            pred_model = get_pred_model()    
            scores.append(pred_model.fit(X[train_idx], Y[train_idx])\
                          .score(X[test_idx], Y[test_idx]))
            print('Accuracy :%f' % scores[i])
        pred_model = get_pred_model() 
        print('training final model')
        pred_model.fit(X, Y)
        
        return pred_model, np.array(scores).mean()

    def get_source_bias_predictions(self, source):
        pred_model, accuracy = self.get_gendered_word_prediction_model(source)
        w2v_model = self.data_manager.get_model_for_source(source)
        # excluded top golden positve words: 
        # words that we did not use for training our classifier for bias
        
        # all words for our source
        source_words = self.top_words_by_source(source, False)
        # positive words that were used for training
        training_positive_words = self.get_common_positive_words()
        training_neutral_words = self.get_common_neutral_words()
        # words for getting the bias list: We exclude those used for training
        # and use all else
        predict_words = list(set(source_words) - set(training_positive_words)
                                               - set(training_neutral_words))
        predict_embeds = [self.normalize(w2v_model[w]) for w in predict_words]
        predict_results = pred_model.predict(predict_embeds)

        return list(zip(predict_words, predict_results)), accuracy
   
    def get_source_bias_measurement(self, source, c=1.0):
        w2v_model = self.data_manager.get_model_for_source(source)
        with open(self.word_pairs_path) as f:
            pair_words = []
            for she_word, he_word in csv.reader(f):
                if she_word in w2v_model and he_word in w2v_model:
                    pair_words.append((she_word, he_word))

        embed_diffs = [] 
        for she_word, he_word in pair_words:
            she_embed = self.normalize(w2v_model[she_word])
            he_embed = self.normalize(w2v_model[he_word])
            embed_diff = she_embed - he_embed
            embed_diffs.append(embed_diff)
        pca = PCA(n_components=len(embed_diffs))
        pca.fit(embed_diffs)
        # pc is g in the paper
        pc = self.normalize(pca.components_[0])
        # neutral words is N in the paper
        word_predictions, accuracy = self.get_source_bias_predictions(source)
        predicted_neutral_words = [word for word, prediction in word_predictions 
                                   if prediction==0]
        neutral_words = (list(self.get_common_neutral_words()) + 
                         predicted_neutral_words)
        tot_direct_bias = 0.0
        # word is w in paper
        for word in neutral_words:
            # w_vec in paper
            word_embedding = self.normalize(w2v_model[word])
            tot_direct_bias += abs(np.dot(pc, word_embedding)) ** c
        
        tot_direct_bias /= len(neutral_words)
        return tot_direct_bias

