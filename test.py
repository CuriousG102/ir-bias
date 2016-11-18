from aquaint import AquaintDatasetExtractor
from gigaword import GigawordDatasetExtractor
from nanc_soup import NANCDatasetExtractor

def test_extractors(*extractors_and_paths):
    num_no_src = 0
    num_no_date = 0
    num_neither = 0
    sources = {}
    for extractor, path in extractors_and_paths:
        print('Testing %s and sampling 1/10,000 articles' % extractor)
        extractor = extractor(path)
        for i, article in enumerate(extractor):
            if article.source:
                if article.source in sources:
                    sources[article.source] = sources[article.source] + 1
                else:
                    sources[article.source] = 1
            
            if not article.source and article.pub_date:
                num_no_src += 1
            elif not article.pub_date and article.source:
                num_no_date += 1
            elif not article.pub_date and not article.source:
                num_neither = 0
            if i % 10000 == 0:
                print('Status Report: Article %i processed\n%s' % (i, article))
        print('CONGRATULATIONS! IT WORKS')
        print('num_no_src:\t' + str(num_no_src))
        print('num_no_date:\t' + str(num_no_date))
        print('num_neither:\t' + str(num_neither))
        print('total bad:\t' + str(num_no_src + num_no_date + num_neither))
        print('total num:\t' + str(i + 1))
        print('\n')
        print('source stats:')
        for source, count in sources.items():
            print((source, count))

if __name__ == '__main__':
    #test_extractors((AquaintDatasetExtractor,'/home/paper/aquaint_real/'))
    #test_extractors((GigawordDatasetExtractor,'/newsdata/gigaword/'))
    test_extractors((NANCDatasetExtractor,'/newsdata/nanc/LDC2008T15__North_American_News_Text_Complete_NTC/'))
