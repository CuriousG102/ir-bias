from aquaint import AquaintDatasetExtractor
import gensim
from gigaword import GigawordDatasetExtractor
import multiprocessing
import os
import re
from something import BigIterable
from sources import Source

def get_text_of_source_articles(all_articles, source):
    for article in all_articles:
        if article.source == source:
            text = article.text
            if article.headline:
                text = ' '.join([article.headline, article.text])   
            text = text.replace('\n', ' ')
            text = re.sub(r'[^a-zA-Z ]', '', text).lower().split()
            yield text

def make_vec_models(save_path, *extractors_and_paths):
    all_articles = BigIterable(*[extractor(path) for extractor, path in extractors_and_paths])
    NUM_PASSES = 5
    for source in Source:
        print('Training for %s' % source)
        model = gensim.models.Word2Vec(iter=NUM_PASSES, 
                                       workers=multiprocessing.cpu_count())
        source_articles = get_text_of_source_articles(all_articles, source)
        model.build_vocab(source_articles)
        print('Built vocab')
        for i in range(NUM_PASSES):
            source_articles = get_text_of_source_articles(all_articles, source)
            model.train(source_articles)
            print('Pass %i complete' % i + 1)
        model.save(os.path.join(save_path, source.name))

if __name__ == '__main__':
    make_vec_models('/home/paper/extractors/models', 
                   (GigawordDatasetExtractor, '/newsdata/gigaword'),
                   (AquaintDatasetExtractor, '/home/paper/aquaint_real/'))

