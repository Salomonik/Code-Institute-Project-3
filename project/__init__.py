import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'routes.login'

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    # Importowanie blueprintu
    from .routes import routes
    app.register_blueprint(routes)

    app.config['TWITCH_CLIENT_ID'] = os.environ.get('TWITCH_CLIENT_ID')
    app.config['TWITCH_CLIENT_SECRET'] = os.environ.get('TWITCH_CLIENT_SECRET')

    # Importowanie modelu User tutaj, aby uniknąć cyklicznych zależności
    from .models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
