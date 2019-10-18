import pandas as pd 
import numpy as np 


class Cleaning(object):
    def __init__(self, raw_data):
        self.raw_data = raw_data
        self.processed_data = None
        self.cleansed_data = None


    def CreateDataFrame(self):
        df = pd.read_csv(self.raw_data)
        df.drop(labels='Unnamed: 0',axis=1,inplace=True)
        self.processed_data = df.description


    def CleanDataFrame(self):
        desc = self.processed_data.str.lower()
        desc = desc.str.replace('[^a-zA-Z0-9 \n\.]', ' ')
        desc = desc.str.replace('\d', ' ')
        self.cleansed_data = desc.str.replace('.', ' ')

