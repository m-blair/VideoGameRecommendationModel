from typing import List

import requests
from requests import Response
from typing import List
from Game import Game

# ///////////////////////////////////////////////////////////////////////////////////
# dicts needed for mapping json data

categories = {
    0: 'main_game',
    1: 'dlc_addon',
    2: 'expansion',
    3: 'bundle',
    4: 'standalone_expansion',
    5: 'mod',
    6: 'episode',
    7: 'season',
    8: 'remake',
    9: 'remaster',
    10: 'expanded_game',
    11: 'port',
    12: 'fork',
    13: 'pack',
    14: 'update'
}

age_ratings = {
    1: 'Three',
    2: 'Seven',
    3: 'Twelve',
    4: 'Sixteen',
    5: 'Eighteen',
    6: 'RP',
    7: 'EC',
    8: 'E',
    9: 'E10',
    10: 'T',
    11: 'M',
    12: 'AO',
    13: 'CERO_A',
    14: 'CERO_B',
    15: 'CERO_C',
    16: 'CERO_D',
    17: 'CERO_Z',
    18: 'USK_0',
    19: 'USK_6',
    20: 'USK_12',
    21: 'USK_16',
    22: 'USK_18',
    23: 'GRAC_ALL',
    24: 'GRAC_Twelve',
    25: 'GRAC_Fifteen',
    26: 'GRAC_Eighteen',
    27: 'GRAC_TESTING',
    28: 'CLASS_IND_L',
    29: 'CLASS_IND_Ten',
    30: 'CLASS_IND_Twelve',
    31: 'CLASS_IND_Fourteen',
    32: 'CLASS_IND_Sixteen',
    33: 'CLASS_IND_Eighteen',
    34: 'ACB_G',
    35: 'ACB_PG',
    36: 'ACB_M',
    37: 'ACB_MA15',
    38: 'ACB_R18',
    39: 'ACB_RC'
}


# ///////////////////////////////////////////////////////////////////////////////////

def format_query(title: str, search_type: str = 'name equals', sort_results: bool = False,
                 sort_by: str = 'release_dates.y asc', limit: int = 25, offset: int = 0):
    """formats an APICalypse query for IGDB \n
    :param offset: num of entries to skip
    :param limit: max num of entries to return
    :param sort_by: the sorting criteria, value must be passed if sort_by = True.
    Example: 'release_dates.y asc'
    :param title: the title to search for
    :param search_type: method to search for the title; accepted values include: 'search', 'name equals', 'name like'
    :param sort_results: sort the result of the query or not. Not compatible with search_type = 'search'. If true, then a value for 'sort_by' must also be passed
    """

    fields = ["id", "name", "release_dates.y", "category", "slug", "platforms.name", "genres.name", "tags",
              "age_ratings.rating", "rating", "rating_count", "similar_games.name", "themes.name", "summary",
              "involved_companies.company.name"]
    cats = [0, 1, 2, 8, 9, 10, 11]

    query_fields = f'f {",".join(fields)};'

    # searching criteria
    match search_type:
        case 'search':
            query_search = f'search "{title}";where (category = ({",".join([str(i) for i in cats])})) & (version_parent = null);'
        case 'name equals':
            query_search = f'where (name = "{title}") & (category = ({",".join([str(i) for i in cats])})) & (version_parent = null);'
        case 'name like':
            query_search = f'where (name ~*"{title}"*) & (category = ({",".join([str(i) for i in cats])})) & (version_parent = null);'
        case _:
            # default to name equals instead of raising exception
            print('Incorrect value for parameter "search_type" provided. Defaulting to "name equals"...')
            query_search = f'where (name = "{title}") & (category = (0,1,2,8,9,10,11)) & (version_parent = null);'

    query = query_fields + query_search

    # sorting criteria
    if sort_results and search_type != 'search':
        query_sort = f"sort {sort_by};"
        query += query_sort
    else:
        # using search and sort keywords result in bad request errors
        pass

    query_limit = f'limit {limit};'
    query_offset = f'offset {offset};'
    query += query_limit + query_offset
    # encode result to avoid encoding errors
    return query.encode('utf-8')


