import joblib
import psycopg2
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

from tqdm import tqdm
from sklearn.preprocessing import MinMaxScaler

def gaussian(t, fwhm):
    return np.exp(-(4*np.log(2)*t**2)/fwhm**2)

################
## Connect DB ##
################

PGDATABASE=''
PGHOST=''
PGPASSWORD=''
PGPORT=7747
PGUSER=''

conn = psycopg2.connect(
   database=PGDATABASE, user=PGUSER, password=PGPASSWORD, host=PGHOST, port=PGPORT
)
cursor = conn.cursor()

'''
data = pd.read_csv('csproject_co2-reading-2022-10-11_10-44-32.csv')
'''
# cursor.execute("DELETE FROM csproject_co2_reading WHERE session_id IS Null")
cursor.execute("SELECT * FROM csproject_co2_reading")
field_names = [i[0] for i in cursor.description]
db_data = cursor.fetchall()

# Convert records to df
data = pd.DataFrame.from_records(db_data, columns=field_names)
data['created_at'] = data['created_at'].astype(str)
data[data['value'] < 3000 ]['value'] = None
data[data['value'] > 180 ]['value'] = None

# Hanlde Nan and 0 values
data = data.drop(columns=['id'])
data = data.replace(0, np.nan)
data['value'] = data['value'].fillna((data['value'].shift() + data['value'].shift(-1))/2)

# Handle dates
date_format = '%Y-%m-%d %H:%M:%S.%f'
data['timestamp'] = data['created_at'].apply(
    lambda x: datetime.datetime.timestamp(datetime.datetime.strptime(x, date_format)))

