import pandas as pd
import numpy as np
import re
from pathlib import Path
from os import listdir, getcwd
from importlib import reload
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, normalize
from text_processing.similarity_metrics import recommend_similar_games, cosine_similarity
from text_processing import nlp, similarity_metrics
from collections import Counter
from ast import literal_eval
import matplotlib.pyplot as plt

platform_aliases = {
    "Legacy Mobile Device": "Mobile",
    "PlayStation": "PS1",
    "PlayStation 2": "PS2",
    "PlayStation 3": "PS3",
    "PlayStation 4": "PS4",
    "PlayStation 5": "PS5",
    "PlayStation Vita": "VITA",
    "PS Vita": "VITA",
    "PlayStation Portable": "PSP",
    "PlayStation VR": "PSVR",
    "PlayStation VR2": "PSVR2",
    "Dreamcast": "DC",
    "Game Boy": "GB",
    "Game Boy Color": "GBC",
    "Game Boy Advance": "GBA",
    "Nintendo GameCube": "GCN",
    "GameCube": "GCN",
    "Nintendo 3DS": "3DS",
    "Nintendo 64": "N64",
    "Nintendo DS": "DS",
    "Nintendo DSi": "DSi",
    "Nintendo Switch": "NS",
    "Sega Game Gear": "GG",
    "Game Gear": "GG",
    "Sega Mega Drive/Genesis": "GEN",
    "Genesis": "GEN",
    "SEGA 32X": "32X",
    "SEGA CD": "SCD",
    "Sega Master System/Mark III": "SMS",
    "SEGA Master System": "SMS",
    "Sega Saturn": "SAT",
    "Xbox": "XBOX",
    "Xbox 360": "XB360",
    "Xbox One": "XB1",
    "Xbox Series S/X": "XSX",
    "Xbox Series X|S": "XSX",
    "Family Computer": "FC",
    "Nintendo Famicom": "FC",
    "Famicom": "FC",
    "Family Computer Disk System": "FDS",
    "Super Famicom": "SFC",
    "Nintendo Entertainment System": "NES",
    "Super Nintendo Entertainment System": "SNES",
    "PC (Microsoft Windows)": "Windows",
    "New Nintendo 3DS": "New 3DS",
    "Nintendo 64DD": "64DD",
    "Turbografx-16/PC Engine CD": "TGCD/PCECD",
    "TurboGrafx-16/PC Engine": "TG16/PCE",
    "Web browser": "Browser",
    "Neo Geo CD": "NGCD",
    "ZX Spectrum": "ZXS",
    "3DO Interactive Multiplayer": "3DO",
    "Philips CD-i": "CDI",
    "Amiga CD32": "CD32",
    "N-Gage": "NGAGE",
    "Game.com": "GCOM",
    "Commodore VIC-20": "VIC",
    "Commodore C64/128/MAX": "C64",
    "Commodore 16": "C16",
    "Atari 2600": "A26",
    "Atari 5200": "A52",
    "Atari 7800": "A78",
    "Atari Lynx": "LYNX",
    "Atari Jaguar": "JAG",
    "Atari Jaguar CD": "JCD",
    "Odyssey 2 / Videopac G7000": "ODY2",
    "Amiga": "AMI",
    "Amazon Fire TV": "FIRE",
    "Oculus Rift": "RIFT",
    "Vectrex": "VECT",
    "Neo Geo AES": "AES",
    "Neo Geo Pocket": "NGP",
    "Neo Geo Pocket Color": "NGPC",
    "ColecoVision": "CV",
    "Intellivision": "INTV"
}

age_ratings_map = {
    "Three": 'EC',
    "Seven": 'E',
    "Twelve": 'E10',
    "Sixteen": 'T',
    "Eighteen": 'M',
    "RP": 'RP',
    "EC": "EC",
    "E": "E",
    "E10": "E10",
    "T": "T",
    "M": "M",
    "AO": "AO",
    "CERO_A": "E",
    "CERO_B": "E10",
    "CERO_C": "T",
    "CERO_D": "M",
    "CERO_Z": "M",
    "USK_0": "E",
    "USK_6": "E10",
    "USK_12": "T",
    "USK_16": "T",
    "USK_18": "M",
    "GRAC_ALL": "E",
    "GRAC_Twelve": "E10",
    "GRAC_Fifteen": "T",
    "GRAC_Eighteen": "M",
    "GRAC_TESTING": "RP",
    "CLASS_IND_L": "E",
    "CLASS_IND_Ten": "E10",
    "CLASS_IND_Twelve": "T",
    "CLASS_IND_Fourteen": "T",
    "CLASS_IND_Sixteen": "T",
    "CLASS_IND_Eighteen": "M",
    "ACB_G": "E",
    "ACB_PG": "T",
    "ACB_M": "T",
    "ACB_MA15": "T",
    "ACB_R18": "M",
    "ACB_RC": "AO"
}

