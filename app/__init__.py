from flask import Flask
from flask_login import LoginManager
from app.models import db, User
from config import config

login_manager = LoginManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Login manager config
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Je moet inloggen om deze pagina te bekijken'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.auth.routes import auth_bp
    from app.main.routes import main_bp
    from app.projects.routes import projects_bp
    from app.invites.routes import invites_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(invites_bp, url_prefix='/invites')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app