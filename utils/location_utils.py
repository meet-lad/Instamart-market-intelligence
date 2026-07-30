from db.postgres import fetch_dataframe


def get_city_limit(interest_score):

    if interest_score >= 98:
        return 3
    elif interest_score >= 92:
        return 2
    else:
        return 1


def get_top_cities(state, limit):

    query = f"""
    SELECT
        city,
        area,
        instamart_stores
    FROM vw_top_instamart_cities
    WHERE states = '{state}'
    ORDER BY instamart_stores DESC
    LIMIT {limit}
    """

    return fetch_dataframe(query)