import os
from flask import Flask
from flask_cors import CORS
from waitress import serve
from routes import register_routes

def create_app():
    app = Flask(__name__)
    register_routes(app)
    return app

# This is what Waitress (or gunicorn, etc.) needs:
app = create_app()
CORS(app, origins=["http://localhost:5123"])


@app.route('/')
def home():
    return "Hello from Waitress!"

if __name__ == '__main__':
    print(f"Flask Python PID: {os.getpid()}", flush=True)
    
    # This runs only if you start with `python app.py`
    from waitress import serve
    serve(app, host='127.0.0.1', port=5000)
