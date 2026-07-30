import pandas as pd
from pytrends.request import TrendReq
from datetime import datetime
import time

from db.postgres import (
    fetch_dataframe,
    insert_dataframe
)
#set up language and tz=330 is minutes offset to get +5:30 hrs as Indian standard time
pytrends = TrendReq(
    hl="en-US",
    tz=330
)

def get_keywords():

    query = """
    SELECT keyword_id,
           keyword,
           category
    FROM keywords
    """

    df = fetch_dataframe(query)

    df["keyword_id"] = (
        df["keyword_id"]
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
    )

    return df

#This func extracts all the states and their interests for the keyword in past 30 days (not sorted by interest values but name)
def get_interest_by_region(keyword):

    pytrends.build_payload(
        kw_list=[keyword],
        cat=0,
        timeframe='today 1-m',
        geo='IN',
        gprop=''
    )

    df = pytrends.interest_by_region(
        resolution='REGION',
        inc_low_vol=True,
        inc_geo_code=False
    )

    return df

#this function is responsible for shortlisting the top 3 or less states having interest >=90%
#here by = keyword because the keyword itself is the column name and interest are listed under it
def get_top_states(keyword):

    df = get_interest_by_region(keyword)

    df = df.sort_values(
        by=keyword,
        ascending=False
    )

    df = df.reset_index()

    df = df[
        df[keyword] >= 90
    ]

    df = df.head(3)

    return df

def run_pytrends_pipeline():

    keywords_df = get_keywords()

    records = []
    run_timestamp = datetime.now()

    for _, row in keywords_df.iterrows():

        keyword_id = row["keyword_id"]
        keyword = row["keyword"]
        
        try:
            states_df = get_top_states(keyword)
            time.sleep(3)

        except Exception as e:
            print(f"Error for {keyword}: {e}")
            time.sleep(10)
            continue
        
        if states_df.empty:
            print(f"No high-interest states found for {keyword}")
            continue

        for _, state_row in states_df.iterrows():

            records.append({
            "run_timestamp": run_timestamp,
            "keyword_id": keyword_id,
            "keyword": keyword,
            "states": state_row["geoName"],
            "interest_score": state_row[keyword]
        })

    final_df = pd.DataFrame(records)

    print(final_df)

    insert_dataframe(
    final_df,
    "fact_keyword_state"
    )

    print("fact_keyword_state populated successfully.")

    return final_df


if __name__ == "__main__":
    run_pytrends_pipeline()