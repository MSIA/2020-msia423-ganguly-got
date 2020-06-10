import pandas as pd
import numpy as np
import pytest
import src.clean as clean

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
              'DwD': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0]}


def test_happy_book_intro():
    """
    Testing 'happy path' for book_intro
    :return: True if book_intro is correctly computed
    """
    input_df = pd.DataFrame(happy_path)

    book_intro_true = input_df
    book_intro_true['book_intro'] = [1, 3, 5, 5, 3, 2, 1, 1, 2, 3]

    book_intro_test = clean.book_intro(input_df)

    assert book_intro_test.equals(book_intro_true)


def test_unhappy_book_intro():
    """
    Testing 'unhappy path' for book_intro - unexpected column name
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
                             'GOT': [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                             'CoK': [1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
                             'SoS': [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
                             'FfC': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                             'DwD': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0]})

    with pytest.raises(SystemExit) as e:
        clean.book_intro(input_df)
    assert str(e.value) == "book_intro: Key Error"


def test_happy_fill_death_chapter():
    """
    Testing 'happy path' for fill_death_chapter
    :return: True if fill_death_chapter is correctly computed
    """
    input_df = pd.DataFrame(happy_path)

    fill_death_chapter_true = pd.DataFrame(
        {'Allegiances': ['Lannister', 'House Frey', 'House Targaryen', 'House Greyjoy', 'Lannister',
                         'Baratheon', "Night's Watch", 'House Frey', 'House Greyjoy',
                         "Night's Watch"],
         'Death Year': [np.nan, 299, np.nan, 300, np.nan, np.nan, 300, 300, np.nan, np.nan],
         'Book of Death': [np.nan, 3, np.nan, 5, np.nan, np.nan, 4, 5, np.nan, np.nan],
         'Death Chapter': [np.nan, 51, np.nan, 20, np.nan, np.nan, 35, 35.5, np.nan, np.nan],
         'Book Intro Chapter': [56, 49, 5, 20, np.nan, np.nan, 21, 59, 11, 0],
         'Gender': [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
         'Nobility': [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
         'GoT': [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
         'CoK': [1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
         'SoS': [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
         'FfC': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
         'DwD': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0]})

    fill_death_chapter_test = input_df
    fill_death_chapter_test['Death Chapter'] = fill_death_chapter_test.apply(clean.fill_death_chapter,
                                                                             dict=book_chapter, axis=1)

    assert fill_death_chapter_test.equals(fill_death_chapter_true)


def test_unhappy_fill_death_chapter():
    """
    Testing 'unhappy path' for fill_death_chapter - unexpected column type
    :return: True if raises SystemExit
    """
    input_df = pd.DataFrame({'Allegiances': ['Lannister', 'House Frey', 'House Targaryen', 'House Greyjoy', 'Lannister',
                                             'Baratheon', "Night's Watch", 'House Frey', 'House Greyjoy',
                                             "Night's Watch"],
                             'Death Year': [np.nan, 299, np.nan, 300, np.nan, np.nan, 300, 300, np.nan, np.nan],
                             'Book of Death': [None, '3', None, '5', None, None, '4', '5', None, None],
                             'Death Chapter': [np.nan, 51, np.nan, 20, np.nan, np.nan, 35, np.nan, np.nan, np.nan],
                             'Book Intro Chapter': [56, 49, 5, 20, np.nan, np.nan, 21, 59, 11, 0],
                             'Gender': [1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
                             'Nobility': [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                             'GOT': [1, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                             'CoK': [1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
                             'SoS': [1, 1, 0, 0, 1, 1, 1, 1, 0, 1],
                             'FfC': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                             'DwD': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0]})

    fill_death_chapter_test = input_df

    with pytest.raises(SystemExit) as e:
        fill_death_chapter_test['Death Chapter'] = fill_death_chapter_test.apply(clean.fill_death_chapter,
                                                                                 dict=book_chapter, axis=1)
    assert e.type == SystemExit


def test_happy_clean_allegiance():
    """
    Testing 'happy path' for clean_allegiance
    :return: True if length of filtered data and unique values of cleaned columns are as expected
    """
    input_df = pd.DataFrame(happy_path)
    clean_allegiance_test = clean.clean_allegiance(input_df)

    assert_counter = 0
    if len(clean_allegiance_test) == 6:
        assert_counter += 1
    if set(clean_allegiance_test['Allegiance'].unique()) == set(['HouseLannister', 'HouseBaratheon',
                                                                 'HouseTargaryen', 'NightsWatch']):
        assert_counter += 1

    assert assert_counter == 2


def test_unhappy_clean_allegiance():
    """
    Testing 'unhappy path' for clean_allegiance
    :return: True if raises SystemExit
    """
    input_df = pd.DataFrame(happy_path)
    input_df.rename(columns={'Allegiances': 'Alegiance'}, inplace=True)

    with pytest.raises(SystemExit) as e:
        clean.clean_allegiance(input_df)
    assert str(e.value) == "clean_allegiance: Key Error"
