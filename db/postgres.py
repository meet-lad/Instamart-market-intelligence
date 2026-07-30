import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

#now for the database connection
def get_engine():

    connection_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(connection_string)

    return engine

def fetch_dataframe(query):

    engine = get_engine()
#we are calling engine here because for reading the sql we need to first establish the connection
#so pandas will know which database to query
    df = pd.read_sql(query, engine)

    return df

def execute_query(query):

    engine = get_engine()

    with engine.connect() as connection:

        connection.execute(text(query))

        connection.commit()

def insert_dataframe(df, table_name):

    engine = get_engine()

    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False
    )

