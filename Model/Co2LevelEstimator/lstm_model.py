import joblib
import torch
import pandas as pd
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim


MODEL_PATH = 'Model/models/lstm_model.pt'
SCALER_PATH = 'Model/models/lstm_scaler.pkl'
TIMEOUT = 100

class LSTMModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, layer_dim, output_dim):
        super(LSTMModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.layer_dim = layer_dim
        self.lstm = nn.LSTM(input_dim, hidden_dim, layer_dim, batch_first=True)
        self.linear = nn.Linear(hidden_dim, output_dim)
        
    def forward(self, x, hidden=None):
        h0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).requires_grad_()
        c0 = torch.zeros(self.layer_dim, x.size(0), self.hidden_dim).requires_grad_()
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        out = self.linear(out[:, -1, :])
        return out

class LSTM_CO2_Estimator():

    def __init__(self, len_lag_feat=10, hidden_dim=32, layer_dim=1, output_dim=10):
        self.len_lag_feat = len_lag_feat
        self.hidden_dim = hidden_dim
        self.layer_dim = layer_dim
        self.output_dim = output_dim
        self.load_model()

    def load_model(self):
        self.scaler = joblib.load(SCALER_PATH)
        model_state_dict = torch.load(MODEL_PATH)
        self.model = LSTMModel(self.len_lag_feat, self.hidden_dim, self.layer_dim, self.output_dim)
        self.model.load_state_dict(model_state_dict)
        self.model.eval()

    def get_features(self, lag_features):
        ## TODO: Assert len of timeserie, maybe auto fill the missing points
        _feats = []
        if len(lag_features) >= self.len_lag_feat:
            _feats = lag_features[:self.len_lag_feat]
        else:
            _feats = [0] * (len(lag_features) - self.len_lag_feat) + lag_features
        return self.scaler.transform([_feats])

    def predict(self, lag_features):
        feats = self.get_features(lag_features)
        Xs = torch.Tensor(feats)
        Xs = torch.reshape(Xs, (Xs.shape[0], 1, Xs.shape[1]))
        y_pred = self.model(Xs).detach().numpy()
        co2_level_estimation = self.scaler.inverse_transform(np.array(y_pred))[0]
        return co2_level_estimation.tolist()