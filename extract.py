from aquaint import AquaintDatasetExtractor
from gigaword import GigawordDatasetExtractor
from model_data import DataManager
from nanc_soup import NANCDatasetExtractor
from settings import settings 

dm = DataManager(settings['new_temp_path'], settings['save_path'])
dm.generate_extractions(
    AquaintDatasetExtractor('/newsdata/aquaint_real'),
    GigawordDatasetExtractor('/newsdata/gigaword'),
    NANCDatasetExtractor('/newsdata/nanc/LDC2008T15__North_American_News_Text_Complete_NTC')
)

