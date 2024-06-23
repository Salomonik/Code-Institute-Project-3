import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

if os.path.exists("env.py"):
    import env  # noqa

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
app.config["DEBUG"] = os.environ.get("DEBUG") == 'True'

db = SQLAlchemy(app)

# Importowanie tras
from project import routes  # noqa

# Dodaj atrybut app do przestrzeni nazw modułu
__all__ = ['app']
