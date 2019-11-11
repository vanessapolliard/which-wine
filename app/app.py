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

def get_db_data():
    select_query = "SELECT wine_id, similar_wines FROM similarities limit 5;"
    cur.execute(select_query)
    data = cur.fetchall()
    return data

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

# SELECT title, variety, price, points FROM winemetadata where wine_id = ANY ((select similar_wines[:5] from similarities where wine_id = (select wine_id from winemetadata where title = 'Rainstorm 2013 Pinot Gris (Willamette Valley)'))::int[]);

# home page
@app.route('/')
def index():
    data = get_db_data()
    return render_template('index.html', data=data)

# find similar wines
@app.route('/findsimilarwines')
def find_similar_wines():
    df = pd.DataFrame(get_lookup_data())
    return render_template('findsimilarwines.html', df=df)

@app.route('/get_varietals')
def get_varietals():
    df = pd.DataFrame(get_lookup_data())
    category = request.args.get('category')
    if category:
        sub_df = df[df[1] == category]
        sub_df.sort_values(by=2,inplace=True)
        data = set(sub_df[2])
        data = [{"value": x} for x in sorted(data)]
    return jsonify(data)

@app.route('/get_wineries')
def get_wineries():
    df = pd.DataFrame(get_lookup_data())
    category = request.args.get('category')
    varietal = request.args.get('varietal')
    if category:
        sub_df = df[(df[1] == category) & (df[2] == varietal)]
        sub_df.sort_values(by=3,inplace=True)
        data = set(sub_df[3])
        data = [{"value": x} for x in sorted(data)]
    return jsonify(data)

@app.route('/get_wines')
def get_wines():
    df = pd.DataFrame(get_lookup_data())
    category = request.args.get('category')
    varietal = request.args.get('varietal')
    winery = request.args.get('winery')
    if category:
        sub_df = df[(df[1] == category) & (df[2] == varietal) & (df[3] == winery)]
        sub_df.sort_values(by=0,inplace=True)
        data = set(sub_df[0])
        data = [{"value": x} for x in sorted(data)]
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
    data = get_data_placeholder()
    return render_template('winequiz.html', data=data)

# quiz results page
@app.route('/quizresults')
def results():
    data = get_data_placeholder()
    return render_template('quizresults.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=False, debug=False) # Make sure to change debug=False for production
