from aquaint import AquaintDatasetExtractor
from gigaword import GigawordDatasetExtractor
from nanc import NANCDatasetExtractor

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
    test_extractors((NANCDatasetExtractor,'/home/paper/nanc/'))
