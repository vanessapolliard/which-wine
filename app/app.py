import os
import pickle
import psycopg2

from flask import Flask, render_template, jsonify, request, redirect, url_for

# FILE_DIRECTORY = os.path.split(os.path.realpath(__file__))[0]
# DATA_DIRECTORY = os.path.join(FILE_DIRECTORY, 'data')

app = Flask(__name__)

conn = psycopg2.connect(database="whichwine",
                        user="postgres",
                        host="18.219.179.32", port="5432")
cur = conn.cursor()

def get_db_data():
    select_query = "SELECT wine_id, similar_wines FROM similarities limit 5;"
    cur.execute(select_query)
    data = cur.fetchall()
    return data

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
    data = get_db_data()
    #data = get_data_placeholder()
    return render_template('index.html', data=data)

# find similar wines
@app.route('/findsimilarwines')
def find_similar_wines():
    data = get_data_placeholder()
    return render_template('findsimilarwines.html', data=data)

# similar wines results
@app.route('/similarwines')
def similar_wines():
    data = get_data_placeholder()
    return render_template('similarresults.html', data=data)

# take the wine quiz
@app.route('/winequiz')
def wine_quiz():
    data = get_data_placeholder()
    return render_template('winequiz.html', data=data)

# quiz results page
@app.route('/quizresults')
def results():
    data = get_data_placeholder()
    return render_template('quizresults.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=True, debug=False) # Make sure to change debug=False for production
