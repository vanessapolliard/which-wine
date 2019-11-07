import numpy as np
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

def connect():
    conn = psycopg2.connect(database="whichwine",
                        user="postgres",
                        host="18.219.179.32", port="5432")
    cur = conn.cursor()
    return conn, cur

def insert_into_db(conn, cur, insert_vals):
    # similarities or similarwines
    try:
        insert_query = "INSERT INTO similarities VALUES \
                    (%s, %s)"
        cur.execute(insert_query, tuple(insert_vals))
        conn.commit()
    except Exception as e:
        print(e)
        print(insert_query % tuple(insert_vals))
        

def save_similarities(conn, cur, dist_matrix):
    for idx, wine_dists in enumerate(dist_matrix):
        wine_id = idx
        similar_wines = np.argsort(wine_dists)[1:50]
        similar_wines = similar_wines.tolist()
        insert_vals = [wine_id, similar_wines]
        insert_into_db(conn, cur, insert_vals)


def save_theta(conn, cur, theta_matrix):
    for idx, wine in enumerate(theta_matrix):
        insert_vals = []
        insert_vals.append(idx)

        insert_query = "INSERT INTO topicloadings VALUES \
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cur.execute(insert_query, tuple(insert_vals))
        conn.commit()



def close_connection(conn):
    conn.close()

def alchemy_insert(df):
    engine = create_engine('postgresql+psycopg2://postgres:@18.219.179.32/whichwine')
    df.to_sql('topicloadings', engine)



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
    #           topic7 numeric,
    #           price numeric,
    #           red numeric,
    #           rose numeric,
    #           sparkling numeric,
    #           white numeric
    #           );