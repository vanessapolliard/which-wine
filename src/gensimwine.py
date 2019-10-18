from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_distances
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem.wordnet import WordNetLemmatizer
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from cleaning import Cleaning
import multiprocessing as mp
from pprint import pprint
import gensim.corpora as corpora
import pandas as pd
import numpy as np
import gensim
import time
import re


def lemmatize_stemming(text):
    return WordNetLemmatizer().lemmatize(text, pos='v')


def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        stem = lemmatize_stemming(token)
        if stem not in stop_words and len(stem) > 3:
            result.append(stem)
    return result


def create_theta_matrix(theta_array, num_topics):
    new_df = pd.DataFrame(0, index=range(0, len(theta_array)),
                          columns=range(0, num_topics))
    for idx, row in enumerate(theta_array):
        for tuple_val in row:
            new_df[idx, tuple_val[0]] = tuple_val[1]
    return new_df


# duplicate of above function except called using pool multithreading
def create_theta_matrix2(idx, row):
    for tuple_val in row:
        new_df[idx, tuple_val[0]] = tuple_val[1]
    return new_df


# find all words in the documents
def all_words(phi):
    words = []
    for idx in range(phi.shape[1]):
        words.append(id2word[idx])
    return words


if __name__ == '__main__':
    raw_data = '../data/winemag-data-190314.csv'
    num_topics = 7
    additional_stop = ['wine', 'flavor', 'aromas', 'finish',
                       'palate', 'note', 'nose', 'drink',
                       'fruit', 'like']

    # Get clean data descriptions
    cleaning = Cleaning(raw_data)
    cleaning.CreateDataFrame()
    cleaning.CleanDataFrame()
    desc = cleaning.cleansed_data

    # add to stop words
    stop_words = list(gensim.parsing.preprocessing.STOPWORDS)
    for val in additional_stop:
        stop_words.append(val)
    stop_words = frozenset(stop_words)

    # featurize the data
    processed_docs = desc.map(preprocess)
    print('Data featurized')

    # create dictionary
    id2word = gensim.corpora.Dictionary(processed_docs)

    # create corpus
    texts = processed_docs

    # create Term Frequency
    bow_corpus = [id2word.doc2bow(text) for text in texts]

    # run gensim LDA model
    start = time.time()
    lda_model = gensim.models.LdaMulticore(bow_corpus,
                                           num_topics=num_topics,
                                           id2word=id2word,
                                           passes=3,
                                           workers=35)
    stop = time.time()
    print('Model created in ', stop-start)
    lda_model.save('finalmodel')
    # lda_model = gensim.models.LdaModel.load('../models/maybetheone')

    # show terms in topics
    pprint(lda_model.print_topics())

    # get phi matrix for wordcloud
    phi = lda_model.get_topics()
    words = all_words(phi)
    cloud_df = pd.DataFrame(phi, columns=words)

    # document vs topic list of lists of tuples
    theta = [lda_model.get_document_topics(item)
             for item in bow_corpus[:50000]]
    print('Theta array created')

    # create theta matrix
    # create new dataframe of shape observations by topics
    new_df = pd.DataFrame(0, index=range(0, len(theta)),
                          columns=range(0, num_topics))
    pool = mp.Pool(mp.cpu_count())
    start2 = time.time()
    print('Theta matrix creation start time: ', start2)
    theta_matrix = pool.starmap(create_theta_matrix2, [(idx, row)
                                for idx, row in enumerate(theta)])
    stop2 = time.time()
    pool.close()
    print('Matrix created in ', stop2-start2, ' seconds')
