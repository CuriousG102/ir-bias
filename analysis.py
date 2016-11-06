import gensim
import numpy

from sources import Source
from model_data import DataManager

TEMP = '/newsdata/models_test'
SAVE = '/home/paper/extractors/models/'

'''playing with what  calculations of word embeddings will look like'''

def analysis():
    data_manager = DataManager(TEMP, SAVE)
    model = data_manager.get_model_for_source(getSource('SLATE')) 
    print(numpy.linalg.norm(normalize(model['woman'])))

def normalize(word):
    mag = numpy.linalg.norm(word)
    return word/mag

def getSource(abrv):
    '''hard coded for now...'''
    return Source.SLATE

analysis()
