import re
import os

import pickle
import string
import pyconll
import requests
import statistics

import pandas as pd
import numpy as np

MODEL_PATH = './co2_level_estimator.pickle'
TIMEOUT = 100

class Co2Estimator:

    def __init__(self):
        self.load_model()


    def load_model(self, path=MODEL_PATH):
        self.model = pickle.load(open( path, "rb"))

    def get_features(self, timeserie_features):
        ## TODO: Assert len of timeserie, maybe auto fill the missing points
        return []

    def predict(self, timeserie_features):
        feats = self.get_features(timeserie_features)
        co2_level = self.model.predict(feats)[0]
        return co2_level