genre_map = {
    'Adventure': 'Adventure',
    'Sport': 'Sport',
    'Role-playing (RPG)': 'RPG',
    'Simulator': 'Simulation',
    'Shooter': 'Shooter',
    'Strategy': 'Strategy',
    'Platform': 'Platformer',
    'Puzzle': 'Puzzle',
    'Racing': 'Racing',
    'Fighting': 'Fighting',
    'Hack and slash/Beat \'em up': 'Hack & slash',
    'Arcade': 'Arcade',
    'Music': 'Rhythm',
    'Turn-based strategy (TBS)': 'TBS',
    'Tactical': 'Tactical',
    'Visual Novel': 'Visual Novel',
    'Real Time Strategy (RTS)': 'RTS',
    'Quiz/Trivia': 'Quiz/Trivia',
    'Card & Board Game': 'Card/Board',
    'Point-and-click': 'Point-and-click',
    'Indie': 'Indie',
    'Pinball': 'Pinball',
    'MOBA': 'MOBA'
}

esrb_ratings = ["RP", "EC", "E", "E10", "T", "M", "AO"]


def assign_platform_aliases(platform_str) -> str:
    if ',' in platform_str:
        platforms = platform_str.split(',')
        mapped_plats = [platform_aliases.get(platform, platform) for platform in platforms]
        return ','.join(mapped_plats)
    else:
        if platform_str in list(platform_aliases.keys()):
            return str(platform_aliases[platform_str])
        else:
            return platform_str


def assert_esrb_rating(age_ratings_str: str | None):
    if ',' in age_ratings_str:
        age_ratings_list = literal_eval(age_ratings_str)
        for rating in esrb_ratings:
            if rating in age_ratings_list:
                return rating

        if rating in age_ratings_map.keys():
            return age_ratings_map[rating]

    elif not age_ratings_str:
        return np.NaN

    else:
        rating = "".join(literal_eval(age_ratings_str))
        for r in esrb_ratings:
            if rating == r:
                return r

        if rating in age_ratings_map.keys():
            return age_ratings_map[rating]


def map_genres(genre_str: str):
    if ',' in genre_str:
        genre_list = list(literal_eval(genre_str))
        if len(genre_list) > 1:
            genres = []
            for genre in genre_list:
                if str(genre) in genre_map.keys():
                    genres.append(genre_map[genre])
            return ",".join(genres)
    else:
        genre_str = literal_eval(genre_str)
        return genre_map[genre_str]


def get_unique_companies(df: pd.DataFrame, col_name: str):
    companies = []
    for company_str in df[col_name].tolist():
        if ',' in company_str:
            company_list = company_str.split(',')
            for company in company_list:
                if company not in companies:
                    companies.append(company)
        else:
            if company_str not in companies:
                companies.append(company)
    return companies


def count_companies(df: pd.DataFrame, col_name: str):
    company_counts = Counter()
    for company_str in df[col_name].tolist():

        if ',' in company_str:
            company_list = company_str.lower().split(',')
            for company in company_list:
                if company not in company_counts.keys():
                    company_counts[company] = 1
                else:
                    company_counts[company] += 1
        else:
            company_str = company_str.lower()
            if company_str not in company_counts.keys():
                company_counts[company_str] = 1
            else:
                company_counts[company_str] += 1
    return company_counts


def find_simple_company_subsidiaries(parent_company: str, df: pd.DataFrame, col_name: str = 'companies', match_anywhere: bool = False):
    if not match_anywhere:
        parent_pattern = rf"^{parent_company}\s\w+"
    else:
        parent_pattern = rf"{parent_company}\s\w+"

    matches = []
    for i in df[col_name].tolist():
        if re.match(parent_pattern, i):
            matches.append(i)
        else:
            if str(i).__contains__(parent_company) and match_anywhere:
                matches.append(i)

    return matches