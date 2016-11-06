import os

settings = {
    'temp_path': '/newsdata/extracted_text',
    'save_path': '/home/paper/extractors/models',
    'experiment_save_path': '/home/paper/extractors/experiment_models',
    'questions_path': '/home/paper/extractors/questions-words.txt',
    'golden_model_path': '/newsdata/google_news/GoogleNews-vectors-negative300.bin',
    'positive_words_path': '/newsdata/gender_specific.csv',
    'word_pairs_path': '/home/paper/extractors/word_pairs.csv'
}

for k in settings:
    if 'paper_' + k in os.environ:
        settings[k] = os.environ['paper_' + k] 

