from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_distances
from sklearn.feature_extraction import stop_words
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.decomposition import NMF
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import time
import re

def tokenize(doc):
    wordnet = WordNetLemmatizer()
    return [wordnet.lemmatize(word) for word in word_tokenize(doc.lower())]

def find_top_words(matrix):
    words = {}
    for idx, __ in enumerate(matrix):
        top_words = np.argsort(matrix[idx])[-10:][::-1]
        top_words = tf_feature_names[top_words]
        words[idx] = top_words
    return words

def find_similar_wines(wine_title):
    wine_idx = df[df['title'] == wine_title].index[0]
    dists = cosine_distances(W, W)
    top_wines = np.argsort(dists[wine_idx,:])[-10:][::1]
    #top_wines = df.title[top_wines]
    top_wines = df.loc[top_wines][['title','description','variety']]
    return top_wines[1:]

if __name__ == '__main__':
    raw_data = '../data/winemag-data-190314.csv'
    wine_title = 'Quinta dos Avidagos 2011 Avidagos Red (Douro)'

    df = pd.read_csv(raw_data)
    df.drop(labels='Unnamed: 0',axis=1,inplace=True)
    desc = df.description
    desc = desc.str.lower()
    desc = desc.str.replace('[^a-zA-Z0-9 \n\.]', ' ')
    desc = desc.str.replace('\d', ' ')
    desc = desc.str.replace('.', ' ')
    print('Data cleaned')

    stop = list(stop_words.ENGLISH_STOP_WORDS)
    additional_stop = ['ha', 'le', 'u', 'wa','s','t','s','r','ro','wine','flavor','aromas','finish', 'palate', 'note', 'nose', 'drink', 'ofcut', 'feeeling']
    for val in additional_stop:
        stop.append(val)
    stop = frozenset(stop)
    tf_vect = TfidfVectorizer(stop_words=stop,tokenizer=tokenize)
    tf = tf_vect.fit_transform(desc)
    words = tf_vect.get_feature_names()
    tf_feature_names = np.array(words)
    print('Data featurized')

    start = time.time()
    nmf = NMF(n_components = 10)
    nmf.fit(tf)
    W = nmf.transform(tf)
    H = nmf.components_
    stop = time.time()
    print('Model created in ', stop-start)
    
    topic_words = find_top_words(H)
    print(topic_words)

    find_similar_wines(wine_title)