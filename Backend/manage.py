from flask import Flask, request
from flask import jsonify
import os

from app.factory import create_app

app = create_app()
port = int(os.environ.get("PORT", 5000))
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=port)


#TODO: Add commands to run scripts beside the app (if needed in future)