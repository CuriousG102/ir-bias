import os
  
from lxml import etree
  
class Article:
    def __init__(self, headline, pub_date, text, source, other, dateline):
        self.headline = headline # string or None
        self.pub_date = pub_date # datetime
        self.text = text         # should never be None, always string
        self.source = source     # Source enumeration
        self.other = other       # dictionary with arbitrary keys and values
        self.dateline = dateline # string or None

    def __str__(self):
        return ('Article:\n'
                'Headline: {s.headline}\n'
                'Publication Date: {s.pub_date}\n'
                'Source: {s.source}\n'
                'Dateline: {s.dateline}\n'
                'Other: {s.other}\n'
                'Text:\n'
                '{s.text}\n').format(s=self)


class AbstractDatasetExtractor:
    NAME = 'abstract extractor'
    IGNORED_EXTENSIONS = ['1st', 'swp', 'tar', 'txt', 'DS_Store', 'rst']
    ENCODING = None
  
    def __init__(self, path):
        self.path = path
  
    def get_file_paths(self):
        paths = []
        for root, dirs, files in os.walk(self.path):
            for file_ in files:
                f_split = file_.split('.')
                if len(f_split) > 1 and f_split[-1] in self.IGNORED_EXTENSIONS:
                    continue
                paths.append(os.path.join(root, file_))
        return paths
  
    def get_parse_tree_for_path(self, path):
        try:
            parser = etree.XMLParser(recover=True)
            if self.ENCODING:
                with open(path, 'r', encoding=self.ENCODING) as f:
                    return etree.fromstring('<root>'+f.read()+'</root>', parser)
            else:
                with open(path, 'r') as f:
                    return etree.fromstring('<root>'+f.read()+'</root>', parser) 
        except Exception:
            raise Exception('Failed on: ' + path)
  
    def parse_tree_to_articles(self, tree):
        raise NotImplemented()
  
    def __iter__(self):
        for path in self.get_file_paths():
            tree = self.get_parse_tree_for_path(path)
            yield from self.parse_tree_to_articles(tree)

