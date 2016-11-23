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
                 golden_model_path=settings['golden_model_path'],
                 positive_words_path=settings['positive_words_path'],
                 word_filter=lambda w: w.isalpha() and len(w) <= 20,
                 word_pairs_path=settings['word_pairs_path']):
        self.train_cutoff = train_cutoff
        self.data_manager = DataManager(dm_temp_path, dm_save_path)
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
        '''
        currently, you need to either comment out the Google News or Crawford 
        code snippet so that only one set of neutral words is used for the 
        direct bias formula
        '''


        '''retrieves neutral words from Google News
        top_golden_words = self.top_words_golden(True)
        neutral_words = top_golden_words - set(self.get_common_positive_words())
        '''

        '''retrieves neutral words from Crawford'''
        with open('/newsdata/crawford_gend_neutral.csv') as f:
            neutral_words = [row[0].strip() for row in csv.reader(f)]
        neutral_words = set(neutral_words)
     
       
        '''only keeps words that are present across all sources'''
        for source in self.get_eligible_sources():
            neutral_words &= set(self.top_words_by_source(source, False))

        return neutral_words

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
        neutral_words = (list(self.get_common_neutral_words()))
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

