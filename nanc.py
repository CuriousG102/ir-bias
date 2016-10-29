import datetime
import re

from lxml import etree    
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

    ENCODING = 'ISO-8859-1'

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
                if docid is not None:
                    docid = ' '.join(docid.xpath('.//text()')) 
                docSource = doc.find('SOURCE')
                if docSource is not None:
                    docSource = ' '.join(docSource.xpath('.//text()'))
                if docid is not None and 'nyt' in docid.lower():
                    date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
                    preamble = doc.find('PREAMBLE')
                    if preamble is not None:
                        preamble = ' '.join(preamble.xpath('.//text()'))
                        lines = re.split(r'\n', preamble)
                        source = self.SOURCE_DEFAULTS[re.split(r'-', lines[0])[-1].split(' ')[0]]
                        headline = None
                elif docid is not None and 'latwp' in docid.lower():
                    date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
                    copyright = doc.find('CPYRIGHT')
                    if copyright is not None:
                        copyright = ' '.join(copyright.xpath('.//text()')).split(' ')[-1]
                        if copyright == 'Newsday':
                            source = Source.NEWSDAY
                        elif copyright == 'Courant':
                            source = Source.HARTC
                        elif copyright == 'Sun':
                            source = Source.BSUN
                        elif copyright == 'Times':
                           source = Source.LAT
                        elif copyright == 'Post':
                           source = Source.WAPO
                    else:
                        source = Source.LATW
                    headline = doc.find('HEADLINE') 
                    if headline is not None:
                        headline = ' '.join(headline.xpath('.//text()')).split('\n')[0]
                elif docid is not None and 'reu' in docid.lower():
                    headline = doc.find('HEADLINE')
                    if headline is not None:
                        headline = ' '.join(headline.xpath('.//text()'))
                    source = sources.REUTE
                    header = ' '.join(doc.find('HEADER').xpath('.//text()')).strip()
                    date = re.findall(r'\d+', docid)[0][:2] + '-' + re.strip(' ', header)[1]
                    date = datetime.datetime.striptime(date, '%y%m%d')
                elif docSource is not None and 'WJ' in docSource:
                    source = sources.WSJ
                    headline = doc.find('HEADLINE')
                    if headline is not None:
                        headline = ' '.join(headline.xpath('.//text()'))
                    date = ' '.join(doc.find('DSPDATE').xpath('.//text()')).strip()
                    date = datetime.datetime.strptime(doc.find(date, '%y%m%d'))
                dateline = doc.find('DATELINE')
                if dateline is not None:
                    dateline = ' '.join(dateline.xpath('.//text()'))
                text = doc.find('TEXT')
				other = None
                yield Article(headline, date, text, source, other, dateline) 
            except Exception:
                raise Exception('Failed on: ' + etree.tostring(doc).decode())
