import os

# Importuj plik env.py, jeśli istnieje
if os.path.exists("env.py"):
    import env  # noqa

from flask import Flask, render_template, request
import requests
from datetime import datetime

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

def modify_image_url(url, size):
    return url.replace('t_thumb', size)

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
    data = (
        f'search "{game_name}"; '
        'fields name, genres.name, platforms.name, summary, storyline, cover.url, '
        'screenshots.url, videos.video_id, rating, rating_count, involved_companies.company.name, '
        'game_modes.name, themes.name, first_release_date;'
    )
    
    # Debugowanie: Wyświetl zapytanie
    print("Request URL:", url)
    print("Request Headers:", headers)
    print("Request Data:", data)
    
    response = requests.post(url, headers=headers, data=data)
    
    # Debugowanie: Wyświetl odpowiedź serwera
    print("Response status code:", response.status_code)
    print("Response text:", response.text)
    
    response.raise_for_status()
    game_info = response.json()
    
    # Modyfikacja URL obrazów
    for game in game_info:
        if 'cover' in game:
            game['cover']['url'] = modify_image_url(game['cover']['url'], 't_cover_big')
        if 'screenshots' in game:
            for screenshot in game['screenshots']:
                screenshot['url'] = modify_image_url(screenshot['url'], 't_screenshot_big')
    
    # Debugowanie: Wyświetl URL-e zrzutów ekranu
    for game in game_info:
        if 'screenshots' in game:
            for screenshot in game['screenshots']:
                print("Screenshot URL:", screenshot['url'])

    return render_template('games.html', game_info=game_info)


def popular_games():
    url = 'https://api.igdb.com/v4/games'
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    data = (
        'fields name, popularity, rating, cover.url, first_release_date, genres.name, platforms.name; '
        'sort popularity desc; '
        'where first_release_date >= ' + str(int(time.time()) - 30 * 24 * 60 * 60) + '; '
        'limit 10;'
    )
    
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    games = response.json()
    
    # Debugging
    print(games)

    return render_template('popular_games.html', games=games)

# Definiowanie filtra dateformat
@app.template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    return datetime.fromtimestamp(value).strftime(format)

if __name__ == '__main__':
    app.run(host=os.environ.get("IP", "0.0.0.0"), port=int(os.environ.get("PORT", 5000)), debug=True)
