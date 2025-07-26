import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

# Flask-Migrate will be initialized inside the app factory
migrate = Migrate()

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # Config from .env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from . import models
    from .models import User
    from .routes import auth, dashboard, invoices, vendors, timesheets

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(invoices.bp)
    app.register_blueprint(vendors.bp)
    app.register_blueprint(timesheets.bp)

    return app

# ✅ Create the app object so it can be used in seed.py and alembic
app = create_app()