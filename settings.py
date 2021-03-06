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
    'questions_path': '/home/paper3/ir-bias/questions-words.txt',
    'accuracy_path': '/newsdata/models_temp_data/models_accuracy.pkl',
    'neutral_words_path': '/newsdata/crawford_gend_neutral.csv',
    'career_data_path': '/home/paper3/ir-bias/career_data.tsv'
}

for k in settings:
    if 'paper_' + k in os.environ:
        settings[k] = os.environ['paper_' + k] 

