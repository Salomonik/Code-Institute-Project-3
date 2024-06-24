import os

os.environ.setdefault("IP", "0.0.0.0")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("SECRET_KEY", "any_secret_key")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("DEVELOPMENT", "True")
os.environ.setdefault("DB_URL", "postgresql://postgres:H@localhost/project")
os.environ['TWITCH_CLIENT_ID'] = 'uo0gzrbsiyigb5u0fx6xfrp0t041g1'
os.environ['TWITCH_CLIENT_SECRET'] = 'ublqbikwqvtf0m19lkqkp03rt3efxp'