def post_request(query: str, twitch_client_id: str, access_token: str, endpoint: str = 'games') -> Response | None:
    """Sends request to IGDB for data based on the endpoint provided, and content of the query \n
    :param query: query encoded as a byte-string
    :param endpoint: the endpoint to pull data from. For now, we will only use 'games'
    :returns DB response as a json"""
    base_igdb_url = "https://api.igdb.com/v4"
    url = base_igdb_url + "/" + f"{endpoint}"

    headers = {'headers': {'Client-ID': twitch_client_id,
                           'Authorization': f"Bearer {access_token}"},
               'data': query}

    response = requests.post(url, **headers)

    if response is None:
        return None
    else:
        return response


def validate_response(response: Response, title: str, exact_matches_only: bool = True) -> dict | list | None:
    data = response.json()
    num_results = len(data)

    if num_results == 0:
        # null response
        return None

    elif num_results == 1:
        body = data[0]
        name = body.get('name')

        if exact_matches_only and title == name:
            return body
        elif exact_matches_only and title != name:
            return None
        elif not exact_matches_only:
            return body

    elif num_results > 1:
        responses = []
        for i in range(num_results):
            try:
                body = data[i]
            except KeyError:
                continue
            name = body.get('name')
            if exact_matches_only and title == name:
                responses.append(body)
            elif exact_matches_only and title != name:
                pass
            elif not exact_matches_only:
                responses.append(response)
        if not exact_matches_only:
            if responses is not None:
                return responses
            else:
                return None


def parse_response(response) -> List[dict] | dict | None:
    # some gnarly code to extract values from the json data for games
    if isinstance(response, dict):
        # result has 1 element
        body = response
        result = {"id": body.get('id'),
                  "release_dates": body.get('release_dates', None)[0].get('y', None),
                  "name": body.get('name'),
                  "category": categories[body.get('category', None)] if 'category' in body else None,
                  "slug": body.get('slug'),
                  "platforms": [i['name'] for i in body.get('platforms')] if 'platforms' in body else None,
                  "genres": [i['name'] for i in body.get('genres')] if 'genres' in body else None,
                  "tags": [str(i) for i in body.get('tags')] if 'tags' in body else None,
                  "age_ratings": [age_ratings[i.get('rating')] for i in
                                  body['age_ratings']] if 'age_ratings' in body else None,
                  "rating": body.get('rating', None),
                  "rating_count": body.get('rating_count', 0),
                  "similar_games": [i['name'] for i in body.get('similar_games')] if 'similar_games' in body else None,
                  "themes": [i['name'] for i in body.get('themes')] if 'themes' in body else None,
                  "summary": body.get('summary'),
                  "involved_companies": [i['company']['name'] for i in
                                         body['involved_companies']] if 'involved_companies' in body else None
                  }
        return result

    elif isinstance(response, list):
        responses = []
        for i in range(len(response.json())):
            data = response.json()
            body: dict = data[i]
            result = {"id": body.get('id'),
                      "release_dates": body.get('release_dates')[0].get('y'),
                      "name": body.get('name'),
                      "category": categories[body['category']] if 'category' in body else None,
                      "slug": body.get('slug'),
                      "platforms": [i['name'] for i in body['platforms']] if 'platforms' in body else None,
                      "genres": [i['name'] for i in body['genres']] if 'genres' in body else None,
                      "tags": [str(i) for i in body['tags']] if 'tags' in body else None,
                      "age_ratings": [age_ratings[i['rating']] for i in
                                      body['age_ratings']] if 'age_ratings' in body else None,
                      "rating": body.get('rating', None),
                      "rating_count": body.get('rating_count', 0),
                      "similar_games": [i['name'] for i in body['similar_games']] if 'similar_games' in body else None,
                      "themes": [i['name'] for i in body['themes']] if 'themes' in body else None,
                      "summary": body.get('summary'),
                      "involved_companies": [i['company']['name'] for i in
                                             body['involved_companies']] if 'involved_companies' in body else None
                      }

            responses.append(result)
        return responses



