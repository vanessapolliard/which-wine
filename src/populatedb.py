import numpy as np
import pandas as pd
import psycopg2

def connect():
    conn = psycopg2.connect(database="whichwine",
                        user="postgres",
                        host="18.219.179.32", port="5432")
    cur = conn.cursor()
    return conn, cur

def insert_into_db(conn, cur, wine_id, similar_wines):
    insert_vals = [wine_id, similar_wines]
    insert_query = "INSERT INTO similarwines VALUES \
                    (%s, %s)"
    cur.execute(insert_query, tuple(insert_vals))
    conn.commit()

def save_similarities(conn, cur, dist_matrix):
    for idx, wine_dists in enumerate(dist_matrix):
        wine_id = idx
        similar_wines = np.argsort(wine_dists)[1:50]
        insert_into_db(conn, cur, wine_id, list(similar_wines))

def close_connection(conn):
    conn.close()


if __name__ == '__main__':
    # connect()
    # save_similarities(conn, cur, dists)
    # close_connection()
    pass