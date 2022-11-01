from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.setting.config import CONFIGS as cf
from Backend.app.data_layer.postgresql_db import PostgreSQL_DB


class SessionHandler(Resource):

    def __init__(self):
        super().__init__()
        self.db = PostgreSQL_DB()


class RegisterSession(SessionHandler):

    def __init__(self):
        super().__init__()

    def post(self):
        '''
        Register session of the sensor to the db
        Args:
        - sensor_id : ID of the sensor
        '''
        parser = RequestParser()
        parser.add_argument("sensor_id", type=list, location="form", required=True)
        sensor_id = parser.parse_args()["sensor_id"]

        # TODO: Store sensor data to DB

        response_mess = {}
        return jsonify({'mess': response_mess})