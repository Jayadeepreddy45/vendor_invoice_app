import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_migrate import Migrate

# Load environment variables from .env
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to this when not logged in

def create_app():
    # ✅ Explicitly set template and static folder (helps avoid confusion)
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # ✅ Config values from .env
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)


    # ✅ Import and register after app is created
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
