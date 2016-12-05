import csv
import pickle
from functools import lru_cache

import gensim
from gensim.models import Word2Vec
import numpy as np
from sklearn import svm, model_selection
from sklearn.decomposition import PCA

from model_data import DataManager
from settings import settings

class BiasFinder:
    '''
    Probably not thread safe
    Revision of bias_explorer that no longer uses SVM to obtain list of gender neutral words
    '''
    def __init__(self, train_cutoff=50000,
                 dm_temp_path=settings['temp_path'],
                 dm_save_path=settings['experiment_save_path'],
                 accuracy_cutoff=.4,
                 career_data_path=settings['career_data_path'],
                 golden_model_path=settings['golden_model_path'],
                 positive_words_path=settings['positive_words_path'],
                 word_filter=lambda w: w.isalpha() and len(w) <= 20,
                 word_pairs_path=settings['word_pairs_path'],
                 neutral_words_path=settings['neutral_words_path']):
        self.train_cutoff = train_cutoff
        self.data_manager = DataManager(dm_temp_path, dm_save_path)
        self.accuracy_cutoff = accuracy_cutoff
        self.career_data_path = career_data_path
        self.golden_model_path = golden_model_path
        self.positive_words_path = positive_words_path
        self.word_filter = word_filter
        self.word_pairs_path = word_pairs_path
        self.neutral_words_path = neutral_words_path

    def normalize(self, vector):
        return vector/np.linalg.norm(vector)
 
    @lru_cache()
    def get_eligible_sources(self):
        sources = []
        source_acc = self.data_manager.load_models_accuracy()
        for source in source_acc:
            accur_dict, accur_percentage = source_acc[source]
            #print('Accuracy: %f %s' % (accur_percentage, source))
            if accur_percentage >= self.accuracy_cutoff:
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
        #print('Getting top words for %s' % source)
        source_model = self.data_manager.get_model_for_source(source)
        return self.top_words_by_count(source_model,
                                       use_train_cutoff=use_train_cutoff)

    @lru_cache()
    def top_words_golden(self, use_train_cutoff):
        #print('Getting top words for Golden')
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
        '''retrieves neutral words from specified neutral words path'''
        if self.neutral_words_path: 
            with open(self.neutral_words_path) as f:
                neutral_words = [row[0].strip() for row in csv.reader(f)]
            neutral_words = set(neutral_words)
        else:
            neutral_words = (self.top_words_golden(True) - 
                             set(self.get_positive_words()))

        '''only keeps words that are present across all sources and in the
               top words of all sources'''
        for source in self.get_eligible_sources():
            neutral_words &= set(self.top_words_by_source(source, True)) 
        assert(len(neutral_words) > 0)
        return neutral_words

    def get_principal_components(self, w2v_model):
        print('fetching principal components')
        top_words = set(self.top_words_by_count(w2v_model, True))
        total_pairs = 0
        pairs_not_found = 0
        pairs_not_in_top_words = 0
        with open(self.word_pairs_path) as f:
            pair_words = []
            for she_word, he_word in csv.reader(f):
                total_pairs += 1
                if she_word in w2v_model and he_word in w2v_model:
                    if she_word in top_words and he_word in top_words:
                        pair_words.append((she_word, he_word))
                    else: 
                        pairs_not_in_top_words += 1 
                else:
                    pairs_not_found += 1
        print('--PCA stats--')
        print('Pairs used: %i' % (total_pairs - pairs_not_found 
                                              - pairs_not_in_top_words))
        print('Pairs not in model: %i' % pairs_not_found)
        print('Pairs not in top words: %i' % pairs_not_in_top_words)

        embed_diffs = [] 
        for she_word, he_word in pair_words:
            she_embed = self.normalize(w2v_model[she_word])
            he_embed = self.normalize(w2v_model[he_word])
            embed_diff = she_embed - he_embed
            embed_diffs.append(self.normalize(embed_diff))
        pca = PCA(n_components=len(embed_diffs))
        pca.fit(embed_diffs)
        # pc is g in the paper
        return pca 

    def get_source_bias_measurement(self, source, c=1.0):
        w2v_model = self.data_manager.get_model_for_source(source)
        pca = self.get_principal_components(w2v_model)
        pc = self.normalize(pca.components_[0])
        # neutral words is N in the paper
        neutral_words = self.get_common_neutral_words()
        tot_direct_bias = 0.0
        # word is w in paper
        for word in neutral_words:
            # w_vec in paper
            word_embedding = self.normalize(w2v_model[word])
            tot_direct_bias += abs(np.dot(pc, word_embedding)) ** c
        
        tot_direct_bias /= len(neutral_words)
        print(source)
        print(tot_direct_bias)
        return tot_direct_bias

    def calculate_wefat(self):
        print('calculating wefat')

        w2v_model = Word2Vec.load_word2vec_format(self.golden_model_path,
                                                binary=True)
        top_words = self.top_words_by_count(w2v_model, 
                                            use_train_cutoff=True)

#        print(top_words)

        with open(self.word_pairs_path) as f:
            pair_words = []
#            print(list(csv.reader(f)))
            for she_word, he_word in csv.reader(f):
                if she_word in w2v_model and he_word in w2v_model:
                    if she_word in top_words and he_word in top_words:
                        pair_words.append((she_word, he_word))
        print(pair_words)

        with open(self.career_data_path) as f:
            career_data = []
            for title, abbrev, percentage in csv.reader(f, delimiter="\t"):
                if abbrev in w2v_model and top_words:
                    career_data.append((title, abbrev, percentage))
        print(career_data)

        results = {}
        for triple in career_data:
            cos_A = []
            cos_B = []

            w = triple[1]
            for pair in pair_words:
                a = pair[0]
                b = pair[1]
                cos_A.append(w2v_model.similarity(w, a))
                cos_B.append(w2v_model.similarity(w, b))

            mean_cos_A = np.mean(cos_A)
            mean_cos_B = np.mean(cos_B)
            
            cos_total = cos_A + cos_B
            sd = np.std(cos_total)

            results[w] = (triple[2], (mean_cos_A - mean_cos_B) / sd)
            print(w, results[w])

        return results
