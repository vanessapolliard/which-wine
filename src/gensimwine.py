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

def find_similar_wines(wine_title):
    wine_idx = df[df['title'] == wine_title].index[0]
    top_wines = np.argsort(dists[wine_idx, :])[-10:][::1]
    # top_wines = df.title[top_wines]
    top_wines = df.loc[top_wines][['title', 'variety']]
    return top_wines[1:]


if __name__ == '__main__':
    # raw_data = '../data/winemag-data-190314.csv'
    raw_data = '../data/winemag_data_inclcategory.csv' # includes category - red, white, etc
    year_cutoff = 2008.0
    num_topics = 7
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
    bow_corpus_df = pd.DataFrame(bow_corpus)
    bow_corp_subset = bow_corpus_df[df_full['vintage'] > year_cutoff]
    bow_corpus2 = list(bow_corp_subset)

    # # document vs topic list of lists of tuples
    # theta = [lda_model.get_document_topics(item)
    #          for item in bow_corpus[:50000]] # limit to 50000 data points
    # print('Theta array created')

    # # create theta matrix
    # start2 = time.time()
    # theta_matrix = create_theta_matrix(theta, num_topics)
    # print('Matrix created in ', time.time()-start2, ' seconds')

    # # TODO
    # # add price, varietal, category to matrix
    # df_sub2 = df_full[df_full['vintage'] > year_cutoff][['category','price']]
    # theta_matrix['category'] = df_sub2['category']
    # theta_matrix['price'] = df_sub2['price']
    # scaler = MinMaxScaler()
    # theta_matrix['price'] = scaler.fit_transform(theta_matrix[['price']])
    # theta_matrix = pd.get_dummies(theta_matrix, prefix=['category'], columns=['category'])
    # theta_matrix.dropna(inplace=True)
    # # need to test out dummies and normalized price and see if i need to scale them at all



    # # find dists once then save matrix
    # start3 = time.time()
    # #dists = cosine_distances(theta_matrix, theta_matrix)
    # print('Distances created in ', time.time()-start3, ' seconds')
    # #find_similar_wines('wine_title')