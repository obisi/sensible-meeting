from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import date, timedelta

from Backend.app.setting.config import CONFIGS as cf
from Backend.app.data_layer.postgresql_db import PostgreSQL_DB
from Model.Co2LevelEstimator.lstm_model import LSTM_CO2_Estimator


class ModelBaseHandler(Resource):

    def __init__(self):
        super().__init__()
        self.db = PostgreSQL_DB()


class EstimateCO2Level(ModelBaseHandler):

    def __init__(self):
        super().__init__()

    def post(self):
        '''
        Estimate the Co2 level in next 10 minutes
        Args:
        - session_id (float): the amount of minute from now
        Response:
        - co2_level_pred (float): estimation of Co2 in next 10 min
        - should_terminate_meeting_in (float): predict when the meeting should end (in next N minutes)
        '''
        parser = RequestParser()
        parser.add_argument("session_id", type=float, location="form", required=True)
        session_id = parser.parse_args()["session_id"]

        model = LSTM_CO2_Estimator(len_lag_feat=10)
        _from_date = date.today() - timedelta(minutes = 10)
        db_data = self.db.load_sensor_data(session_id, _from_date, None)
        db_data = db_data.groupby(db_data.index // 60).mean()
        db_data = db_data.sort_values('timestamp', ascending=True).reset_index(drop=True)
        lag_features = db_data['value'].to_list()[-10:]
        pred = model.predict(lag_features)

        response_mess = {
            'co2_level_pred': pred,
            'should_terminate_meeting_in': 10.0,
        }
        return jsonify(response_mess)