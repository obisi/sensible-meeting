import datetime

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
        parser.add_argument("sensor_id", type=int, location="form", required=True)
        parser.add_argument("num_people", type=int, location="form", required=True)
        parser.add_argument("location", type=str, location="form", required=True)
        sensor_id = parser.parse_args()["sensor_id"]
        num_people = parser.parse_args()["num_people"]
        location = parser.parse_args()["location"]

        is_ok = self.db.register_session(sensor_id, num_people, location)
        if is_ok:
            return jsonify({'is_ok': True, 'mess': 'Registered session successfully!'})
        else:
            return jsonify({'is_ok': False, 'mess': 'Registered session unsuccessfully!'})

class TerminateSession(SessionHandler):

    def __init__(self):
        super().__init__()

    def post(self):
        '''
        Terminate session of the sensor to the db
        Args:
        - session_id : ID of the sensor
        '''
        parser = RequestParser()
        parser.add_argument("session", type=int, location="form", required=True)
        session_id = parser.parse_args()["session"]
        db_session = self.db.fetch_session(session_id)
        now_ts = datetime.datetime.now().timestamp()
        if db_session:
            is_ok = self.db.update_session(session_id, db_session['num_people'], db_session['location'], now_ts)
            if is_ok:
                return jsonify({'is_ok': True, 'mess': 'Terminated session successfully!'})
            else:
                return jsonify({'is_ok': False, 'mess': 'Terminated session unsuccessfully!'})
        else:
            return jsonify({'is_ok': False, 'mess': 'The session does not existed!'})
