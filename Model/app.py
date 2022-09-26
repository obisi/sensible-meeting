from flask import Flask

app = Flask(__name__)



@app.route('/info',methods="GET")
def info():
    return "Welcome to Sensible Meeting model app"

@app.route('/health',methods="GET")
def health():
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)