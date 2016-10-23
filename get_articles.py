import os
  
from lxml import etree
  
class Article:
    def __init__(self, headline, pub_date, text, source, other, dateline):
        self.headline = headline
        self.pub_date = pub_date
        self.text = text
        self.source = source
        self.other = other
        self.dateline = dateline

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
  
    def __init__(self, path):
        self.path = path
  
    def get_file_paths(self):
        paths = []
        for root, dirs, files in os.walk(self.path):
            for file_ in files:
                paths.append(os.path.join(root, file_))
        return paths
  
    def get_parse_tree_for_path(self, path):
        try:
            parser = etree.XMLParser(recover=True)
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
