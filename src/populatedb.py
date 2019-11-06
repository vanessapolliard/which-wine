import numpy as np
import pandas as pd
import psycopg2

conn = psycopg2.connect(database="whichwine",
                        user="postgres",
                        host="18.219.179.32", port="5435")
cur = conn.cursor()

def insert_into_db(wine_id, similar_wines):
    insert_vals = [wine_id, similar_wines]
    insert_query = "INSERT INTO similarwines VALUES \
                    (%s, %s)"
    cur.execute(insert_query, tuple(insert_vals))
    conn.commit()

def save_similarities(dist_matrix):
    for idx, wine_dists in enumerate(dist_matrix):
        wine_id = idx
        similar_wines = np.argsort(wine_dists)[1:50]
        insert_into_db(wine_id, similar_wines)


if __name__ == '__main__':
    # save_similarities(dists)
    # conn.close()
    pass