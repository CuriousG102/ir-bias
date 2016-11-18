
# coding: utf-8

# In[ ]:

# get some local stuff we'll be needing

from aquaint import AquaintDatasetExtractor
from gigaword import GigawordDatasetExtractor                                                                    
from model_data import DataManager
from nanc_soup import NANCDatasetExtractor                                                                       
from settings import settings
from something import BigIterable
from sources import Source


# In[ ]:

# import some handy dandy viz stuff

import numpy as np
import pandas as pd

# In[ ]:

# ooh and let's throw in some local python libs too 0 0     ___________________
#                                                   _|__   /                  /                                                   _____
#                                                  |___|  <  "whoaaaaaaaaaa" /
#                                                         /_________________/

from collections import Counter
import os
import pickle
import re

class HighPerformanceCounter(Counter):
    '''
    Counter has a key flaw in that its __iadd__ method keeps only 
    keys with positive counts by calling the internal method 
    _keep_positive. _keep_positive loops over
    every single key on every single addition of two counters
    to make sure that no key now has a negative value and must be
    removed. This state of affairs
    can drastically improved by only checking the elements 
    we're actually modifying during an inplace addition.
    Unfortunately this behavior can't be patched 
    on the actual python project because it would break
    back-compatibility. Python unit tests and possibly
    down-stream users rely on all the inplace methods to
    actually remove non-positive keys whether or not
    they're non-positive because of previous operations
    or non-positive because of the immediate effect of other
    '''

    def __iadd__(self, other):
        for elem, count in other.items():
            self[elem] += count
            if not self[elem] > 0:
                del self[elem]
        return self

# In[ ]:

# just your friendly neighborhood data manager

def get_meta_info():
    data_manager = DataManager(settings['local_temp_path'], settings['save_path'])


    # In[ ]:

    # and your friendly neighborhood BigIterable
    all_articles = BigIterable(
        AquaintDatasetExtractor('/newsdata/aquaint_real'),
        GigawordDatasetExtractor('/newsdata/gigaword'),
        NANCDatasetExtractor('/newsdata/nanc/LDC2008T15__North_American_News_Text_Complete_NTC')
    )


    # In[ ]:

    # sample_structure = {
    #     Source.NYT: {
    #         'word_count': HighPerformanceCounter('men'=300),
    #         datetime.datetime(1993, 8, 12): {
    #             'doc_count': 1,
    #             'word_count': 300
    #         }
    #     }
    # }

    META_INFO_PATH = '/newsdata/meta_info.p'

    if os.path.exists(META_INFO_PATH):
        with open(META_INFO_PATH, 'rb') as f:
            meta_info = pickle.load(f)
    else:            
        meta_info = dict()
        for article in all_articles:
            if not article.text:
                continue
            text = article.text
            if article.headline:
                text = ' '.join([article.headline, text])
            text = text.replace('\n', ' ')
            text = re.sub(r'[^a-zA-Z ]', '', text).lower().split()
            source = article.source
            pub_date = article.pub_date
            if source not in meta_info:
                meta_info[source] = dict()
                meta_info[source]['word_count'] = HighPerformanceCounter()
            if pub_date not in meta_info[source]:
                meta_info[source][pub_date] = dict()
                meta_info[source][pub_date]['doc_count'] = 0
                meta_info[source][pub_date]['word_count'] = 0
            meta_info[source]['word_count'] += HighPerformanceCounter(text)
            meta_info[source][pub_date]['word_count'] += len(text)
            meta_info[source][pub_date]['doc_count'] += 1
        with open(META_INFO_PATH, 'wb') as f:
            pickle.dump(meta_info, f)

    return meta_info

