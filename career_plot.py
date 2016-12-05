from career_analysis_simple import CareerAnalysis
from career_analysis import BiasFinder

# import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from settings import settings

def plot_career_stats_simple(career_data_path='./career_data.tsv',
                             word_pairs_path='./word_pairs.csv'):
    career_stats = CareerAnalysis(career_data_path=career_data_path,
                                  word_pairs_path=word_pairs_path)
    data = career_stats.calculate_wefat()

def plot_career_stats(career_data_path='./career_stats.tsv',
                      word_pairs_path='./word_pairs.csv'):
    bias_finder = BiasFinder(career_data_path='./career_data.tsv',
                             word_pairs_path='./word_pairs.csv')
    data = bias_finder.calculate_wefat()

# plot_career_stats_simple()
plot_career_stats()
