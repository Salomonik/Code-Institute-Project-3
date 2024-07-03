import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    login_manager.login_view = 'routes.login'
    
    # Importowanie blueprintu
    from .routes import routes
    app.register_blueprint(routes)
    
    app.config['TWITCH_CLIENT_ID'] = os.environ.get('TWITCH_CLIENT_ID')
    app.config['TWITCH_CLIENT_SECRET'] = os.environ.get('TWITCH_CLIENT_SECRET')

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))