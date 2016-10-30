from aquaint import AquaintDatasetExtractor
import gensim
from gigaword import GigawordDatasetExtractor
import multiprocessing
import os
import re
from something import BigIterable
from sources import Source

def get_source_file_path(temp_path, source):
    file_name = re.sub(r'[^a-zA-Z]', '_', source.source_name) + '.txt'
    return os.path.join(temp_path,  file_name)

def generate_temp_corp_files(temp_path, *extractors):
    all_articles = BigIterable(*extractors)
    source_file_map = dict()
    try:
        for article in all_articles:
            if article.source in source_file_map:
                source_file = source_file_map[article.source]
            else:
                file_path = get_source_file_path(temp_path, article.source)
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

    return source_file_map.keys()

def generate_model_files(save_path, temp_path, sources, num_passes=5):
    for source in sources:
        print('training on %s' % source)
        file_path = get_source_file_path(temp_path, source)
        sentences = gensim.models.word2vec.LineSentence(file_path)
        model = gensim.models.Word2Vec(sentences,
                                       iter=num_passes, 
                                       workers=multiprocessing.cpu_count())
        model_path = get_source_file_path(save_path, source)
        model.save(model_path)

def make_vec_models(save_path, temp_path, *extractors):
    temp_file_sources = generate_temp_corp_files(temp_path, *extractors)
    generate_model_files(save_path, temp_path, temp_file_sources) 

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
    # make_vec_models('/home/paper/extractors/models', 
    #                 '/newsdata/extracted_text',
    #                 GigawordDatasetExtractor('/newsdata/gigaword'),
    #                 AquaintDatasetExtractor('/home/paper/aquaint_real/'))
    judge_model_qualities('/home/paper/extractors/models',
                          '/home/paper/extractors/questions-words.txt')
