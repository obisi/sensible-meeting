from flask import Flask, jsonify, request
from Model.Co2LevelEstimator.model import Co2Estimator

app = Flask(__name__)


@app.route('/fi_diff', methods=['POST'])
def co2_level_estimation():
    timeserie_features = request.json['timeserie_features']
    co2_level = co2_model.predict(timeserie_features)
    return jsonify({'co2_level': co2_level})


if __name__ == '__main__':
    print("Initializing C02 model...")
    co2_model = Co2Estimator()
    ## TODO: Initialize other models if needed (for scalability)
    app.run(host='0.0.0.0', port=5000)
