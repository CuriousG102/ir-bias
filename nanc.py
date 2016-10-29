from lxml import etree

import datetime
import re

from get_articles import AbstractDatasetExtractor, Article
from sources import Source

class NANCDatasetExtractor(AbstractDatasetExtractor):
    SOURCE_DEFAULTS = {
        'APW': Source.APW,
        'AZR': Source.ARZ_REPUB,
        'BLOOM': Source.BLMBRG,
        'B': Source.BOST,
        'BO': Source.BOST,
        'BOS': Source.BOST,
        'COX': Source.COX,
        'EC': Source.ECO,
        'ECO': Source.ECO,
        'ECONOMI': Source.ECO,
        'ECONOMIST': Source.ECO,
        'LADN': Source.LA_DAILY,
        'LAT': Source.LAT,
        'NYT': Source.NYT,
        'REUFF': Source.REUTE,
        'REUTE': Source.REUTE,
        'SFCHRON': Source.SF_CHRON,
        'SPI': Source.SEATTLE_POST_INTEL,
        'TE': Source.FW_STAR_TELEGRAM,
        'TEX': Source.FW_STAR_TELEGRAM,
        'WP': Source.WAPO,
        'WSJ': Source.WSJ
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
                docid = doc.find('DOCID')
                docSource = doc.find('SOURCE')
                if docid is not None and 'nyt' in docid.lower():
                    date = datetime.datetime.strptime(re.findAll(r'\d+', docid)[0], '%Y%m%d')
                    preamble = doc.find('PREAMBLE')
                    if preamble is not None:
				        lines = re.split(r'\n', preamble)
                        source = self.SOURCE_DEFAULTS[re.split(r'-', lines[0])[-1].split(' ')[0]]
                        headline = ''
                        date = None
                elif docid is not None and 'latwp' in docid.lower():
                    date = datetime.datetime.strptime(re.findAll(r'\d+', docid)[0], '%Y%m%d')
                    copyright = doc.find('CPYRIGHT').split(' ')[-1]
                    if copyright == 'Newsday':
                        source = sources.NEWSDAY
                    elif copyright == 'Courant'
                        source = sources.HARTC
                    elif copyright == 'Sun':
                        source = sources.BSUN
                    elif copyright == 'Times':
                        source = sources.LAT
                    elif copyright == 'Post':
                        source = sources.WAPO
					headline = doc.find('HEADLINE').split('\n')[0];
                elif docid is not None and 'reu' in docid.lower():
				    headline = doc.find('HEADLINE')
					source = sources.REUTE
					date = re.findall(r'\d+', docid)[0][:2] + '-' + re.strip(' ', doc.find('HEADER').strip())[1]
                    date = datetime.datetime.striptime(date, '%Y%m%d')
                elif docSource is not None and 'WJ' in docSource:
                    source = sources.WSJ
                    headline = doc.find('HL')
                    date = datetime.datetime.strptime(doc.find('DSPDATE').strip(), '%Y%m%d')
				dateline = doc.find('DATELINE')
                other = {'type': doc_attrs['type']}
                text = doc.find('TEXT')
                #doc_attrs = dict(doc.items())
				yield Article(headline, date, text, source, other, dateline) 
            except Exception:
                raise Exception('Failed on: ' + etree.tostring(doc).decode())
