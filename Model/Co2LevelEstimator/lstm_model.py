import joblib
import torch
import pandas as pd
import numpy as np

from Model.models_server import co2_level_estimation


MODEL_PATH = '../models/lstm_model.pt'
SCALER_PATH = '../models/lstm_scaler.pkl'
TIMEOUT = 100

class LSTM_CO2_Estimator():

    def __init__(self):
        self.load_model()

    def load_model(self):
        self.scaler = joblib.load(SCALER_PATH)
        self.model = torch.load(MODEL_PATH)
        self.lag_feature_len = 10
        self.pred_len = 10

    def get_features(self, lag_features):
        ## TODO: Assert len of timeserie, maybe auto fill the missing points
        _feats = []
        if len(lag_features) > self.lag_feature_len:
            _feats = lag_features[:self.lag_feature_len]
        if len(lag_features) < self.lag_feature_len:
            _feats = [0] * (len(lag_features) - self.lag_feature_len) + lag_features
        return self.scaler.transform(_feats)

    def predict(self, lag_features):
        feats = self.get_features(lag_features)
        y_pred = self.model([feats])
        co2_level_estimation = self.scaler.inverse_transform(np.array(y_pred))[0]
        return co2_level_estimation