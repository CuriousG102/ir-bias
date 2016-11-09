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
        'CLINIC': Source.NYT,
        'COX': Source.COX,
        'COLUMN': Source.COX,
        'EC': Source.ECO,
        'ECO': Source.ECO,
        'ECONOMI': Source.ECO,
        'ECONOMIST': Source.ECO,
        'HNS': Source.HRST,
        'INDEPENDENT': Source.IND,
        'KAN': Source.KAN_CITY_STAR,
        'LADN': Source.LA_DAILY,
        'LAT': Source.LAT,
        'NYT': Source.NYT,
        'REUFF': Source.REUTE,
        'REUTE': Source.REUTE,
        'SF': Source.SF_CHRON,
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

    def get_parse_tree_for_path(self, path):
        try:
            with open(path, 'r', encoding=self.ENCODING) as f:
                return BeautifulSoup(f, 'html.parser')
        except Exception:
            raise Exception('Failed on: ' + path)

    def parse_latwp(self, doc):
        TEXT_AND_SOURCE = [('Newsday', Source.NEWSDAY),
                           ('Courant', Source.HARTC),
                           ('Sun', Source.BSUN),
                           ('Times', Source.LAT),
                           ('Post', Source.WAPO),]
        docid = doc.docid.text

        headline = (' ').join(doc.headline.text.strip().split(' ')[1:-2]) if doc.headline else None
        dateline = doc.dateline.text if doc.dateline else None
        date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
        source = Source.LATW
        text = doc.find('text').text.strip() if doc.find('text') else None
        other = None
 
        copyright = doc.cpyright.text if doc.cpyright else None
        if copyright:
            for txt, src in TEXT_AND_SOURCE:
                if txt.lower() in copyright.lower():
                    source = src

        return Article(headline, date, text, source, other, dateline)
    
    def parse_nyt(self, doc):
        TEXT_AND_SOURCE = [('Los Angeles Daily News', Source.LA_DAILY), 
                           ('N.Y. Times', Source.NYT),
                           ('Cox News', Source.COX),
                           ('Economist', Source.ECO),]
        docid = doc.docid.text

        headline = doc.headline.text.strip() if doc.headline else None
        dateline = doc.dateline.text if doc.dateline else None
        date = datetime.datetime.strptime(re.findall(r'\d+', docid)[0], '%y%m%d')
        text = doc.find('text').text.strip() if doc.find('text') else None
        source = Source.NYT
        other = None

        preamble = doc.preamble.text if doc.preamble else None
        if preamble:
            src = preamble.split('\n')[1].split('-')[-1].split(' ')[0]
            if src in self.SOURCE_DEFAULTS:
                source = self.SOURCE_DEFAULTS[src]
            else:
                for txt, src in TEXT_AND_SOURCE:
                    if txt.lower() in preamble.lower():
                        source = src
        
        return Article(headline, date, text, source, other, dateline)

    def parse_reu(self, doc):
        docid = doc.docid

        headline = doc.headline.text.strip() if doc.headline else None
        dateline = doc.dateline.text if doc.dateline else None
        source = Source.REUTE
        date = None
        text = doc.find('text').text.strip() if doc.find('text') else Nonei
        other = None

        header = doc.header.text.strip() if doc.header else None
        if header:
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
                
        return Article(headline, date, text, source, other, dateline)

    def parse_wj(self, doc):
        headline = doc.hl.text.strip() if doc.hl else None
        dateline = doc.dateline.text if doc.dateline else None
        source = Source.WSJ
        date = doc.dspdate
        text = doc.find('text').text.strip() if doc.find('text') else None
        other = None

        if not date:
            date = doc.msgdate
        
        if date:
            date = date.text.strip()[2:]
            date = datetime.datetime.strptime(date, '%y%m%d')
        else:
            date = None

        return Article(headline, date, text, source, other, dateline)

    def parse_tree_to_articles(self, tree):
        i = 0
        for doc in tree.find_all('doc'):
            try:
                docid = doc.docid.text if doc.docid else None
                docsource = doc.source.text if doc.source else None
                prdsrvid = doc.prdsrvid.text if doc.prdsrvid else None
                
                if docid and 'nyt' in docid.lower():
                    yield self.parse_nyt(doc)
                elif docid and 'latwp' in docid.lower():
                    yield self.parse_latwp(doc)            
                elif docid and 'reu' in docid.lower():
                    yield self.parse_reu(doc) 
                elif (docsource  and 'WJ' in docsource) or (prdsrvid and 'WJ' in prdsrvid or 'WA' in prdsrvid):
                    yield self.parse_wj(doc) 
                else:
                    date = None
                    source = None
                    headline = doc.headline.text.strip() if doc.headline else None
                    dateline = doc.dateline.text if doc.dateline else None
                    other = None
                    text = doc.find('text').text.strip() if doc.find('text') else None
                    yield Article(headline, date, text, source, other, dateline)
            except Exception:
                raise Exception('Failed on: ' + str(tree.find_all('doc')[i]))
            finally:
                i += 1
