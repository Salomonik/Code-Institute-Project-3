import os
import requests
from flask import render_template, request, jsonify
from . import app, db
from .models import Game

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
    try:
        # Fetch popular games
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        data = (
            'fields name, cover.url, first_release_date, genres.name, platforms.name, '
            'storyline, involved_companies.company.name, game_modes.name, screenshots.url, videos.video_id; '
            'sort hypes desc; '
            'limit 12;'
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
        
        # Debugging: Print the popular games data
        print("Popular games:", popular_games)
        
        modify_images(popular_games)
         
        return render_template('index.html', popular_games=popular_games)
    except Exception as e:
        print("Error fetching popular games:", e)
        return render_template('error.html', error=str(e))

def modify_image_url(url, size):
    # Znajdź nazwę rozdzielczości w URL i zamień ją na nową rozdzielczość
    sizes = ["t_thumb", "t_cover_small", "t_logo_med", "t_screenshot_med", "t_cover_big", "t_screenshot_big", "t_screenshot_huge", "t_720p", "t_1080p"]
    for s in sizes:
        if s in url:
            return url.replace(s, size)
    return url  # Jeśli nie znaleziono żadnej z powyższych nazw, zwróć URL bez zmian

def modify_images(game_details):
    for game in game_details:
        if 'cover' in game:
            game['cover']['url'] = modify_image_url(game['cover']['url'], 't_cover_big')
        if 'screenshots' in game:
            for screenshot in game['screenshots']:
                screenshot['url'] = modify_image_url(screenshot['url'], 't_screenshot_huge')

@app.route('/get_games', methods=['GET'])
def get_games():
    try:
        game_name = request.args.get('game_name')
        platform = request.args.get('platform')
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
        
        if platform:
            data += f' where platforms = [{platform}];'
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        game_info = response.json()
        
        modify_images(game_info)
        
        return render_template('games.html', game_info=game_info)
    except Exception as e:
        print("Error fetching game data:", e)
        return render_template('error.html', error=str(e))

@app.route('/game_details/<int:game_id>', methods=['GET'])
def game_details(game_id):
    try:
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        data = (
            f'fields name, genres.name, platforms.name, release_dates.human, summary, storyline, cover.url, '
            'screenshots.url, videos.video_id, rating, rating_count, involved_companies.company.name, '
            'game_modes.name, themes.name, first_release_date; '
            f'where id = {game_id};'
        )
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        game_details = response.json()
        
        modify_images(game_details)
        
        return render_template('game_details.html', game_details=game_details[0])
    except Exception as e:
        print("Error fetching game details:", e)
        return render_template('error.html', error=str(e))

@app.route('/suggest_games', methods=['GET'])
def suggest_games():
    try:
        query = request.args.get('query')
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': CLIENT_ID,
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        data = (
            f'search "{query}"; '
            'fields name; '
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
        suggestions = response.json()
        
        # Debugging: Print the suggestions data
        print("Suggestions:", suggestions)
        
        modify_images(suggestions)
        
        return jsonify(suggestions)
    except Exception as e:
        print("Error fetching game suggestions:", e)
        return jsonify([])

# Definiowanie filtra dateformat
@app.template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    return datetime.fromtimestamp(value).strftime(format)
