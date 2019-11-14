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

price_ranges = ['$5-$15','$15-$25','$25-$50','$50-$75','$75-$100','$100+']
topic_words = {0:'apple',1:'blackberry',2:'peach',3:'cherry',4:'pepper',5:'wood',6:'vanilla'}

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

def get_quizresults(category, price_low, price_high, topicthresh):
    top_topic = topicthresh.index(max(topicthresh))
    orderby = 'topic' +  str(top_topic)

    topic_query = " "
    for idx, thresh in enumerate(topicthresh):
        if thresh > 0:
            topic_query = topic_query + " and topic" + str(idx) + " > " + str(thresh) 
    print(topic_query)       

    vals = [price_low, price_high]

    select_query = "SELECT title, variety, price, points FROM winemetadata where wine_id = ANY ( \
                    select wine_id from topicloadings_price \
                    where " + category + " = 0.5 and real_price between %s and %s" + topic_query + "order by " + orderby + " DESC limit 10);"

    # vals = [price_low, price_high, topicthresh[0], topicthresh[1], topicthresh[2],
    #         topicthresh[3], topicthresh[4], topicthresh[5], topicthresh[6]]
    # select_query = "SELECT title, variety, price, points FROM winemetadata where wine_id = ANY ( \
    #                 select wine_id from topicloadings_price \
    #                 where " + category + " = 0.5 and real_price between %s and %s \
    #                 and topic0 > %s and topic1 > %s and topic2 > %s and topic3 %s \
    #                 and topic4 %s and topic5 %s and topic6 %s  \
    #                 order by " + orderby + " DESC);"
    cur.execute(select_query, tuple(vals))
    data = cur.fetchall()
    return data

# home page
@app.route('/')
def index():
    return render_template('index.html')

# WORKFLOW 1
# find similar wines
@app.route('/findsimilarwines')
def find_similar_wines():
    df = load_metadata()
    return render_template('findsimilarwines.html', df=df)

# get dropdown vals
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

# get dropdown vals
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

# get dropdown vals
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



# WORKFLOW 2
# take the wine quiz
@app.route('/winequiz')
def wine_quiz():
    df = load_metadata()
    return render_template('winequiz.html', df=df, prices=price_ranges)

# quiz results page
@app.route('/quizresults', methods=['GET','POST'])
def results():
    category = request.form['category']

    # Price
    price_range = request.form['price']
    if price_range == price_ranges[0]:
        price_low = 5
        price_high = 15
    elif price_range == price_ranges[1]:
        price_low = 15
        price_high = 25
    elif price_range == price_ranges[2]:
        price_low = 25
        price_high = 50
    elif price_range == price_ranges[3]:
        price_low = 50
        price_high = 75
    elif price_range == price_ranges[4]:
        price_low = 75
        price_high = 100
    else:
        price_low = 100
        price_high = 5000

    # Topics
    topics = [0 for x in range(0,7)]
    print(request.args.get(0))
    if request.form.get("apple"):
        topics[0] = 1
    if request.form.get("blackberry"):
        topics[1] = 1
    if request.form.get("peach"):
        topics[2] = 1
    if request.form.get("cherry"):
        topics[3] = 1
    if request.form.get("pepper"):
        topics[4] = 1
    if request.form.get("wood"):
        topics[5] = 1
    if request.form.get("vanilla"):
        topics[6] = 1

    topicthresh = [0 for x in range(0,7)]
    if category in ('red','white'):
        cutoffs = {1: 0.8, 2: 0.3, 3: 0.2, 4: 0.2, 5: 0.15, 6: 0.1, 7: 0.1}
    elif category in ('sparkling','rose'):
        cutoffs = {1: 0.3, 2: 0.1, 3: 0.1, 4: 0, 5: 0, 6: 0, 7: 0}

    cutoff = cutoffs[sum(topics)] # 0.2
    if request.form.get("apple"):
        topicthresh[0] = cutoff
    if request.form.get("blackberry"):
        topicthresh[1] = cutoff
    if request.form.get("peach"):
        topicthresh[2] = cutoff
    if request.form.get("cherry"):
        topicthresh[3] = cutoff
    if request.form.get("pepper"):
        topicthresh[4] = cutoff
    if request.form.get("wood"):
        topicthresh[5] = cutoff
    if request.form.get("vanilla"):
        topicthresh[6] = cutoff

    data = get_quizresults(category, price_low, price_high, topicthresh)
    return render_template('quizresults.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, threaded=False, debug=False) # Make sure to change debug=False for production
