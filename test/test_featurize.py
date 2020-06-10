import pandas as pd
import numpy as np
import pytest
import src.featurize as featurize

book_chapter = {1: 72, 2: 69, 3: 80, 4: 45, 5: 71}

happy_path = {'Allegiances': ['Lannister', 'House Frey', 'House Targaryen', 'House Greyjoy', 'Lannister',
                              'Baratheon', "Night's Watch", 'House Frey', 'House Greyjoy',
                              "Night's Watch"],
              'Death Year': [np.nan, 299, np.nan, 300, np.nan, np.nan, 300, 300, np.nan, np.nan],
              'Book of Death': [np.nan, 3, np.nan, 5, np.nan, np.nan, 4, 5, np.nan, np.nan],
              'Death Chapter': [np.nan, 51, np.nan, 20, np.nan, np.nan, 35, np.nan, np.nan, np.nan],
              'Book Intro Chapter': [56, 49, 5, 20, np.nan, np.nan, 21, 59, 11, 0],
              'Gender': [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
              'Nobility': [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
              'GoT': [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
              'CoK': [1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
              'SoS': [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
              'FfC': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
              'DwD': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
              'book_intro': [1, 3, 5, 5, 3, 2, 1, 1, 2, 3]}


def test_happy_chapters_survived():
    """
    Testing 'happy path' for chapters_survived
    :return: True if chapters_survived is correctly computed
    """
    input_df = pd.DataFrame(happy_path)

    chapters_survived_true = input_df
    chapters_survived_true['GoT_chapters'] = [16, 0, 0, 0, 0, 0, 51, 13, 0, 0]
    print(chapters_survived_true)

    chapters_survived_test = featurize.chapters_survived(input_df, 'GoT_chapters', 1.0, book_chapter)
    print(chapters_survived_test)

    assert chapters_survived_test.equals(chapters_survived_true)


def test_unhappy_chapters_survived():
    """
    Testing 'unhappy path' for chapters_survived - missing key in dictionary
    :return: True if raises SystemExit
    """
    missing_key_dict = {1: 72, 3: 80, 4: 45, 5: 71}
    input_df = pd.DataFrame(happy_path)

    with pytest.raises(SystemExit) as e:
        featurize.chapters_survived(input_df, 'CoK_chapters', 2.0, missing_key_dict)
    assert str(e.value) == "book_survival: Key Error"


def test_happy_target_class():
    """
    Testing 'happy path' for target_class
    :return: True if unique values of target column are as expected
    """
    input_df = pd.DataFrame({'Allegiances': ['Lannister', 'House Frey', 'House Targaryen', 'House Greyjoy', 'Lannister',
                                             'Baratheon', "Night's Watch", 'House Frey', 'House Greyjoy',
                                             "Night's Watch"],
                             'Death Year': [np.nan, 299, np.nan, 300, np.nan, np.nan, 300, 300, np.nan, np.nan],
                             'Book of Death': [np.nan, 3, np.nan, 5, np.nan, np.nan, 4, 5, np.nan, np.nan],
                             'Death Chapter': [np.nan, 51, np.nan, 20, np.nan, np.nan, 35, np.nan, np.nan, np.nan],
                             'Book Intro Chapter': [56, 49, 5, 20, np.nan, np.nan, 21, 59, 11, 0],
                             'Gender': [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                             'Nobility': [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                             'GoT': [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                             'CoK': [1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
                             'SoS': [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
                             'FfC': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                             'DwD': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
                             'book_intro': [1, 3, 5, 5, 3, 2, 1, 1, 2, 3],
                             'chapters_survived': [281, 66, 156, 230.5, 235, 196, 283, 180, 311, 42]})

    target_class_test = featurize.target_class(input_df, 'survive_class_id')

    assert set(target_class_test['survive_class'].unique()) == set(['0-100', '100-200', 'gt200'])


def test_unhappy_target_class():
    """
    Testing 'unhappy path' for target_class - missing column
    :return: True if raises SystemExit
    """
    input_df = pd.DataFrame({'Allegiances': ['Lannister', 'House Frey', 'House Targaryen', 'House Greyjoy', 'Lannister',
                                             'Baratheon', "Night's Watch", 'House Frey', 'House Greyjoy',
                                             "Night's Watch"],
                             'Death Year': [np.nan, 299, np.nan, 300, np.nan, np.nan, 300, 300, np.nan, np.nan],
                             'Book of Death': [np.nan, 3, np.nan, 5, np.nan, np.nan, 4, 5, np.nan, np.nan],
                             'Death Chapter': [np.nan, 51, np.nan, 20, np.nan, np.nan, 35, np.nan, np.nan, np.nan],
                             'Book Intro Chapter': [56, 49, 5, 20, np.nan, np.nan, 21, 59, 11, 0],
                             'Gender': [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                             'Nobility': [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                             'GoT': [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                             'CoK': [1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
                             'SoS': [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
                             'FfC': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                             'DwD': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0],
                             'book_intro': [1, 3, 5, 5, 3, 2, 1, 1, 2, 3]})

    with pytest.raises(SystemExit) as e:
        featurize.target_class(input_df, 'survive_class_id')
    assert str(e.value) == "target_class: Key Error"
