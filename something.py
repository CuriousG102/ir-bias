from aquaint import AquaintDatasetExtractor
from get_articles import Article
from gigaword import GigawordDatasetExtractor

class BigIterable:
    def __init__(self, *iters):
        self.iterables = iters
    
    def __iter__(self):
        source_dates = dict()
        num_not_enough_info = 0
        num_unique_articles = 0
        num_dups = 0
        for iterable in self.iterables:
            specific_source_dates = dict()
            for article in iterable:
                if article.pub_date and article.source:
                    if article.source in source_dates\
                    and article.pub_date in source_dates[article.source]:
                        num_dups += 1
                        if num_dups % 10000 == 0:
                            print('On duplicate %i' % num_dups)
                        continue

                    if article.source in specific_source_dates:
                        specific_source_dates[article.source].add(article.pub_date)
                    else:
                        specific_source_dates[article.source] = set([article.pub_date])
                else:
                    num_not_enough_info += 1
                    if num_not_enough_info % 10000 == 0:
                        print('Threw out article %i')
                    continue

                num_unique_articles += 1
                if num_unique_articles % 10000 == 0:
                    print('On article %i' % num_unique_articles)
                yield article
            
            for k, v in specific_source_dates.items():
                if k in source_dates:
                    source_dates[k].union(v)
                else:
                    source_dates[k] = v
            
            print('done with one of the iterables')

        print('Processed %i articles, %i duplicates' % (num_unique_articles, num_dups))
        if num_not_enough_info:
            print('WARNING: Threw out %i articles due to lack of source and/or date' % num_not_enough_info)

if __name__ == '__main__':
    big_iter = BigIterable(
        AquaintDatasetExtractor('/home/paper/aquaint_real'),
        GigawordDatasetExtractor('/newsdata/gigaword')
    )

    counts = dict()
    word_counts = dict()
    for article in big_iter:
        if article.source in counts:
            counts[article.source] += 1
            word_counts[article.source] += article.text.count(' ') + 1
            if article.headline:
                word_counts[article.source] += article.headline.count(' ') + 1
        else:
            counts[article.source] = 1
            word_counts[article.source] = article.text.count(' ') + 1
            if article.headline:
                word_counts[article.source] += article.headline.count(' ') + 1

    print('Num articles each source')
    print(counts)
    print('Num words each source')
    print(word_counts)    

