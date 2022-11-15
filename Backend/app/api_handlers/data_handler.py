import datetime

from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from Backend.app.setting.config import CONFIGS as cf
from Backend.app.data_layer.postgresql_db import PostgreSQL_DB

date_format = '%Y-%m-%d %H:%M:%S.%f'


class SensorRecordHandler(Resource):

    def __init__(self):
        super().__init__()
        self.db = PostgreSQL_DB()


class RecordSensorData(SensorRecordHandler):

    def __init__(self):
        super().__init__()

    def post(self):
        parser = RequestParser()
        parser.add_argument("sensor_id", type=int, location="form", required=True)
        parser.add_argument("value", type=float, location="form", required=True)
        parser.add_argument("session_id", type=int, location="form", required=False)
        parser.add_argument('created_at', type=lambda x: datetime.strptime(x,date_format), location="form", required=False)

        sensor_id = parser.parse_args()["sensor_id"]
        value = parser.parse_args()["value"]
        created_at = parser.parse_args()["created_at"]
        session_id = parser.parse_args().get('session_id', None)

        is_ok = self.db.save_sensor_data(sensor_id, value, created_at, session_id)
        if is_ok:
            return jsonify({'is_ok': True, 'mess': 'Save sensor record successfully!'})
        else:
            return jsonify({'is_ok': False, 'mess': 'Save sensor record unsuccessfully!'})