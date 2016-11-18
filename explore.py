import itertools

from settings import settings
from sources import Source
from model_data import DataManager

def judge_model_quality(model):
    '''
    Judge model quality
    '''
    accur = model.accuracy(settings['questions_path'])
    tot_accur = accur[-1]
    assert(tot_accur['section'] == 'total')
    correct = len(tot_accur['correct'])
    incorrect = len(tot_accur['incorrect'])
    if correct + incorrect == 0:
        accur_percentage = 0
    else:
        accur_percentage = correct / (correct + incorrect)
    return accur, accur_percentage

def search_hyper_parameters(gensim_args, skip_sources=None):
    '''
    Searches the hyperparameter space for each available source.
    Pass in a dict with an iterable for each kwarg you want to search
    over with gensim Word2Vec's kwargs. The function will then try
    all possible combinations of all possible hyperparameters and
    will retain fhe model for each source that has the highest accuracy
    rating as judged by the method in judge_model_quality
    '''
    gensim_args = {k: list(v) for k, v in gensim_args.items()}
    data_manager = DataManager(settings['local_temp_path'],
                               settings['experiment_save_path'])
    best_parameters = dict()

    possible_options = []
    for kwarg, values in gensim_args.items():
        arg_options = [(kwarg, value) for value in values] 
        possible_options.append(arg_options)

    num_combos = 1
    for option_set in possible_options:
        num_combos *= len(option_set)
    print('Number option combinations: %i' % num_combos)

    for source in data_manager.get_available_source_texts():
        if skip_sources and source in skip_sources:
            print('Skipping: %s' % source)
            continue
        data_manager.clear_model_for_source(source)
        print('Searching Hyperparameter Space: %s' % source) 
        best_accuracy = -1

        for option_choices in itertools.product(*possible_options):
            option_choices = dict(option_choices)
            print('Training for options: %s' % option_choices)
            model = data_manager.generate_model(source, 
                                                gensim_args=option_choices)
            _, accuracy = judge_model_quality(model)
            print('Training Accuracy: %f' % accuracy)
            if accuracy > best_accuracy:
                best_accuracy = accuracy
                data_manager.clear_model_for_source(source)
                data_manager.save_model(source, model)
                best_parameters[source] = option_choices

    print('Best parameters were: %s' % best_parameters)
    return best_parameters

if __name__ == '__main__':
    search_hyper_parameters({
        'size': [300],
        'window': [3, 5, 7],
        'sample': [1e-3, 1e-5],
        'hs': [0, 1],
    },
    skip_sources=set([
        Source.ARZ_REPUB,
        Source.APW,
        Source.HRST,
        Source.BLMBRG,
        Source.WSJ,
        Source.COX,
        Source.LATW,
        Source.XIN,
        Source.WAPO,
		Source.ATL_CONST,
		Source.LBPT,
		Source.BSUN,
		Source.AFP,
		Source.CNA,
		Source.BOST,
		Source.NYT,
		Source.HARTC,
		Source.AZG,
		Source.SEATTLE_POST_INTEL,
		Source.LA_DAILY,
		Source.SF_CHRON,
		Source.NEWSDAY,
		Source.ECO,
		Source.SLATE,
		Source.LAT,
		Source.IND,
    ]))

