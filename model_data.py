from aquaint import AquaintDatasetExtractor
import gensim
from gigaword import GigawordDatasetExtractor
import multiprocessing
import os
import re
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

    def get_file_path(self, path, source):
        file_name = re.sub(r'[^a-zA-Z]', '_', source.source_name) + '.txt'
        return os.path.join(path,  file_name)

    def get_text_file_path(self, source):
        return self.get_file_path(self.temp_path, source)

    def get_model_file_path(self, source):
        return self.get_file_path(self.save_path, source)

    def generate_extractions(self, *extractors):
        '''
        Generates temp files with text extractions for every source
        found in articles from *extractors, iterables which 
        return instances of class get_articles.Article

        Returns set of sources extracted
        '''
        all_articles = BigIterable(*extractors)
        source_file_map = dict()
        try:
            for article in all_articles:
                if article.source in source_file_map:
                    source_file = source_file_map[article.source]
                else:
                    file_path = self.get_text_file_path(source)
                    source_file = open(file_path, 'w')
                    soruce_file_map[article.source] = source_file
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

        return source_file_map.keys()

    def generate_model_files(self, sources, gensim_args=None):
        default_kwargs = {
            'iter': 5,
            'workers': multiprocessing.cpu_count()
        }

        if gensim_args:
            assert(type(gensime_args) == dict)
            default_kwargs.update(gensim_args)

        for source in sources:
            print('Training on %s' % source)
            f_path = self.get_text_file_path(source)
            sentences = gensim.models.word2vec.LineSentence(f_path)
            model = gensim.models.Word2Vec(sentences,
                                           **default_kwargs)
            model_path = self.get_model_file_path(source)
            model.save(model_path)

    def clear_all_and_make_models(self, *extractors, gensim_args=None):
        '''
        Clears the temp directory and the model directory
        and starts from scratch
        '''
        self.clear_temp_files()
        self.clear_model_files()
        sources = self.generate_extractions(*extractors)
        self.generate_model_files(sources)

def judge_model_qualities(save_path, questions_path):
    all_accur_data = dict()
    for root, dirs, files in os.walk(save_path):
        for file_ in files:
            f_split = file_.split('.')
            if len(f_split) > 1 and f_split[-1] == 'txt':
                print('Judging Quality: %s' % file_)
                model = gensim.models.Word2Vec.load(os.path.join(root, file_))
                accur = model.accuracy(questions_path)
                all_accur_data[file_] = accur
                tot_accur = accur[-1]
                assert(tot_accur['section'] == 'total')
                correct = len(tot_accur['correct'])
                incorrect = len(tot_accur['incorrect'])
                print('Total Accuracy: %f' % (correct / (correct + incorrect)))
    return all_accur_data
    
if __name__ == '__main__':
    judge_model_qualities('/home/paper/extractors/models',
                          '/home/paper/extractors/questions-words.txt')