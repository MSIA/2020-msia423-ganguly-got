import pandas as pd
import pickle
import os
import logging


logger = logging.getLogger(__name__)


def input_var_df(var):
    """
    Creating dataFrame for given input feature, with 2 columns,
    1. key = 1 for all (to be used to compute cartesian product of all feature categories)
    2. var = 0, 1

    Arguments:
        var: model input feature

    Return:
        dataFrame of the input feature with same name
    """
    var_df = pd.DataFrame({'key': [1, 1], var: [0, 1]})
    return var_df


def pred_mapping(row, dict):
    """
    Maps predicted survival category to actual target category or remarks

    Arguments:
        row: one row in the scored data
        dict: dictionary prediction mapping

    Return:
        Survival category corresponding to predicted class
    """
    val = dict[row['score']]
    return val


def scoring(model_pkl_path, model_pkl_file=None, target_mapping=None, input_features=None, remarks=None):
    """
    1. Creates base for offline scoring considering all possible combination of feature values
    2. Scores offline base with fit model

    Arguments:
        model_pkl: pickle object of trained model
        target_mapping: dictionary defining mapping of predicted class: target category
        input_features: list of independent variables in the model
        remarks: dictionary to provide user interesting insight from model prediction

    Returns:
        offline scored data for model serving
    """

    # creating a dictionary of dataFrames for each of the model input variables
    d = {}
    for var in input_features:
        d[var] = input_var_df(var)

    # creating cartesian product of individual dataFrames to simulate all possible scenarios
    score_data = d[next(iter(d))]
    for var in d.keys():
        if var != next(iter(d)):
            score_data = score_data.merge(d[var], on='key')

    logger.info("Offline score base created with %d rows", len(score_data))

    # loading model from pickle object
    model_pkl = os.path.join(model_pkl_path, model_pkl_file)
    try:
        with open(model_pkl, 'rb') as file:
            model = pickle.load(file)
    except FileNotFoundError as e:
        logger.error("Model object not found at " + model_pkl)
        raise SystemExit("Trained model object not found!")

    try:
        # scoring data
        score_data['score'] = model.predict(score_data[input_features])
    except KeyError as e:
        logger.error(e)
        raise SystemExit("Offline scoring failed!")

    try:
        # getting target mapping
        score_data['prediction'] = score_data.apply(pred_mapping, dict=target_mapping, axis=1)

        # remarks based on prediction
        score_data['remarks'] = score_data.apply(pred_mapping, dict=remarks, axis=1)

        # setting primary key
        score_data['id'] = score_data.index

        # dropping 'key' (used only to create the cartesian product)
        score_data = score_data.drop('key', axis=1)

        logger.info("Offline data scored!")

    except KeyError as e:
        logger.error("Missing key in 'target_mapping' or 'remarks' dictionaries. Might lead to missing predictions!")

    return score_data



