import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1', 't']
    DEVELOPMENT = os.environ.get('DEVELOPMENT', 'False').lower() in ['true', '1', 't']
    TWITCH_CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')  # Dodaj to, jeśli tego potrzebujesz
    TWITCH_CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')  # Dodaj to, jeśli tego potrzebujesz
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
