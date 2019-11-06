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
from pprint import pprint
import gensim.corpora as corpora
import multiprocessing as mp
import pandas as pd
import numpy as np
import gensim
import time
import re
from sklearn.preprocessing import MinMaxScaler


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
            new_df.loc[idx, tuple_val[0]] = tuple_val[1]
    return new_df


# find all words in the documents
def all_words(phi):
    words = []
    for idx in range(phi.shape[1]):
        words.append(id2word[idx])
    return words


def find_similar_wines(wine_title, dists, df):
    wine_idx = df[df['title'] == wine_title].index[0]
    top_wines = np.argsort(dists[wine_idx, :])[:10] #taking first 10 because this is cosine distance, not similarity
    top_wines = df.loc[top_wines][['title', 'variety', 'category', 'price']]
    return top_wines


if __name__ == '__main__':
    # raw_data = '../data/winemag-data-190314.csv'
    raw_data = '../data/winemag_data_inclcategory.csv' # includes category - red, white, etc
    year_cutoff = 2009.0
    num_topics = 7
    price_weight = 0.1
    category_weight = 0.5
    additional_stop = ['wine', 'flavor', 'aromas', 'finish',
                       'palate', 'note', 'nose', 'drink',
                       'fruit', 'like']

    # Get clean data descriptions
    cleaning = Cleaning(raw_data)
    cleaning.CreateDataFrame()
    cleaning.CleanDataFrame()
    desc = cleaning.cleansed_data
    df = cleaning.processed_data

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

    # # run gensim LDA model
    # start = time.time()
    # lda_model = gensim.models.LdaMulticore(bow_corpus,
    #                                        num_topics=num_topics,
    #                                        id2word=id2word,
    #                                        passes=3,
    #                                        workers=35)
    # print('Model created in ', time.time()-start)
    # lda_model.save('finalmodel')
    lda_model = gensim.models.LdaModel.load('../models/finalmodel')

    # show terms in topics
    pprint(lda_model.print_topics())

    # get phi matrix for wordcloud
    # phi = lda_model.get_topics()
    # words = all_words(phi)
    # cloud_df = pd.DataFrame(phi, columns=words)

    # TODO
    # limit theta matrix based on price
    df_full = pd.read_csv(raw_data,index_col=0)
    df_sub = df_full['vintage']
    good_idx = df_full['vintage'] > year_cutoff
    bow_corpus = [bow_corpus[idx] for idx, i in enumerate(good_idx) if i == True]

    # document vs topic list of lists of tuples
    theta = [lda_model.get_document_topics(item)
             for item in bow_corpus]
             # for item in bow_corpus[:50000]] # limit to 50000 data points
    print('Theta array created')

    # create theta matrix
    start2 = time.time()
    theta_matrix = create_theta_matrix(theta, num_topics)
    print('Matrix created in ', time.time()-start2, ' seconds')

    # create lookup table
    df_lookup = df_full[df_full['vintage'] > year_cutoff]
    df_lookup.dropna(axis = 0, subset = ['price','category'],inplace=True) 
    df_lookup.reset_index(inplace=True)

    # add price & category to wine vectors
    theta_matrix['category'] = df_lookup['category']
    theta_matrix['price'] = df_lookup['price']
    theta_matrix.dropna(axis = 0, subset = ['price'],inplace=True) 
    scaler = MinMaxScaler()
    theta_matrix['price'] = scaler.fit_transform(theta_matrix[['price']])
    theta_matrix = pd.get_dummies(theta_matrix, prefix=['category'], columns=['category'])
    # weighting category / price lower
    theta_matrix['price'] = theta_matrix['price']*price_weight
    theta_matrix[theta_matrix.columns[-4:]] = theta_matrix[theta_matrix.columns[-4:]]*category_weight


    # find dists
    start3 = time.time()
    dists = cosine_distances(theta_matrix, theta_matrix)
    print('Distances created in ', time.time()-start3, ' seconds')

    wine_title = "Sweet Cheeks 2012 Vintner's Reserve Wild Child Block Pinot Noir (Willamette Valley)"
    # find_similar_wines(wine_title, dists, df_lookup)
    # df_lookup[df_lookup['title'] == wine_title]
