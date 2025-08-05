import os
from flask import Flask
from flask_cors import CORS
from waitress import serve
import routes
from routes import register_routes
import sys

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
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    # This runs only if you start with `python app.py`
    from waitress import serve
    serve(app, host='127.0.0.1', port=port)
    print("Server started on http://", flush=True)