# Smooth data
smooth_interval = 60 # seconds
smooth_data = data.groupby(data.index // smooth_interval).mean()

# Sort data
smooth_data = smooth_data.sort_values('timestamp', ascending=True).reset_index(drop=True)
len(smooth_data)

# check the lag autocorrelation
pd.plotting.autocorrelation_plot(smooth_data['value'].to_list())

# plot smoothed data
plt.figure(figsize=(16,8))
plt.title('CO2 Measurements')
plt.plot(smooth_data['value'])
plt.xlabel('Timestamp',fontsize=18)
plt.ylabel('CO2 level',fontsize=18)
plt.show()

##########
## LSTM ##
##########
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
torch.manual_seed(1)

def get_x_y_pairs(sequence_data, lag_feat_len, pred_len):
    lag_features = [
        sequence_data[i:i+lag_feat_len] 
        for i in range(len(sequence_data)-lag_feat_len-pred_len)
    ]
    Ys = [
        sequence_data[i+lag_feat_len:i+lag_feat_len+pred_len] 
        for i in range(len(sequence_data)-lag_feat_len-pred_len)
    ]
    return lag_features, Ys

class Co2SequenceDataset(Dataset):
    def __init__(self, df):
        self.df = df

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        X = torch.Tensor(row.X)
        y = torch.Tensor(row.Y)
        return X, y

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
    
def train_lstm(data_loader, model, optimizer):
    model.train()
    total_loss = 0.0
    for Xs, Ys in data_loader:
        Xs = torch.reshape(Xs, (Xs.shape[0], 1, Xs.shape[1]))
        Xs = Xs.to(device)
        Ys = Ys.to(device)
        optimizer.zero_grad()
        y_hat = model(Xs)
        loss = criterion(y_hat, Ys)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(data_loader)

def eval_lstm(data_loader, model):
    model.eval()
    total_loss = 0.0
    with torch.no_grad():
        for Xs, Ys in data_loader:
            Xs = torch.reshape(Xs, (Xs.shape[0], 1, Xs.shape[1]))
            Xs = Xs.to(device)
            Ys = Ys.to(device)
            y_hat = model(Xs)
            loss = criterion(y_hat, Ys)
            total_loss += loss.item()
    return total_loss / len(data_loader)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

scale_data = True
lag_feat_len = 10 # 10min
pred_len = 10 # 10min

batch_size = 50
input_dim = lag_feat_len
hidden_dim = 32
layer_dim = 1
output_dim = pred_len
epochs = 300
lr = 0.001

sequence_data = smooth_data['value'].to_list()

if scale_data:
    print('[Info] Scaling data values between 0,1...')
    _sequence_data = [[_] for _ in sequence_data]
    scaler = MinMaxScaler(feature_range=(0, 1)) 
    scaled_data = scaler.fit_transform(_sequence_data)
    sequence_data = [_[0] for _ in scaled_data]
    joblib.dump(scaler, 'lstm_scaler.pkl')
    print('--> Saved scaler')

print('[Info] Creating lag features data ...')
lag_feats, Ys = get_x_y_pairs(sequence_data, lag_feat_len, pred_len)
print('--> Features shape', np.array(lag_feats).shape)
print('--> Targets shape', np.array(Ys).shape)

print('[Info] Splitting train, val and test datasets ...')
df = pd.DataFrame({'X': lag_feats, 'Y': Ys})
# df = df.sample(frac=1).reset_index(drop=True)
train_val_df, test_df = train_test_split(df, test_size = 0.2, shuffle = False)
train_df, valid_df = train_test_split(train_val_df, test_size = 0.25, random_state = 42)
print('--> Train len:', len(train_df))
print('--> Val len:', len(valid_df))
print('--> Test len:', len(test_df))

print('[Info] Creating DataLoaders ...')
trainset = Co2SequenceDataset(train_df)
validset = Co2SequenceDataset(valid_df)
testset = Co2SequenceDataset(test_df)
train_loader = DataLoader(trainset, batch_size=batch_size, shuffle=True)
valid_loader = DataLoader(validset, batch_size=batch_size)
test_loader = DataLoader(testset, batch_size=1)
for x, y in train_loader:
    break
print('--> One batch X shape:', x.shape)
print('--> One batch y shape:', y.shape)

print('[Info] Training model ...')
model = LSTMModel(input_dim, hidden_dim, layer_dim, output_dim)
model.to(device)
criterion = nn.MSELoss(reduction='mean')
optimizer = optim.Adam(model.parameters(), lr=lr)

last_updated_best_model_epoch = 0
best_valid_loss = np.Inf
train_epoch_loss = []
val_epoch_loss = []
for i in range(epochs):
    train_loss = train_lstm(train_loader, model, optimizer)
    valid_loss = eval_lstm(valid_loader, model)
    train_epoch_loss.append(train_loss)
    val_epoch_loss.append(valid_loss)
    if valid_loss < best_valid_loss:
        torch.save(model.state_dict(), 'lstm_model.pt')
        best_valid_loss = valid_loss
        last_updated_best_model_epoch = i+1
    if i == 0 or (i+1) % 100 == 0 or i+1 == epochs:
        print(f'--> Epoch: {i+1}, Train loss: {train_loss}, Validation loss: {valid_loss}')

plt.plot(train_epoch_loss)
plt.plot(val_epoch_loss)
plt.legend(['Train loss', 'Validate loss'], loc='upper right')
plt.show()
print('[Info] Last updated best model at epoch {}'.format(last_updated_best_model_epoch))

y_true = []
y_pred = []
total_loss = 0.0
for Xs, Ys in test_loader:
    Xs = torch.reshape(Xs, (Xs.shape[0], 1, Xs.shape[1]))
    Xs = Xs.to(device)
    Ys = Ys.to(device)
    y_hat = model(Xs)
    loss = criterion(y_hat, Ys)
    total_loss += loss.item()
    y_true.append(Ys.detach().numpy()[0])
    y_pred.append(y_hat.detach().numpy()[0])
test_df['Y_pred'] = pd.Series(y_pred, index=test_df.index)
train_val_df['Y_pred'] = None
plot_df = pd.concat([train_val_df,test_df],ignore_index=False)
inversed_scale_prediction = scaler.inverse_transform(np.array(y_pred))

plt.figure(figsize=(16,8))
plt.title('LSTM model')
plt.xlabel('Time', fontsize=18)
plt.ylabel('CO2 level', fontsize=18)

general = True
min_test_idx = min(test_df.index)
max_test_idx = max(test_df.index)
print('[Info] Test Loss:', total_loss / len(test_loader))

plt.plot([_[0] for _ in plot_df['Y'].to_list()])
if not general:
    plot_test_idx = min_test_idx + 1
    test_pred_plot = [None]*(len(train_val_df) + plot_test_idx-min_test_idx) + plot_df['Y'][plot_test_idx]
    plt.plot(test_pred_plot)
else:
    plt.plot([_[0] if _ is not None else None for _ in plot_df['Y_pred'].to_list()])
plt.legend(['Y true', 'Y pred'], loc='upper right')
plt.show()