import pandas as pd

from db.postgres import fetch_dataframe

from utils.location_utils import (
    get_city_limit,
    get_top_cities
)

def get_keyword_states():

    query = """
    SELECT
        keyword_id,
        keyword,
        states,
        interest_score
    FROM vw_latest_keyword_state
    """

    return fetch_dataframe(query)

def get_search_queue():

    keyword_df = get_keyword_states()

    records = []

    for _, row in keyword_df.iterrows():

        limit = get_city_limit(
            row["interest_score"]
        )

        cities_df = get_top_cities(
            row["states"],
            limit
        )

        for _, city_row in cities_df.iterrows():

            records.append({

                "keyword_id":
                    row["keyword_id"],

                "keyword":
                    row["keyword"],

                "states":
                    row["states"],

                "interest_score":
                    row["interest_score"],

                "city":
                    city_row["city"],

                "area":
                    city_row["area"],

                "instamart_stores":
                    city_row["instamart_stores"]
            })

    return pd.DataFrame(records)

def build_city_selection_df():

    keyword_states_df = get_keyword_states()

    records = []

    for _, row in keyword_states_df.iterrows():

        keyword_id = row["keyword_id"]
        keyword = row["keyword"]
        state = row["states"]
        interest_score = row["interest_score"]

        limit = get_city_limit(interest_score)

        cities_df = get_top_cities(
            state,
            limit
        )

        for _, city_row in cities_df.iterrows():

            records.append({
                "keyword_id": keyword_id,
                "keyword": keyword,
                "states": state,
                "interest_score": interest_score,
                "city": city_row["city"],
                "area": city_row["area"],
                "instamart_stores": city_row["instamart_stores"]
            })

    return pd.DataFrame(records)

if __name__ == "__main__":

    df = get_search_queue()

    print(df.head(20))
    print(df.shape)

