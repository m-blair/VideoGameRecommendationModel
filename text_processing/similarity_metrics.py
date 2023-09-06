import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from os import getcwd
from typing import List


# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def recommend_similar_titles_single_feature(similarity_matrix, target_game_index: int, N: int = 5):
    target_game_similarity_scores = similarity_matrix[target_game_index]

    # Sort indices based on similarity scores
    similar_game_indices = target_game_similarity_scores.argsort()[::-1]

    # Exclude the target game itself
    similar_game_indices = similar_game_indices[similar_game_indices != target_game_index]

    # Get the top N similar game indices
    top_similar_indices = similar_game_indices[:N]

    return top_similar_indices


def recommend_similar_games(scores, target_game_index, N=5):
    # Get the similarity score for the target game
    target_score = scores[target_game_index]

    # Calculate the absolute differences between the target score and all other scores
    score_differences = np.abs(scores - target_score)

    # Sort the indices based on score differences in ascending order (closest first)
    similar_game_indices = np.argsort(score_differences)

    # Exclude the target game (if it's in the recommendations)
    similar_game_indices = [i for i in similar_game_indices if i != target_game_index]

    # Return the top N similar game indices
    return similar_game_indices[:N]


