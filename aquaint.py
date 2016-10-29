from lxml import etree

import datetime
import re

from get_articles import AbstractDatasetExtractor, Article
from sources import Source

class AquaintDatasetExtractor(AbstractDatasetExtractor):
    SOURCE_DEFAULTS = {
        'AP': Source.APW, 
        'APW': Source.APW,
        'AZR': Source.ARZ_REPUB,
        'BOS': Source.BOST,
        'COX': Source.COX,
        'HNS': Source.HRST,  
        'KAN': Source.KAN_CITY_STAR,
        'LADN': Source.LA_DAILY,
        'LBPT': Source.LBPT, 
        'NYT': Source.NYT,
        'SLATE': Source.SLATE, 
        'SFCHRON': Source.SF_CHRON,
        'SPI': Source.SEATTLE_POST_INTEL,		
        'TEX': Source.FW_STAR_TELEGRAM,
        'XIE': Source.XIN
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
                docno = doc.find('DOCNO')
                if docno is not None:
                    doc_str = re.split(r'(\d+)', ''.join(docno.xpath('.//text()')))
                    date = datetime.datetime.strptime(doc_str[1], '%Y%m%d')
                    for abrv in self.SOURCE_DEFAULTS:
                        if abrv in doc_str[0]:
                            source = self.SOURCE_DEFAULTS[abrv]
                """
                date_str = doc.find('DATE_TIME')
                if date_str is not None:
                    date_str = ''.join(date_str.xpath('.//text()'))
                    date_str = date_str.strip().split(' ')
                date = datetime.datetime.strptime((date_str[0]),'%Y-%m-%d') 		
                """
                other = doc.find('DOCTYPE')
                if other is not None:
                    other = {'type': ''.join(other.xpath('.//text()')).strip()}
                body = doc.find('BODY')
                slug = body.find('SLUG')
                if (slug is not None) and (source == self.SOURCE_DEFAULTS['NYT']):
                    for abrv in self.SOURCE_DEFAULTS:
                        if abrv in (''.join(slug.xpath('.//text()')).split('-')[-1]):
                            source = self.SOURCE_DEFAULTS[abrv]						
                headline = body.find('HEADLINE')
                if headline is not None:
                    headline = ' '.join(headline.xpath('.//text()')) 
                dateline = doc.find('DATELINE')
                text = ' '.join(body.find('TEXT').xpath('.//text()'))
                yield Article(headline, date, text, source, other, dateline) 
            except Exception:
                raise Exception('Failed on: ' + etree.tostring(doc).decode())
