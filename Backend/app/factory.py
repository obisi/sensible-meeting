from flask import Flask
from flask import jsonify
from flask_restful import Api
from flask_cors import CORS

from Backend.app.setting.config import CONFIGS


def create_app(register_stuffs=True, config=CONFIGS):
    app = Flask(__name__)
    app.config.from_object(config)

    register_rest_api(app)
    return app


def register_rest_api(app):
    from Backend.app.api_handlers.data_handler import RecordSensorData
    from Backend.app.api_handlers.session_handler import RegisterSession, TerminateSession, getSession
    from Backend.app.api_handlers.model_handler import EstimateCO2Level

    version = app.config["VERSION"]
    rest_api_url = app.config["REST_API_URL"]
    api_version_url = "/{}/{}/".format(rest_api_url, version)
    api = Api(app)
    CORS(app)

    api.add_resource(RecordSensorData, "{}data_io/record".format(api_version_url))
    api.add_resource(EstimateCO2Level, "{}model/estimate_co2".format(api_version_url))
    api.add_resource(RegisterSession, "{}session/register".format(api_version_url))
    api.add_resource(TerminateSession, "{}session/terminate".format(api_version_url))
    api.add_resource(getSession, "{}session/get_session".format(api_version_url))