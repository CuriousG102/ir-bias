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

def make_vec_models(save_path, temp_path, *extractors):
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

    NUM_PASSES = 5

    for source in source_file_map.keys():
        print('training on %s' % source)
        file_path = get_source_file_path(temp_path, source)
        sentences = gensim.models.word2vec.LineSentence(file_path)
        model = gensim.models.Word2Vec(sentences,
                                       iter=NUM_PASSES, 
                                       workers=multiprocessing.cpu_count())
        model.save(os.path.join(save_path, source.name))

if __name__ == '__main__':
    make_vec_models('/home/paper/extractors/models', 
                    '/newsdata/extracted_text',
                   GigawordDatasetExtractor('/newsdata/gigaword'),
                   AquaintDatasetExtractor('/home/paper/aquaint_real/'))

