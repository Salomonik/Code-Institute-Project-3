import os
import time
from datetime import datetime
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Import env.py to set environment variables
if os.path.exists("env.py"):
    import env  # noqa

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
    
    # Debugging: Print the request details
    print("Request URL:", url)
    print("Request Payload:", payload)
    
    response.raise_for_status()
    return response.json()['access_token']

# Debugging: Print the CLIENT_ID and CLIENT_SECRET
print("Client ID:", CLIENT_ID)
print("Client Secret:", CLIENT_SECRET)

access_token = get_igdb_access_token(CLIENT_ID, CLIENT_SECRET)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/popular_games', methods=['GET'])
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
    
    # Debugging: Print the request details
    print("Request URL:", url)
    print("Request Headers:", headers)
    print("Request Data:", data)
    
    response = requests.post(url, headers=headers, data=data)
    
    # Debugging: Print the response details
    print("Response status code:", response.status_code)
    print("Response text:", response.text)
    
    response.raise_for_status()
    popular_games = response.json()
    
    return render_template('index.html', popular_games=popular_games)

def modify_image_url(url, size):
    # Znajdź nazwę rozdzielczości w URL i zamień ją na nową rozdzielczość
    sizes = ["t_thumb", "t_cover_small", "t_logo_med", "t_screenshot_med", "t_cover_big", "t_screenshot_big", "t_screenshot_huge", "t_720p", "t_1080p"]
    for s in sizes:
        if s in url:
            return url.replace(s, size)
    return url  # Jeśli nie znaleziono żadnej z powyższych nazw, zwróć URL bez zmian


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
        'fields name, genres.name, platforms.name, release_dates.human, summary, storyline, cover.url, '
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
                screenshot['url'] = modify_image_url(screenshot['url'], 't_screenshot_huge')
    
    # Debugowanie: Wyświetl URL-e zrzutów ekranu
    for game in game_info:
        if 'screenshots' in game:
            for screenshot in game['screenshots']:
                print("Screenshot URL:", screenshot['url'])

    return render_template('games.html', game_info=game_info)

# Definiowanie filtra dateformat
@app.template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    return datetime.fromtimestamp(value).strftime(format)

if __name__ == '__main__':
    app.run(host=os.environ.get("IP", "0.0.0.0"), port=int(os.environ.get("PORT", 5000)), debug=True)
