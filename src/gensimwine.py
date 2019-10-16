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


def lemmatize_stemming(text):
    return WordNetLemmatizer().lemmatize(text, pos='v')

def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

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

    processed_docs = desc.map(preprocess)
    print('Data featurized')

    #create dictionary
    id2word = gensim.corpora.Dictionary(processed_docs)

    #create corpus
    texts = processed_docs

    #Term Document Frequency
    bow_corpus = [id2word.doc2bow(text) for text in texts]

    start = time.time()
    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=7, id2word=id2word, passes=2, workers=30)
    stop = time.time()
    print('Model created in ', stop-start)
    lda_model.save('model1')

    pprint(lda_model.print_topics())