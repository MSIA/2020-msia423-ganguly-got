import pandas as pd
import numpy as np
import logging
logger = logging.getLogger(__name__)


def book_intro(df):
    """Creates column book_intro from binary fields about presence of character in each book"""
    try:
        df['book_intro'] = np.where(df['GoT'] == 1, 1,
                                    np.where(df['CoK'] == 1, 2,
                                             np.where(df['SoS'] == 1, 3,
                                                      np.where(df['FfC'] == 1, 4, 5))))
        return df
    except KeyError as error:
        logger.error("book_intro: " + str(error))
        raise SystemExit("book_intro: Key Error")
    except TypeError as error:
        logger.error("book_intro: " + str(error))
        raise SystemExit("book_intro: Type Error")


def fill_death_chapter(row, dict):
    """If book of death is known and chapter of death is not, assume character died in the middle of the book"""
    try:
        if pd.notna(row['Book of Death']) and pd.isna(row['Death Chapter']):
            return dict[row['Book of Death']] / 2
        else:
            return row['Death Chapter']
    except KeyError as error:
        logger.error("fill_death_chapter: KeyError " + str(error))
        raise SystemExit("fill_death_chapter: Key Error")
    except TypeError as error:
        logger.error("fill_death_chapter: " + str(error))
        raise SystemExit("fill_death_chapter: Type Error")


def fill_intro_chapter(row, dict):
    """If book of intro is known and chapter of intro is not, assume character was introduced in the middle of the
    book """
    try:
        if pd.notna(row['book_intro']) and pd.isna(row['Book Intro Chapter']):
            return dict[row['book_intro']] / 2
        else:
            return row['Book Intro Chapter']
    except KeyError as error:
        logger.error("fill_intro_chapter: " + str(error))
        raise SystemExit("fill_intro_chapter: Key Error")
    except TypeError as error:
        logger.error("fill_intro_chapter: " + str(error))
        raise SystemExit("fill_intro_chapter: Key Error")


def clean_allegiance(df):
    """Clean up 'Allegiance' column to have only the 6 major houses to reduce number of dummy variables"""
    try:
        df['Allegiances'] = np.where(df['Allegiances'] == 'Lannister', 'House Lannister',
                            np.where(df['Allegiances'] == 'Targaryen', 'House Targaryen',
                            np.where(df['Allegiances'] == 'Greyjoy', 'House Greyjoy',
                            np.where(df['Allegiances'] == 'Baratheon', 'House Baratheon',
                            np.where(df['Allegiances'] == 'Arryn', 'House Arryn',
                            np.where(df['Allegiances'] == 'Tyrell', 'House Tyrell',
                            np.where(df['Allegiances'] == 'Stark', 'House Stark',
                            np.where(df['Allegiances'] == 'Martell', 'House Martell',
                            np.where(df['Allegiances'] == 'Tully', 'House Tully',
                            np.where(df['Allegiances'] == "Night's Watch", 'Nights Watch',
                            np.where(df['Allegiances'] == "None", 'NoneH',
                                     df['Allegiances'])))))))))))
        df['Allegiances'] = df['Allegiances'].str.replace(" ", "")

        df['Allegiance'] = np.where(df['Allegiances'] == 'HouseLannister', 'HouseLannister',
                           np.where(df['Allegiances'] == 'HouseBaratheon', 'HouseBaratheon',
                           np.where(df['Allegiances'] == 'HouseStark', 'HouseStark',
                           np.where(df['Allegiances'] == 'HouseTargaryen', 'HouseTargaryen',
                           np.where(df['Allegiances'] == 'NightsWatch', 'NightsWatch',
                           np.where(df['Allegiances'] == 'Wildling', 'Wildling',
                                    'Others'))))))

        clean_df = df[df['Allegiance'] != 'Others']     # keeping only characters from 6 major houses

        return clean_df
    except KeyError as error:
        logger.error("clean_allegiance: " + str(error))
        raise SystemExit("clean_allegiance: Key Error")
    except TypeError as error:
        logger.error("clean_allegiance: " + str(error))
        raise SystemExit("clean_allegiance: Key Error")


def clean_base(base_df, book_chapter=None):
    """
    Cleans up base data (character-deaths.csv)
    1. Fills gaps in 'Death Chapter' and 'Book Intro Chapter'
    2. Cleans up 'Allegiance' column to ensure uniformity
    3. Retains characters only from the 6 major houses

    Arguments:
        base_df: raw data from character-deaths.csv
        book_chapter: dictionary defining each book and the number of chapters in it

    Returns:
        clean data - clean_base.csv
    """
    # base_df.rename(columns={'GoT': 'GOT'}, inplace=True)
    logger.debug("Number of rows in raw data = %d", len(base_df))

    # book where character was introduced
    base_df = book_intro(base_df)
    logger.info("Created column 'book_intro'")

    # filling gaps in death and intro chapters
    base_df['Death Chapter'] = base_df.apply(fill_death_chapter, dict=book_chapter, axis=1)
    base_df['Book Intro Chapter'] = base_df.apply(fill_intro_chapter, dict=book_chapter, axis=1)
    logger.info("Filled gaps in 'intro chapter' and 'death chapter'")

    # cleaning 'Allegiances' column to ensure uniformity
    base_df = clean_allegiance(base_df)
    logger.info("Clean base created")

    logger.debug("Number of rows in clean data = %d", len(base_df))

    return base_df
