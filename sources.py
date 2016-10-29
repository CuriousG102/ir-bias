from enum import Enum

class Source(Enum):
    AFP = ([], 'Agence France-Presse')
    APW = ([], 'Associated Press Worldstream')
    ALB_TIMES_U = ([], 'Albany Times Union')
    ARZ_REPUB = (['ARIZONA-REPUBLIC', 'AZR'], 'Arizona Republic')
    ATL_CONST = ([], 'Atlanta Constitution')
    BLMBRG = (['BLOOM'], 'Bloomberg Business News')
    BOST = (['B', 'BO', 'BOS'], 'Boston Globe')
    CASPER = ([], 'Casper (Wyo.) Star-Tribune')
    CHRON = ([], 'Houston Chronicle') # no unique tag
    CHI_SUN = ([], 'Chicago Sun-Times')
    COLUMBIA_NEWS = ([], 'Columbia News Service')
    COX = (['COX'], 'Cox News Service')
    CNA = ([], 'Central News Agency of Taiwan')
    ECO = (['EC', 'ECO', 'ECONOMI', 'ECONOMIST'], 'Economist')
    FW_STAR_TELEGRAM = (['TE', 'TEX'], 'Fort Worth Star-Telegram')
    HRST = (['HNS'], 'Hearst Newspapers') # no unique tag
    INTL_HERALD_TRIB = ([], 'International Herald Tribune')
    KAN_CITY_STAR = (['KAN'], 'Kansas City Star')
    LA_DAILY = (['LADN'], 'Los Angeles Daily News')
    LAT = (['LAT'], 'Los Angeles Times')
    LATW = ([], 'LA Times/WaPo Newswire')
    LBPT = ([], 'Long Beach Press-Telegram')
    NYT = (['NYT'], 'New York Times')
    REUTE = (['REUFF', 'REUTE'], 'Reuters')
    SAN_ANTONIO_EXPRESS = ([], 'San Antonio Express-News') # no unique tag
    SEATTLE_POST_INTEL = (['SPI'], 'Seattle Post-Intelligencer')
    SF_CHRON = (['San Francisco Chronicle', 'SFCHRON'], 'San Francisco Chronicle')
    SFE = ([], 'San Francisco Examiner') # no unique tag
    SLATE = ([], 'Slate')
    ST_NEWS_SERVICE = ([], 'State News Service')
    WAPO = ([], 'Washington Post')
    WSJ = ([], 'Wall-Street Journal')
    XIN = ([], 'Xinua News Agency')

    def __init__(self, datelines, name):
        self.datelines = datelines
        self.source_name = name
    
    def __str__(self):
        return self.source_name + ': '.join(self.datelines)
