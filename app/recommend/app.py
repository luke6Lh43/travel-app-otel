from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'To be implemented in a next release'

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5005, threaded=True)