from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# The auth blueprint defines the login/signup route as `login_signup` (endpoint
# name: 'auth.login_signup'), so point Flask-Login at that endpoint.
login_manager.login_view = 'auth.login_signup'

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')

    # Secret key (required for sessions)
    app.config['SECRET_KEY'] = 'mysecretkey'  # you can change later

    # Database config (replace password with your MySQL password)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/lifelens'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Register user loader for flask-login
    # We import here to avoid circular imports at module import time
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        """Return the user object for Flask-Login given a user ID."""
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Register blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .main import main_bp
    app.register_blueprint(main_bp)

    return app
