from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.setting.config import CONFIGS as cf


class DataBaseHandler(Resource):

    def __init__(self):
        super().__init__()


class RecordSensorData(DataBaseHandler):

    def __init__(self):
        super().__init__()

    def post(self):
        parser = RequestParser()
        parser.add_argument("data", type=list, location="form", required=True)
        data = parser.parse_args()["data"]

        # TODO: Store sensor data to DB

        response_mess = {}
        return jsonify({'mess': response_mess})