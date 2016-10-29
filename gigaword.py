from lxml import etree

import datetime

from get_articles import AbstractDatasetExtractor, Article
from sources import Source

class GigawordDatasetExtractor(AbstractDatasetExtractor):
    SOURCE_DEFAULTS = {
        'AFP': Source.AFP,
        'AP': Source.APW, 
        'APW': Source.APW,
        'CNA': Source.CNA,
        'LTW': Source.LATW,
        'NYT': Source.NYT,
        'XIN': Source.XIN
    }

    def __init__(self, path):
        super().__init__(path)
        self.source_slug_mapping = dict()
        for source in Source:
            for dateline in source.datelines:
                assert(dateline not in self.source_slug_mapping)
                self.source_slug_mapping[dateline] = source
            

    def parse_tree_to_articles(self, tree):
        for doc in tree.getiterator(tag='DOC'):
            try:
                doc_attrs = dict(doc.items())
                headline = doc.find('HEADLINE')
                if headline is not None:
                    headline = ' '.join(headline.xpath('.//text()')) 
                dateline = doc.find('DATELINE')
                if dateline is not None:
                    dateline = ' '.join(dateline.xpath('.//text()')) 
                text = ' '.join(doc.find('TEXT').xpath('.//text()'))
                date_string = doc_attrs['id'].split('_')[-1].split('.')[0]
                date = datetime.datetime.strptime(date_string,
                                                  '%Y%m%d')
                other = {'type': doc_attrs['type']}
                source = self.SOURCE_DEFAULTS[doc_attrs['id'].split('_')[0]]
                if dateline and source == Source.NYT:
                    slug_line = dateline[dateline.rfind('(')+1:dateline.rfind(')')]
                    slug_line = slug_line.split('-')[-1]
                    for slug in self.source_slug_mapping:
                        if slug.upper() == slug_line.upper().strip():
                            source = self.source_slug_mapping[slug]
                yield Article(headline, date, text, source, other, dateline) 
            except Exception:
                raise Exception('Failed on: ' + etree.tostring(doc).decode())
