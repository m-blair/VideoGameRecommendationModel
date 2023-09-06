import pandas as pd
import numpy as np
from pathlib import Path
from os import getcwd
import string
from collections import Counter
from nltk.tokenize import word_tokenize, TweetTokenizer
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords
from sklearn.preprocessing import LabelBinarizer, MultiLabelBinarizer, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import category_encoders as ce
from typing import List

stop_words = set(stopwords.words('english'))
puncts_to_exclude = "."
punctuation = string.punctuation.replace(puncts_to_exclude, '')

# ///////////////////////////////////////////// PREPROCESSING //////////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

stemmer = PorterStemmer()


# need to get unique combos of genres, ignoring ordering
def count_genre_combinations(df: pd.DataFrame, col_name: str):
    genre_lists = df[col_name].apply(lambda x: x.split(','))
    genre_combos_counter = Counter([frozenset(genre_list) for genre_list in genre_lists])
    return genre_combos_counter


def strip_escape_chars(df: pd.DataFrame, col_name: str) -> pd.Series | pd.DataFrame | None:
    if col_name in list(df.columns):
        return pd.DataFrame(df[col_name].apply(lambda x: x.replace('\r', '').replace('\n', '') if pd.notnull(x) else x))
    else:
        raise ValueError(f"Invalid column name {col_name} for the provided dataframe.")


def trim_escape_chars(text: str, chars: List[str] = None) -> str:
    if not chars:
        return text.replace('\r', '').replace('\n', '')
    else:
        for char in chars:
            text = text.replace(char, "")
        return text


def preprocess_text(text: str, stem_words: bool = True, remove_stopwords: bool = True,
                    remove_numeric: bool = True) -> str:
    # lowercase
    text = text.lower()
    # remove punctuation
    text = text.translate(str.maketrans("", "", punctuation))
    # get tokens
    tokens = word_tokenize(text)
    # remove stop words
    if remove_stopwords:
        tokens = [word for word in tokens if word not in stop_words]

    if stem_words and not remove_numeric:
        tokens = [stemmer.stem(token) for token in tokens]

    # stem tokens
    elif stem_words and remove_numeric:
        tokens = [stemmer.stem(token) for token in tokens if not token.isnumeric()]

    elif not stem_words and remove_numeric:
        tokens = [token for token in tokens if not token.isnumeric()]

    # re-join stems
    return " ".join(tokens)


# ///////////////////////////////////////////// FEATURE ENCODING ///////////////////////////////////////////////////////
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


def binary_encode(df: pd.DataFrame, col_name: str):
    encoder = LabelBinarizer()
    encoded = encoder.fit_transform(df[col_name])
    return encoded


def one_hot_encode(df: pd.DataFrame, col_name: str):
    # Split the genre strings into lists of individual genres
    split_df = df[col_name].apply(lambda x: x.split(','))

    # Create a set of all individual genres
    all_individual_genres = set(genre for sublist in split_df for genre in sublist)

    # Create a new DataFrame for the one-hot encoded genres
    one_hot_encoded_df = pd.DataFrame(index=df.index)

    # Loop through each individual genre and create a binary column for it
    for i in all_individual_genres:
        one_hot_encoded_df[i] = split_df.apply(lambda x: int(i in x))

    return one_hot_encoded_df


def multilabel_encode(df: pd.DataFrame):
    genre_list = df['genres'].apply(lambda x: x.split(','))

    # Create a list of unique genres
    unique_genres = set(genre for sublist in genre_list for genre in sublist)

    # Create a new DataFrame for the one-hot encoded genres
    one_hot_encoded_df = pd.DataFrame(index=df.index)

    # Loop through each unique genre and create a binary column for it
    for genre in unique_genres:
        one_hot_encoded_df[genre] = genre_list.apply(lambda x: int(genre in x))

    return one_hot_encoded_df
