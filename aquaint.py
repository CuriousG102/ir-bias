from lxml import etree

import datetime

from get_articles import AbstractDatasetExtractor, Article
from sources import Source

class AquaintDatasetExtractor(AbstractDatasetExtractor):
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
                datetime = doc.find('DATE_TIME')
                if datetime is not None:
                    datetime = ' '.join(datetime.xpath('.//text()')) 
                body = doc.find('BODY')
                doc_attrs = dict(doc.items())
                headline = body.find('HEADLINE')
                if headline is not None:
                    headline = ' '.join(headline.xpath('.//text()')) 
                text = ' '.join(body.find('TEXT').xpath('.//text()'))
                date = datetime 		#TODO
                other = "test"    		#TODO
                source = "test"			#TODO
                dateline = "test"		#TODO
                """	
		        date_string = doc_attrs['id'].split('_')[-1].split('.')[0]
                date = datetime.datetime.strptime(date_string,
                                                  '%Y%m%d')
                other = {'type': doc_attrs['type']}
                source = self.SOURCE_DEFAULTS[doc_attrs['id'].split('_')[0]]
                if dateline:
                    for slug in self.source_slug_mapping:
                        if slug in dateline:
                            source = self.source_slug_mapping[slug]
                """
                yield Article(headline, date, text, source, other, dateline) 
            except Exception:
                raise Exception('Failed on: ' + etree.tostring(doc).decode())
