from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
from sklearn import metrics
import pandas as pd
import pickle
import logging
import os


logger = logging.getLogger(__name__)

def check_df(df):
    """
    Checks if argument is a Pandas Dataframe
    Returns df if true
    Raises SystemExit if false
    """
    if not isinstance(df, pd.DataFrame):
        logger.error("Input is not a DataFrame object")
        raise SystemExit("Input expected: DataFrame object")
    else:
        logger.info("Input is a DataFrame object as expected")
        return df

def check_features_target(df, feature_set, target_column):
    """
    Checks validity of features and target
    1. Presence of all model features in the input data
    2. Presence of target column
    3. Presence of more than one category in target
    """
    # check if all model features are present in df
    if not set(feature_set).issubset(df.columns):
        missing_features = [x for x in feature_set if x not in df.columns]
        logger.error("Following input variables not found: {}".format(' '.join(map(str, missing_features))))
        raise SystemExit("Please provide all input features")
    # check if target column present in df
    elif target_column not in df.columns:
        logger.error("Target variable not found! Cannot fit model")
        raise SystemExit("Please provide target column")
    # check if target column has at least two distinct categories
    elif len(df[target_column].unique()) == 1:
        logger.error("Target variable contains only one class! Cannot fit model")
        raise SystemExit("Please provide data with at least two classes")
    else:
        logger.info("Target and input features found for fitting model")
        return df

def train_test_split(features, target, test_size, random_seed):
    """
    Splits input data into train and test samples according to 'test_size'
    """
    try:
        # train-test split
        X_train, X_test, y_train, y_test = model_selection.train_test_split(features, target,
                                                                            test_size=test_size,
                                                                            random_state=random_seed)
        return X_train, X_test, y_train, y_test
    except ValueError as e:
        logger.error(e)
        raise SystemExit("Invalid train:test split proportion")


def fit_model(X_train, y_train, feature_set,
              n_estimators, criterion, max_depth, max_features, random_seed, class_weight):
    """
    Fits a Random Forest model and returns fit model object
    """
    if set(X_train.columns) != set(feature_set):
        logger.error("Incorrect model features passed")
        raise SystemExit("fit_model: incorrect model features")
    else:
        # fitting Random Forest model
        rf = RandomForestClassifier(n_estimators=n_estimators, criterion=criterion,
                                    max_depth=max_depth, max_features=max_features,
                                    random_state=random_seed, class_weight=class_weight)
        rf.fit(X_train, y_train)
        logger.info("Model fit successfully")
        return rf


def score_test(model_obj, test):
    """
    Scores test data with fit model
    """
    try:
        test_score = model_obj.predict(test)
        return test_score
    except ValueError as e:
        logger.error(e)
        raise SystemExit("score_test: ValueError")
    except KeyError as e:
        logger.error(e)
        raise SystemExit("score_test: KeyError")


def model(df, save_loaction, test_size=None, target_column=None, feature_set=None,
          random_seed=None, n_estimators=None, criterion=None, class_weight=None,
          max_depth=None, max_features=None,
          model_pickle_file=None, performance_metrics_txt=None):
    """Fitting model and testing performance on test data

    :param df: dataFrame with all model input features
    :param save_loaction: local file path to store model artifacts
    :param test_size: proportion of train:test split
    :param target_column: variable storing survival class
    :param feature_set: model independent variables
    :param random_seed: to fix random state for model reproducibility
    :param model_pickle_file: to export model object for future scoring
    :param performance_metrics_txt: .txt file where test performance metrics are written

    :param n_estimators: number of trees in the forest, default=100
    :param criterion: function to measure the quality of a split, default='gini'
    :param class_weight: weights associated with classes, default=None
    :param max_depth: maximum depth of the tree, default=None
    :param max_features: number of features to consider when looking for the best split, default='auto'

    :return: 1. exports model object as .pkl file
             2. writes performance metrics on test data
    """

    # check if input is a dataFrame object
    df = check_df(df)

    # check if all model features and target are present in input df
    df = check_features_target(df, feature_set, target_column)

    # splitting df into dependent and independent columns
    features = df[feature_set]
    target = df[target_column]

    # checking if random seed has been set
    if random_seed is None:
        logger.warning("Random state not set. Model results might vary between consecutive runs")

    # splitting into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size, random_seed)

    # fitting model
    model_obj = fit_model(X_train, y_train, feature_set,
              n_estimators, criterion, max_depth, max_features, random_seed, class_weight)

    # Save the model as .pkl object in the current working directory
    with open(os.path.join(save_loaction, model_pickle_file), 'wb') as file:
        logger.info("Exporting model to %s for future use", model_pickle_file)
        pickle.dump(model_obj, file)

    # scoring test data with the fitted model
    ypred_bin_test = score_test(model_obj, X_test)

    # computing performance metrics on test data
    confusion = metrics.confusion_matrix(y_test, ypred_bin_test)
    accuracy = metrics.accuracy_score(y_test, ypred_bin_test)

    logger.info("Accuracy on test: %0.3f", accuracy)

    confusion_matrix = pd.DataFrame(confusion, index=['Actual gt200', 'Actual 0-100', 'Actual 100-200'],
                                    columns=['Predicted gt200', 'Predicted 0-100', 'Predicted 100-200'])

    # writing performance metrics to text file
    f = open(os.path.join(save_loaction, performance_metrics_txt), "w")
    print("Accuracy on test: %0.3f" % accuracy, file=f)
    print("\nConfusion Matrix:", file=f)
    print(confusion_matrix, file=f)
    logger.info("Performance metrics written to %s", os.path.join(save_loaction, performance_metrics_txt))
    f.close()
