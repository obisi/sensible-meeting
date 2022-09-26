from flask import jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

from app.setting.config import CONFIGS as cf


class ModelBaseHandler(Resource):

    def __init__(self):
        super().__init__()


class EstimateCO2Level(ModelBaseHandler):

    def __init__(self):
        super().__init__()

    def post(self):
        '''
        Estimate the Co2 level in next <given> minutes
        Args:
        - in_next (float): the amount of minute from now
        Response:
        - co2_level (float): estimation of Co2
        - should_terminate_meeting_in (float): predict when the meeting should end (in next N minutes)
        '''
        parser = RequestParser()
        parser.add_argument("in_next", type=float, location="form", required=True)
        in_next = parser.parse_args()["in_next"]

        # TODO: Call model to estimate Co2 level --> return to UI

        response_mess = {
            'co2_level': 0.0,
            'should_terminate_meeting_in': 10.0,
        }
        return jsonify(response_mess)