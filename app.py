import os
from flask import Flask, render_template, request
import requests

app = Flask(__name__)

CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')

def get_igdb_access_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

access_token = get_igdb_access_token(CLIENT_ID, CLIENT_SECRET)

@app.route('/')
def index():
    return render_template('index.html')

