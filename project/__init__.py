import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Importowanie blueprintu
    from .routes import routes
    app.register_blueprint(routes)
    
    app.config['TWITCH_CLIENT_ID'] = os.environ.get('TWITCH_CLIENT_ID')
    app.config['TWITCH_CLIENT_SECRET'] = os.environ.get('TWITCH_CLIENT_SECRET')

    return app
