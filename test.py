from aquaint import AquaintDatasetExtractor
from gigaword import GigawordDatasetExtractor
from nanc_soup import NANCDatasetExtractor

def test_extractors(*extractors_and_paths):
    for extractor, path in extractors_and_paths:
        print('Testing %s and sampling 1/10,000 articles' % extractor)
        extractor = extractor(path)
        for i, article in enumerate(extractor):
            if i % 10000 == 0:
                print('Status Report: Article %i processed\n%s' % (i, article))
        print('CONGRATULATIONS! IT WORKS')

if __name__ == '__main__':
    #test_extractors((AquaintDatasetExtractor,'/home/paper/aquaint_real'))
    #test_extractors((GigawordDatasetExtractor,'/newsdata/gigaword/'))
    '''
    test_extractors((NANCDatasetExtractor,'/home/paper/nanc/LDC2008T15__North_American_News_Text_Complete_NTC/latwp'))
    test_extractors((NANCDatasetExtractor,'/home/paper/nanc/LDC2008T15__North_American_News_Text_Complete_NTC/reute'))
    test_extractors((NANCDatasetExtractor,'/home/paper/nanc/LDC2008T15__North_American_News_Text_Complete_NTC/reuff'))
    test_extractors((NANCDatasetExtractor,'/home/paper/nanc/LDC2008T15__North_American_News_Text_Complete_NTC/wsj'))
    test_extractors((NANCDatasetExtractor,'/home/paper/nanc/LDC2008T15__North_American_News_Text_Complete_NTC/nyt'))
    '''
    #test_extractors((NANCDatasetExtractor,'/home/paper/nanc/LDC2008T15__North_American_News_Text_Complete_NTC/latwp/1994/lw940623'))
    #test_extractors((NANCDatasetExtractor,'/home/paper/nanc/LDC2008T15__North_American_News_Text_Complete_NTC'))
    test_extractors((NANCDatasetExtractor,'/home/paper/extractors/nanc-subset'))
