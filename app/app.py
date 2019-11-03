import os
import pickle

from flask import Flask, render_template, jsonify, request, redirect, url_for
import psycopg2

# FILE_DIRECTORY = os.path.split(os.path.realpath(__file__))[0]
# DATA_DIRECTORY = os.path.join(FILE_DIRECTORY, 'data')

app = Flask(__name__)

# conn = psycopg2.connect(database="fraud",
#                         user="postgres",
#                         host="localhost", port="5435")
# cur = conn.cursor()

# def get_db_data():
#     select_query = "SELECT * FROM fraudstream"
#     cur.execute(select_query)
#     data = cur.fetchall()
#     return data
def get_data_placeholder():
    data = [[12345, 0.986],[12346, 0.034]]
    return data

# with open(os.path.join(DATA_DIRECTORY, 'user_recommendations.pkl'), 'rb') as f:
#     user_recommendations = pickle.load(f)

# with open(os.path.join(DATA_DIRECTORY, 'user_fave_movies.pkl'), 'rb') as f:
#     user_favorites = pickle.load(f)

# home page
@app.route('/')
def index():
    #data = get_db_data()
    data = get_data_placeholder()
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False) # Make sure to change debug=False for production
