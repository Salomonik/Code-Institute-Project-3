from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import migrate
from config import Config

db = SQLAlchemy()
migrate = migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app,db)
    
    import routes, models
    
    return app