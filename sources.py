from enum import Enum

class Source(Enum):
    AFP = ([], 'Agence France-Presse')
    ALB_TIMES_U = ([], 'Albany Times Union')
    ARZ_REPUB = (['ARIZONA-REPUBLIC', 'AZR'], 'Arizona Republic')
    ATL_CONST = ([], 'Atlanta Constitution')
    BLMBRG = ([], 'Bloomberg Business News')
    BOST = (['BOS'], 'Boston Globe')
    CASPER = ([], 'Casper (Wyo.) Star-Tribune')
    CHI_SUN = ([], 'Chicago Sun-Times')
    COLUMBIA_NEWS = ([], 'Columbia News Service')
    COX = (['COX'], 'Cox News Service')
    FW_STAR_TELEGRAM = ([], 'Fort Worth Star-Telegram')
    HRST = ([], 'Hearst Newspapers') # no unique tag
    CHRON = ([], 'Houston Chronicle') # no unique tag
    INTL_HERALD_TRIB = ([], 'International Herald Tribune')
    KAN_CITY_STAR = (['KAN'], 'Kansas City Star')
    LA_DAILY = (['LADN'], 'Los Angeles Daily News')
    SAN_ANTONIO_EXPRESS = ([], 'San Antonio Express-News') # no unique tag
    SF_CHRON = (['San Francisco Chronicle', 'SFCHRON'], 'San Francisco Chronicle')
    SEATTLE_POST_INTEL = (['SPI'], 'Seattle Post-Intelligencer')
    ST_NEWS_SERVICE = ([], 'State News Service')
    APW = ([], 'Associated Press Worldstream')
    CNA = ([], 'Central News Agency of Taiwan')
    LAT = ([], 'Los Angeles Times')
    LATW = ([], 'LA Times/WaPo Newswire')
    LBPT = ([], 'Long Beach Press-Telegram')
    WAPO = ([], 'Washington Post')
    NYT = (['NYT'], 'New York Times')
    SLATE = ([], 'Slate')
    XIN = ([], 'Xinua News Agency')

    def __init__(self, datelines, name):
        self.datelines = datelines
        self.source_name = name
    
    def __str__(self):
        return self.source_name + ': '.join(self.datelines)
