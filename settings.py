import os

settings = {
    'temp_path': '/newsdata/extracted_text',
    'save_path': '/home/paper/extractors/models',
    'experiment_save_path': '/home/paper/extractors/experiment_models',
    'questions_path': '/home/paper/extractors/questions-words.txt'
}

for k in settings:
    if 'paper_' + k in os.environ:
        settings[k] = os.environ['paper_' + k] 

