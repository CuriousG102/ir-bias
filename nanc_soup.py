import datetime
import re

from lxml import etree    
from get_articles import AbstractDatasetExtractor, Article
from sources import Source

from bs4 import BeautifulSoup

class NANCDatasetExtractor(AbstractDatasetExtractor):
    SOURCE_DEFAULTS = {
        'APW': Source.APW,
        'ATL': Source.ATL_CONST,
        'AZR': Source.ARZ_REPUB,
        'BLOOM': Source.BLMBRG,
        'B': Source.BOST,
        'BO': Source.BOST,
        'BOS': Source.BOST,
        'COX': Source.COX,
        'COLUMN': Source.COX,
        'EC': Source.ECO,
        'ECO': Source.ECO,
        'ECONOMI': Source.ECO,
        'ECONOMIST': Source.ECO,
        'HNS': Source.HRST,
        'KAN': Source.KAN_CITY_STAR,
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
        'WSJ': Source.WSJ,
        '1': None,
        'PA': None,
        'TESTER': None,
        'NAT': None
    }

    ENCODING = 'ISO-8859-1'

    def __init__(self, path):
        super().__init__(path)
        self.source_slug_mapping = dict()
        for source in Source:
            for dateline in source.datelines:
                assert(dateline not in self.source_slug_mapping)
                self.source_slug_mapping[dateline] = source

    def get_parse_tree_for_path(self, path):
        try:
            with open(path, 'r', encoding=self.ENCODING) as f:
                return BeautifulSoup(f, 'html.parser')
        except Exception:
            raise Exception('Failed on: ' + path)

    def parse_tree_to_articles(self, tree):
        i = 0
        for doc in tree.find_all('doc'):
            try:
                docid = doc.docid
                if docid:
                    docid = docid.text
                docSource = doc.source
                if docSource:
                    docSource = docSource.text
                if docid is not None and 'nyt' in docid.lower():
                    date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
                    preamble = doc.preamble
                    if preamble is not None:
                        preamble = preamble.text
                        source = preamble.split('\n')[1].split('-')[-1].split(' ')[0]
                        source = self.SOURCE_DEFAULTS[source]
                    else:
                        source = Source.NYT
                    text = doc.text.split('\n\n\n')[1].strip()
                    headline = doc.headline
                    if headline:
                        headline = headline.text.strip()
                elif docid is not None and 'latwp' in docid.lower():
                    date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
                    copyright = doc.cpyright
                    source = Source.LATW
                    if copyright is not None:
                        if 'Newsday' in copyright:
                            source = Source.NEWSDAY
                        elif 'Courant' in copyright:
                            source = Source.HARTC
                        elif 'Sun' in copyright:
                            source = Source.BSUN
                        elif 'Times' in copyright:
                           source = Source.LAT
                        elif 'Post' in copyright:
                           source = Source.WAPO
                    text = ('\n\n\n').join(doc.text.split('\n\n\n')[2:-1]).strip()
                    text = re.sub('&UR; (Begin optional trim)', '', text)
                    text = re.sub('&UR; (End optional trim)', '', text)
                    headline = doc.headline
                    if headline:
                        headline = (' ').join(doc.headline.text.strip().split(' ')[1:-2])
                elif docid is not None and 'reu' in docid.lower():
                    source = Source.REUTE
                    header = doc.header
                    if header is not None:
                        header = header.text.strip()
                        try:
                            date = re.findall(r'\d+', docid)[0][:2] + '-' + re.split(r' ', header)[1]
                            date = re.sub('-', '', date)
                            date = datetime.datetime.strptime(date, '%y%m%d')
                        except Exception:
                            try:
                                date = re.findall(r'\d+', docid)[0][:2] + doc.keyword.strip()
                                date = datetime.datetime.strptime(date, '%y%m%d')
                            except:
                                date = None
                                pass
                    else:
                        date = None
                    text = doc.text.split('\n\n\n')[1].strip()
                    headline = doc.headline
                    if headline:
                        headline = headline.text.strip()
                elif docSource is not None and 'WJ' in docSource:
                    source = Source.WSJ
                    date = doc.dspdate.text.strip()[2:]
                    date = datetime.datetime.strptime(date, '%y%m%d')
                    text = ('\n\n').join(doc.text.split('\n\n')[1:-1]).strip()
                    headline = doc.headline
                    if headline:
                        headline = headline.text.strip()
                else:
                    date = None
                    source = None
                    doc = doc.text
                    headline = doc.headline
                    if headline:
                        headline = headline.text.strip()
                dateline = doc.dateline
                if dateline:
                    dateline = dateline.text
                other = None
                yield Article(headline, date, text, source, other, dateline)
            except Exception:
                raise Exception('Failed on: ' + str(tree.find_all('doc')[i]))
            finally:
                i += 1
