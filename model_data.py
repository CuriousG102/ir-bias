import multiprocessing
import os
import re

import gensim
import pickle

from aquaint import AquaintDatasetExtractor
from gigaword import GigawordDatasetExtractor
from settings import settings
from something import BigIterable
from sources import Source


class DataManager:
    def __init__(self, temp_path, save_path):
        self.temp_path = temp_path
        self.save_path = save_path

    def clear_files(self, path):
        for f in os.listdir(path):
            f_path = os.path.join(path, f)
            if os.path.isfile(f_path):
                os.unlink(f_path)

    def clear_temp_files(self):
        '''
        Deletes temp files. Good to use before regenerating them to
        ensure you are not surprised by a file left behind
        '''
        self.clear_files(self.temp_path)

    def clear_model_files(self):
        '''
        Deletes model files. Good to use before regenerating models 
        to ensure you are not surprised by a model left behind.
        '''
        self.clear_files(self.save_path)

    def clear_model_for_source(self, source):
        model_path = self.get_model_file_path(source)
        if os.path.isfile(model_path):
            os.unlink(model_path)

    def get_source_file_name(self, source):
        return re.sub(r'[^a-zA-Z]', '_', source.source_name) + '.txt'

    def get_file_path(self, path, source):
        file_name = self.get_source_file_name(source)
        return os.path.join(path, file_name)

    def get_text_file_path(self, source):
        return self.get_file_path(self.temp_path, source)

    def get_model_file_path(self, source):
        return self.get_file_path(self.save_path, source)

    def get_source_model_accuracy(self, source):
        model = self.get_model_for_source(source)
        accur = model.accuracy(settings['questions_path'])
        tot_accur = accur[-1]
        assert(tot_accur['section'] == 'total')
        correct = len(tot_accur['correct'])
        incorrect = len(tot_accur['incorrect'])
        if correct + incorrect == 0:
            accur_percentage = 0
        else:
            accur_percentage = correct / (correct + incorrect)
        return accur, accur_percentage

    def save_models_accuracy(self):
        '''
        Saves a dict that gives information about each models' accuracy:
        the key is the source, the value consists of a tuple
        made up of 1) the dict of accuracy results and 2) the total accuracy
        The save file path and file name is hard-coded in the settings folder	
        '''	
        source_acc = {}
        for source in self.get_available_source_models():
            print('Judging accuracy for %s' % source)
            #model = self.get_model_for_source(source)
            accur_dict, accur_percentage = self.get_source_model_accuracy(source)
            source_acc[source] = [accur_dict, accur_percentage]
        with open(settings['accuracy_path'], 'wb') as f:
            pickle.dump(source_acc, f)

    def load_models_accuracy(self):
        '''
        Loads a dict that gives information about each models' accuracy:
        the key is the source, and the value consists of a tuple made up of
        1) the dict of the accuracy results and 2) the total accuracy 
        '''
        with open(settings['accuracy_path'], 'rb') as f:
            return pickle.load(f)

    def get_available_source(self, path):
        name_source_mapping = {}
        for source in Source:
            file_name = self.get_source_file_name(source)
            name_source_mapping[file_name] = source
        return [name_source_mapping[name] 
                for name in os.listdir(path)
                if name in name_source_mapping]

    def get_available_source_models(self):
        '''
        Return list of sources that have 
        word2vec models
        '''
        return self.get_available_source(self.save_path)

    def get_available_source_texts(self):
        '''
        Return list of sources that have
        texts generated for training
        '''
        return self.get_available_source(self.temp_path)
    
    def get_model_for_source(self, source):
        return gensim.models.Word2Vec.load(self.get_model_file_path(source))

    def generate_extractions(self, *extractors):
        '''
        Generates temp files with text extractions for every source
        found in articles from *extractors, iterables which 
        return instances of class get_articles.Article

        Returns set of sources extracted
        '''
        all_articles = BigIterable(*extractors)
        NO_SOURCE_REPORT_RATE = NO_TEXT_REPORT_RATE = 5000
        num_no_text = 0
        source_file_map = dict()
        try:
            for article in all_articles:
                if not article.text:
                    num_no_text += 1
                    if num_no_text % NO_TEXT_REPORT_RATE == 0:
                        print('%i textless articles thrown out' % num_no_text)
                    continue
                if article.source in source_file_map:
                    source_file = source_file_map[article.source]
                else:
                    file_path = self.get_text_file_path(article.source)
                    source_file = open(file_path, 'w')
                    source_file_map[article.source] = source_file
                text = article.text
                if article.headline:
                    text = ' '.join([article.headline, text])
                text = text.replace('\n', ' ')
                text = ' '.join(re.sub(r'[^a-zA-Z ]', '', text).lower().split())
                source_file.write(text)
                source_file.write('\n')
        except:
            for f in source_file_map.values():
                f.close()
            raise Exception('Article text extraction failed. Bailing out.')

        for f in source_file_map.values():
            f.close()

        if num_no_text:
            print('%i textless articles were thrown out' % num_no_text)
        return source_file_map.keys()

    def generate_model_files(self, sources, gensim_args=None):
        for source in sources:
            print('Training on %s' % source)
            model = self.generate_model(source, gensim_args) 
            self.save_model(source, model)    

    def save_model(self, source, model):
        model_path = self.get_model_file_path(source)
        model.save(model_path)

    def generate_model(self, source, gensim_args=None):
        default_kwargs = {
            'iter': 5,
            'workers': multiprocessing.cpu_count()
        }

        if gensim_args:
            assert(type(gensim_args) == dict)
            default_kwargs.update(gensim_args)  

        f_path = self.get_text_file_path(source)
        sentences = gensim.models.word2vec.LineSentence(f_path)
        model = gensim.models.Word2Vec(sentences,
                                       **default_kwargs)
        return model

    def clear_all_and_make_models(self, *extractors, gensim_args=None):
        '''
        Clears the temp directory and the model directory
        and starts from scratch
        '''
        self.clear_temp_files()
        self.clear_model_files()
        sources = self.generate_extractions(*extractors)
        self.generate_model_files(sources, gensim_args)

