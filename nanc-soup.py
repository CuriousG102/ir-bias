import datetime
import re

from lxml import etree    
from get_articles import AbstractDatasetExtractor, Article
from sources import Source

from bs4 import BeautifulSoup

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

	def __iter__(self):
		for path in self.get_file_paths():
			tree = BeautifulSoup(open(path))
			yield from self.parse_tree_to_articles(tree)

    def parse_tree_to_articles(self, tree):
        for doc in self.__iter__():
            try:
                docid = doc.DOCID
                docSource = doc.SOURCE
                if docid is not None and 'nyt' in docid.lower():
                    date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
                    preamble = doc.PREAMBLE
                    if preamble is not None:
                        lines = re.split(r'\n', preamble)
                        source = self.SOURCE_DEFAULTS[re.split(r'-', lines[0])[-1].split(' ')[0]]
                    else:
                        source = Source.NYT
                    headline = None
                elif docid is not None and 'latwp' in docid.lower():
                    date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
                    copyright = doc.CPYRIGHT
                    if copyright is not None:
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
                    headline = doc.HEADLINE
                elif docid is not None and 'reu' in docid.lower():
                    headline = doc.HEADLINE
                    source = Source.REUTE
                    header = doc.HEADER
                    if header is not None:
                        date = re.findall(r'\d+', docid)[0][:2] + '-' + re.strip(' ', header)[1]
                        date = datetime.datetime.striptime(date, '%y%m%d')
                    else:
                        date = None
                elif docSource is not None and 'WJ' in docSource:
                    source = Source.WSJ
                    headline = doc.HEADLINE
                    date = doc.DSPDATE.strip()
                    date = datetime.datetime.strptime(doc.find(date, '%y%m%d'))
                dateline = doc.DATELINE
                text = doc.TEXT
                other = None
                yield Article(headline, date, text, source, other, dateline) 
            except Exception:
                raise Exception('Failed on: ' + etree.tostring(doc).decode())
