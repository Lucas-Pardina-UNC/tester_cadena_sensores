from .auto_test import auto_test_bp
from .chains import chains_bp
from .folders import folders_bp
from .get_set_slaves import slaves_bp
from .other import other_bp
from .projects import projects_bp



def register_routes(app):
    app.register_blueprint(folders_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(chains_bp)
    app.register_blueprint(slaves_bp)
    app.register_blueprint(other_bp)
    app.register_blueprint(auto_test_bp)

    
    


