import os
import pickle
import psycopg2
import pandas as pd

from flask import Flask, render_template, jsonify, request, redirect, url_for

# FILE_DIRECTORY = os.path.split(os.path.realpath(__file__))[0]
# DATA_DIRECTORY = os.path.join(FILE_DIRECTORY, 'data')

app = Flask(__name__)

conn = psycopg2.connect(database="whichwine",
                        user="postgres",
                        host="18.217.219.106", port="5432")
cur = conn.cursor()

def load_metadata():
    with open('../data/winemetadata.pkl','rb') as f:
        df = pickle.load(f)
    return df
# OR
def get_lookup_data():
    select_query = "SELECT title, category, variety, winery FROM winemetadata;"
    cur.execute(select_query)
    df = cur.fetchall()
    return df

def get_results(wine, num_recs):
    vals = [num_recs, wine]
    select_query = "SELECT title, variety, price, points FROM winemetadata where wine_id = ANY ((select similar_wines[:%s] from similarities where wine_id = (select wine_id from winemetadata where title = %s))::int[]);"
    cur.execute(select_query, tuple(vals))
    data = cur.fetchall()
    return data

# home page
@app.route('/')
def index():
    return render_template('index.html')

# find similar wines
@app.route('/findsimilarwines')
def find_similar_wines():
    df = load_metadata()
    return render_template('findsimilarwines.html', df=df)

@app.route('/get_varietals')
def get_varietals():
    df = load_metadata()
    category = request.args.get('category')
    if category:
        sub_df = df[df['category'] == category]
        sub_df.sort_values(by='category',inplace=True)
        data = set(sub_df['variety'])
        data = [{"value": x} for x in sorted(data)]
        default = {"value": "Select a varietal..."}
        data.insert(0, default)
    return jsonify(data)

@app.route('/get_wineries')
def get_wineries():
    df = load_metadata()
    category = request.args.get('category')
    varietal = request.args.get('varietal')
    if varietal:
        sub_df = df[(df['category'] == category) & (df['variety'] == varietal)]
        sub_df.sort_values(by='winery',inplace=True)
        data = set(sub_df['winery'])
        data = [{"value": x} for x in sorted(data)]
        default = {"value": "Select a winery..."}
        data.insert(0, default)
    return jsonify(data)

@app.route('/get_wines')
def get_wines():
    df = load_metadata()
    category = request.args.get('category')
    varietal = request.args.get('varietal')
    winery = request.args.get('winery')
    if winery:
        sub_df = df[(df['category'] == category) & (df['variety'] == varietal) & (df['winery'] == winery)]
        sub_df.sort_values(by='title',inplace=True)
        data = set(sub_df['title'])
        data = [{"value": x} for x in sorted(data)]
        default = {"value": "Select a wine..."}
        data.insert(0, default)
    return jsonify(data)

# similar wines results
@app.route('/similarwines', methods=['GET','POST'])
def similar_wines():
    wine = request.form['wine']
    num_recs = request.form['num_recs']
    data = get_results(wine, num_recs)
    return render_template('similarresults.html', data=data)





# take the wine quiz
@app.route('/winequiz')
def wine_quiz():
    return render_template('winequiz.html')

# quiz results page
@app.route('/quizresults')
def results():
    return render_template('quizresults.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=False, debug=False) # Make sure to change debug=False for production
