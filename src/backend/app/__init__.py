from flask import Flask
from flask_cors import CORS

def create_app():
    """App factory for creating the Flask app instance."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes

    # Register blueprints (modular routes)
    from .routes.folders import folders_bp
    from .routes.projects import projects_bp
    from .routes.chains import chains_bp
    from .routes.other import other_bp
    from .routes.get_set_slaves import slaves_bp
    from .routes.auto_test import auto_test_bp

    app.register_blueprint(folders_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(chains_bp)
    app.register_blueprint(other_bp)
    app.register_blueprint(slaves_bp)
    app.register_blueprint(auto_test_bp)

    return app
