import os

settings = {
    'temp_path': '/newsdata/extracted_text',
    'experiment_temp_path': '/newsdata/extracted_text_temp',
    'local_temp_path': '/home/paper2/ir-bias/extracted_text',
    'experiment_save_path': '/newsdata/experiment_models',
    'golden_model_path': '/newsdata/google_news/GoogleNews-vectors-negative300.bin',
    'positive_words_path': '/newsdata/gender_specific.csv',
    'word_pairs_path': '/home/paper3/ir-bias/word_pairs.csv',
    'new_temp_path': '/newsdata/new_extracted_text',
    'save_path': '/home/paper2/ir-bias/models',
    'questions_path': '/home/paper3/ir-bias/questions-words.txt'
}

for k in settings:
    if 'paper_' + k in os.environ:
        settings[k] = os.environ['paper_' + k] 

