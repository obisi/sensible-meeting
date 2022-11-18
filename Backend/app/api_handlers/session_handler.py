import datetime

from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from Backend.app.setting.config import CONFIGS as cf
from Backend.app.data_layer.postgresql_db import PostgreSQL_DB
from Backend.app.api_handlers.model_handler import ModelBaseHandler


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
        parser.add_argument("sensor_id", type=int, location="json", required=True)
        parser.add_argument("num_people", type=int, location="json", required=False)
        parser.add_argument("location", type=str, location="json", required=False)
        sensor_id = parser.parse_args().get("sensor_id")
        num_people = parser.parse_args().get("num_people")
        location = parser.parse_args().get("location")

        session_id = self.db.register_session(sensor_id, num_people, location)
        if session_id:
            return jsonify({'is_ok': True, 'session_id': session_id, 'mess': 'Registered session successfully!'})
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
        parser.add_argument("session", type=str, required=True)
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

class getSession(SessionHandler):
    def __init__(self):
        super().__init__()
    
    def get(self):
        '''
        Get data for session
        Args:
        - session_id : ID of the sensor
        '''
        parser = RequestParser()
        parser.add_argument("session", type=int, location="form", required=True)
        session_id = parser.parse_args()["session"]
        db_session = self.db.fetch_session(session_id)
        if db_session:
            session_data = db_session.read_session_data(session_id)
            if session_data:
                model_session = ModelBaseHandler()
                prediction = model_session.post(session_id)

                ret = {
                    "is_ok": True,
                    "session_data": session_data
                }
                ret.update(prediction)

                return jsonify(ret)
            else:
                return jsonify({'is_ok': False, 'mess': 'Unable to get session data!'})
        else:
            return jsonify({'is_ok': False, 'mess': 'The session does not existed!'})