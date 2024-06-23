from flask import Blueprint, request, redirect, jsonify
import requests
import os

main = Blueprint('main', __name__)

CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('REDIRECT_URI')

def get_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    response.raise_for_status()
    return response.json()['access_token']

access_token = get_access_token()

@main.route('/login')
def login():
    auth_url = f'https://id.twitch.tv/oauth2/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope=user:read:email'
    return redirect(auth_url)

@main.route('/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(token_url, data=payload)
    response.raise_for_status()
    tokens = response.json()
    return f'Access Token: {tokens["access_token"]}'

@main.route('/get_games/<game_name>')
def get_games(game_name):
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'name': game_name
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return jsonify(response.json())
