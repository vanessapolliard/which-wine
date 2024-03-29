import numpy as np
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def connect():
    conn = psycopg2.connect(database="whichwine",
                        user="postgres",
                        host="18.217.219.106", port="5432")
    cur = conn.cursor()
    return conn, cur


def insert_into_db(conn, cur, insert_vals):
    try:
        insert_query = "INSERT INTO similarities VALUES \
                    (%s, %s)"
        cur.execute(insert_query, tuple(insert_vals))
        conn.commit()
    except Exception as e:
        print(e)
        print(insert_query % tuple(insert_vals))
        
# save distance matrix to postgres DB
def save_similarities(conn, cur, dist_matrix):
    for idx, wine_dists in enumerate(dist_matrix):
        wine_id = idx
        similar_wines = np.argsort(wine_dists)[1:50]
        similar_wines = similar_wines.tolist()
        insert_vals = [wine_id, similar_wines]
        insert_into_db(conn, cur, insert_vals)

def close_connection(conn):
    conn.close()

# use SQL alchemy to insert full df as table to postgres
# used for wine metadata table and wine topic loadings table
def alchemy_insert(df, table_name): 
    engine = create_engine('postgresql+psycopg2://postgres:@18.219.179.32/whichwine') 
    df.to_sql(table_name, engine, if_exists = 'append', index = False) # need to drop table if reloading


if __name__ == '__main__':
    # conn, cur = connect()
    # save_similarities(conn, cur, dists)
    # close_connection()
    pass

    # create postgres tables
    # CREATE TABLE similarities (wine_id integer PRIMARY KEY, similar_wines TEXT []);
    # CREATE TABLE topicloadings (
    #           wine_id integer PRIMARY KEY, 
    #           topic0 numeric,
    #           topic1 numeric,
    #           topic2 numeric,
    #           topic3 numeric,
    #           topic4 numeric,
    #           topic5 numeric,
    #           topic6 numeric,
    #           price numeric,
    #           red numeric,
    #           rose numeric,
    #           sparkling numeric,
    #           white numeric
    #           );
    # CREATE TABLE winemetadata (
    #           wine_id integer PRIMARY KEY, 
    #           country TEXT,
    #           description TEXT,
    #           points numeric,
    #           price numeric,
    #           province TEXT,
    #           title TEXT,
    #           variety TEXT,
    #           winery TEXT,
    #           vintage numeric,
    #           category TEXT
    #           );