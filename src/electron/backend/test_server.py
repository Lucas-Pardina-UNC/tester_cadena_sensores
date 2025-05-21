# test_server.py
from flask import Flask
from waitress import serve

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Waitress!"

if __name__ == '__main__':
    print("Starting server...")
    serve(app, host='127.0.0.1', port=5000)
