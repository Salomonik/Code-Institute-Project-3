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

@app.route('/get_games', methods=['GET'])
def get_games():
    game_name = request.args.get('game_name')
    url = 'https://api.igdb.com/v4/games'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    data = f'search "{game_name}"; fields name, genres.name, release_dates.human;'
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    game_info = response.json()
    return render_template('games.html', game_info=game_info)

if __name__ == '__main__':
    app.run(host=os.environ.get("IP", "0.0.0.0"), port=int(os.environ.get("PORT", 5000)), debug=True)