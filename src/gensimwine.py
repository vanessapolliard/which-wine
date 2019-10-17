from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_distances
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
import numpy as np
import time
import re
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
import gensim.corpora as corpora
from gensim.models import CoherenceModel
from pprint import pprint
import multiprocessing as mp


def lemmatize_stemming(text):
    return WordNetLemmatizer().lemmatize(text, pos='v')

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        stem = lemmatize_stemming(token)
        if stem not in stop_words and len(stem) > 3:
            result.append(stem)
    return result

def create_theta_matrix(theta_array,num_topics):
    #create new dataframe of shape observations by topics
    new_df = pd.DataFrame(0, index=range(0,len(theta_array)), columns=range(0,num_topics))
    for idx, row in enumerate(theta_array):
        for tuple_val in row:
            new_df[idx,tuple_val[0]] = tuple_val[1]
    return new_df

    def create_theta_matrix2(idx,row):
    #create new dataframe of shape observations by topics
    for tuple_val in row:
        new_df[idx,tuple_val[0]] = tuple_val[1]
    return new_df

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

    additional_stop = ['wine','flavor','aromas','finish', 'palate', 'note', 'nose', 'drink', 'fruit', 'like']
    stop_words = list(gensim.parsing.preprocessing.STOPWORDS)
    for val in additional_stop:
        stop_words.append(val)
    stop_words = frozenset(stop_words)

    processed_docs = desc.map(preprocess)
    print('Data featurized')

    #create dictionary
    id2word = gensim.corpora.Dictionary(processed_docs)

    #create corpus
    texts = processed_docs

    #Term Document Frequency
    bow_corpus = [id2word.doc2bow(text) for text in texts]

    start = time.time()
    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=7, id2word=id2word, passes=2, workers=35)
    stop = time.time()
    print('Model created in ', stop-start)
    lda_model.save('model1')

    pprint(lda_model.print_topics())

    # document vs topic list of lists of tuples
    theta = [lda_model.get_document_topics(item) for item in bow_corpus]

    # create non-sparse theta matrix
    new_df = pd.DataFrame(0, index=range(0,len(theta_array)), columns=range(0,num_topics))
    pool = mp.Pool(mp.cpu_count())
    theta_matrix = pool.starmap(create_theta_matrix2, [(idx, row) for idx, row in enumerate(theta_array)])
    pool.close()