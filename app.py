import os

# Importuj plik env.py, jeśli istnieje
if os.path.exists("env.py"):
    import env  # noqa

from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Pobierz zmienne środowiskowe
CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')

# Debugowanie: Sprawdź, czy zmienne środowiskowe są ustawione
print(f"Client ID: {CLIENT_ID}")  # Powinno wyświetlać rzeczywisty Client ID
print(f"Client Secret: {CLIENT_SECRET}")  # Powinno wyświetlać rzeczywisty Client Secret

def get_igdb_access_token(client_id, client_secret):
    url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    
    # Debugowanie: Wyświetl odpowiedź serwera
    print("Response status code:", response.status_code)
    print("Response text:", response.text)
    
    response.raise_for_status()
    return response.json()['access_token']

try:
    access_token = get_igdb_access_token(CLIENT_ID, CLIENT_SECRET)
    print(f"Access Token: {access_token}")  # Debugowanie: Wyświetl token dostępu
except Exception as e:
    print(f"Error obtaining access token: {e}")  # Debugowanie: Wyświetl błąd

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
    
    # Debugowanie: Wyświetl odpowiedź serwera
    print("Response status code:", response.status_code)
    print("Response text:", response.text)
    
    response.raise_for_status()
    game_info = response.json()
    return render_template('games.html', game_info=game_info)

if __name__ == '__main__':
    app.run(host=os.environ.get("IP", "0.0.0.0"), port=int(os.environ.get("PORT", 5000)), debug=True)
