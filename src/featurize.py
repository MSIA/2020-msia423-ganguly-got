import pandas as pd
import numpy as np
import logging
import src.eda_plots as eda_plots

logger = logging.getLogger(__name__)

pd.options.mode.chained_assignment = None       # suppress warnings


def book_survival(row, bookno, dict):
    """
    Computes number of chapters survived in a given book

    Arguments:
        row: information about one character
        bookno: one of the 5 books of the series
        dict: dictionary holding the number of chapters in each book {bookNum: numChapters}

    Returns:
        number of chapters given character survives in the given book as an integer
    """
    try:
        if row['book_intro'] == row['Book of Death'] == bookno:     # introduced and died in same book
            val = row['Death Chapter'] - row['Book Intro Chapter']
        elif row['book_intro'] == bookno:       # introduced in given book, did not die in same book
            val = dict[bookno] - row['Book Intro Chapter']
        elif row['book_intro'] < bookno and (row['Book of Death'] > bookno or pd.isna(row['Book of Death'])):
            val = dict[bookno]
        elif row['Book of Death'] == bookno:        # died in given book
            val = row['Death Chapter']
        else:
            val = 0
        return val
    except KeyError as error:
        logger.error("book_survival: " + str(error))
        raise SystemExit("book_survival: Key Error")
    except TypeError as error:
        logger.error("book_survival: " + str(error))
        raise SystemExit("book_survival: Type Error")


def chapters_survived(df, book, booknum, dict):
    """
    Calls 'book_survival()' defined above to compute the chapters survived by each character in the given book

    Arguments:
        df: base dataFrame
        book: name of new column
        booknum: serial number of given book
        dict: dictionary holding the number of chapters in each book {bookNum: numChapters}

    Returns:
        df with new column storing number of chapters survived in given book
    """
    df[book] = df.apply(book_survival, bookno=booknum, dict=dict, axis=1)
    return df


def target_continuous(df):
    """
    1. Computes total number of chapters survived across all 5 books
    2. Drops the 2 rows with negative value for chapters survived - data issue
    """
    try:
        df['chapters_survived'] = df['GoT_chapters'] + df['CoK_chapters'] + df['SoS_chapters'] + \
                                  df['FfC_chapters'] + df['DwD_chapters']

        # dropping rows with negative chapters survived (2 rows) - data issue
        df = df[df['chapters_survived'] >= 0]

        return df
    except KeyError as error:
        logger.error("target_continuous: " + str(error))
    except TypeError as error:
        logger.error("target_continuous: " + str(error))


def target_class(df, target_column):
    """
    1. Converts chapters survived to three categories - '0-100', '101-200', 'gt200'
    2. Factorizes categories to use as target in Random Forest model
    """
    # creating target classes
    try:
        df['survive_class'] = np.where(df['chapters_survived'] <= 100, '0-100',
                              np.where(df['chapters_survived'] <= 200, '100-200', 'gt200'))
        df[target_column] = df['survive_class'].factorize()[0]
        return df
    except KeyError as error:
        logger.error("target_class: " + str(error))
        raise SystemExit("target_class: Key Error")
    except TypeError as error:
        logger.error("target_class: " + str(error))
        raise SystemExit("target_class: Type Error")


def merge_df(base, profile):
    """
    Merges base data with the character profile data

    Arguments:
        base: base dataFrame from clean_base.csv
        csv: character-profile.csv

    Returns:
        merged dataFrame including profile variables like 'isMarried', 'boolDeadRelations', 'isPopular'
    """
    try:
        base_merged = pd.merge(base,
                               profile[['name', 'isMarried', 'boolDeadRelations', 'isPopular']],
                               left_on='Name', right_on='name',
                               how='left', sort=False)
        return base_merged
    except KeyError as e:
        logger.error("merge_df: KeyError on " + str(e))
        raise SystemExit("profile data merge: KeyError on " + str(e))


def fill_na(df):
    """
    Fill na values with 0
    """
    try:
        complete_df = df.replace([np.inf, -np.inf], np.nan).fillna(0)
        return complete_df
    except AttributeError as e:
        logger.error("fill_na: " + str(e))
        raise SystemExit("fill_na: " + str(e))


def get_dummy(df, col):
    """
    Creates dummy variables from given categorical column

    Arguments:
        df: base dataFrame
        col: categorical column to create dummies for

    Returns:
        df_dummy: base data with new dummy columns
    """
    try:
        dummy = pd.get_dummies(df[col])
        df_dummy = pd.concat([df, dummy], axis=1)
        return df_dummy
    except KeyError as error:
        logger.error("get_dummy: " + str(error))
    except TypeError as error:
        logger.error("get_dummy: " + str(error))


def featurize(base_df, profile_df, eda_plot_path,
              book_chapter=None, target_column=None, eda_plot_features=None):
    """
    Creates features for modeling
    1. Creates target variable - survive_class_id
    2. Merges features from character-profile.csv
    3. Fills gaps in features with 0
    4. Creates dummy columns for 'Allegiance'

    Arguments:
        base_df: dataFrame from clean_base.csv
        profile_df: character-profile.csv
        book_chapter: dictionary holding the number of chapters in each of the 5 books {bookNum: numChapters}

    Returns:
        features: clean df with model features and target variable
    """
    # computing chapters survived in each of the 5 books
    logger.info("Computing chapters survived in each of the 5 books")
    base_df = chapters_survived(base_df, 'GoT_chapters', 1.0, book_chapter)
    base_df = chapters_survived(base_df, 'CoK_chapters', 2.0, book_chapter)
    base_df = chapters_survived(base_df, 'SoS_chapters', 3.0, book_chapter)
    base_df = chapters_survived(base_df, 'FfC_chapters', 4.0, book_chapter)
    base_df = chapters_survived(base_df, 'DwD_chapters', 5.0, book_chapter)

    # computing total chapters survived - continuous target
    logger.info("Computing total chapters survived - continuous target")
    base_df = target_continuous(base_df)

    # creating target classes
    logger.info("Creating target classes")
    base_df = target_class(base_df, target_column)

    # merging character profile information from character-profile.csv
    logger.info("Merging character profile information to base")
    merged = merge_df(base_df, profile_df)

    # filling missing profile information with 0
    logger.info("Imputing missing information with 0")
    complete = fill_na(merged)

    # generating EDA plots
    logger.info("Creating bi-variate plots of features and dependent variable for EDA")
    eda_plots.eda_plots(complete, eda_plot_path, target_column, eda_plot_features)

    # creating dummies for 'Allegiances'
    logger.info("Creating dummies for 'Allegiance'")
    features = get_dummy(complete, 'Allegiance')

    if not isinstance(features, pd.DataFrame):
        logger.error("Features could be created successfully")
        raise SystemExit("src.featurize failed!")
    else:
        if sum(features.isin([None, np.nan, np.inf, -np.inf]).sum()) > 0:
            isnull = pd.DataFrame(features.isin([None, np.nan, np.inf, -np.inf]).sum())
            features_with_na = list(isnull[isnull[0] > 0].index)
            logger.error("Features computed with missing values: {}".format(' '.join(map(str, features_with_na))))
            logger.error("Missing features must be imputed before model fitting.")
        return features


