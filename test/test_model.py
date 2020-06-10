import pandas as pd
import sklearn
import pytest
import src.model as model

happy_path = {'Gender': [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
              'Nobility': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
              'isMarried': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
              'boolDeadRelations': [0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
              'isPopular': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
              'HouseBaratheon': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
              'HouseLannister': [1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
              'HouseStark': [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
              'HouseTargaryen': [0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
              'NightsWatch': [0, 0, 0, 0, 1, 1, 0, 1, 0, 0],
              'Wildling': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
              'survive_class_id': [0, 1, 2, 0, 0, 2, 0, 2, 0, 1]}

input_features = ['Gender', 'Nobility', 'boolDeadRelations', 'isPopular', 'isMarried', 'HouseBaratheon',
                  'HouseLannister', 'HouseStark', 'HouseTargaryen', 'NightsWatch', 'Wildling']

target_column = 'survive_class_id'


def test_happy_check_df():
    """
    Test happy path for check_df()
    Returns: Pass if input is a dataframe
    """
    input_df = pd.DataFrame(happy_path)
    test_df = model.check_df(input_df)
    assert test_df.equals(input_df)


def test_unhappy_check_df():
    """
    Test unhappy path for check_df() - None object
    Returns: Pass if raises SystemExit
    """
    input_df = None
    with pytest.raises(SystemExit) as e:
        model.check_df(input_df)
    assert str(e.value) == "Input expected: DataFrame object"


def test_happy_check_features_target():
    """
    Test happy path for check_features_target()
    Returns: Pass if input_df contains all model features and target variable with multiple categories
    """
    input_df = pd.DataFrame(happy_path)

    test_df = model.check_features_target(input_df, input_features, target_column)
    assert test_df.equals(input_df)


def test_unhappy_check_features_target():
    """
    Test unhappy path for check_features_target() - missing target variable
    Returns: Pass if SystemExit is raised
    """
    input_df = pd.DataFrame(happy_path).drop(target_column, axis=1)

    with pytest.raises(SystemExit) as e:
        model.check_features_target(input_df, input_features, target_column)
    assert str(e.value) == "Please provide target column"


def test_happy_train_test_split():
    """
    Test happy path for train_test_split()
    Returns: Pass if split is in correct proportion
    """
    input_df = pd.DataFrame(happy_path)
    features = input_df[input_features]
    target = input_df[target_column]
    X_train, X_test, y_train, y_test = model.train_test_split(features, target, 0.4, 123)
    assert_case = 0
    if len(X_train) == len(y_train) == 6:
        assert_case += 1
    if len(X_test) == len(y_test) == 4:
        assert_case += 1
    assert assert_case == 2


def test_unhappy_train_test_split():
    """
    Test unhappy path for train_test_split() - sampling proportion > 1
    Returns: Pass if systemExit is raised
    """
    input_df = pd.DataFrame(happy_path)
    features = input_df[input_features]
    target = input_df[target_column]

    with pytest.raises(SystemExit) as e:
        model.train_test_split(features, target, 1.4, 123)
    assert str(e.value) == "Invalid train:test split proportion"


def test_happy_fit_model():
    """
    Test happy path for fit_model()
    Returns: Pass if expected model object is fit
    """
    input_df = pd.DataFrame(happy_path)
    features = input_df[input_features]
    target = input_df[target_column]

    model_obj = model.fit_model(features, target, input_features, 2, 'gini', 2, 2, 123, 'balanced')

    assert isinstance(model_obj, sklearn.ensemble.forest.RandomForestClassifier)


def test_unhappy_fit_model():
    """
    Test unhappy path for fit_model() - missing model feature
    Returns: Pass if SystemExit is raised
    """
    input_df = pd.DataFrame(happy_path)
    features = input_df[input_features].drop('isMarried', axis=1)
    target = input_df[target_column]

    with pytest.raises(SystemExit) as e:
        model.fit_model(features, target, input_features, 2, 'gini', 2, 2, 123, 'balanced')
    assert str(e.value) == "fit_model: incorrect model features"

