from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_distances
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import time
import re

def tokenize(doc):
    '''
    INPUT: string
    OUTPUT: list of strings

    Tokenize and stem/lemmatize the document.
    '''
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
    dists = cosine_distances(theta, theta)
    top_wines = np.argsort(dists[wine_idx,:])[-10:][::1]
    top_wines = df.title[top_wines]
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

    #stop = stop.append(['ha', 'le', 'u', 'wa','s','t','s','r','ro'])
    countvect = CountVectorizer(stop_words='english', tokenizer=tokenize)
    count_vectorized = countvect.fit_transform(desc)
    words = countvect.get_feature_names()
    tf_feature_names = np.array(words)
    print('Data featurized')

    start = time.time()
    lda = LatentDirichletAllocation(n_components=10, max_iter=5, learning_method='online',random_state=0, n_jobs=-1)
    lda.fit(count_vectorized)
    stop = time.time()
    components = lda.components_
    theta = lda.transform(count_vectorized)
    print('Model created in ', stop-start)
    
    top_words_in_topic = find_top_words(components)
    print(top_words_in_topic)

    #find_similar_wines(wine_title)