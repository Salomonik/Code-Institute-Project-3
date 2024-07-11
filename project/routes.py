import os
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from project import db
from project.forms import RegistrationForm, LoginForm, UpdateProfileForm
from project.models import User, Game, Favorite, Comment, Like, Friend, GameGenre, GameGenreAssociation, UserProfile
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
from sqlalchemy.exc import IntegrityError

routes = Blueprint('routes', __name__)

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

@routes.route('/')
def index():
    try:
        client_id = current_app.config['TWITCH_CLIENT_ID']
        client_secret = current_app.config['TWITCH_CLIENT_SECRET']
        
        # Debugging prints
        print("Client ID:", client_id)
        print("Client Secret:", client_secret)

        access_token = get_igdb_access_token(client_id, client_secret)
        current_app.config['ACCESS_TOKEN'] = access_token
        
        # Debugging prints
        print("Access Token:", access_token)
        
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        data = (
            'fields name, cover.url, first_release_date, genres.name, platforms.name, '
            'storyline, involved_companies.company.name, game_modes.name, screenshots.url, videos.video_id; '
            'sort hypes desc; '
            'limit 12;'
        )
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        popular_games = response.json()
        
        modify_images(popular_games)
        
        return render_template('index.html', popular_games=popular_games)
    except Exception as e:
        print("Error fetching popular games:", e)
        return render_template('error.html', error=str(e))

def modify_image_url(url, size):
    sizes = ["t_thumb", "t_cover_small", "t_logo_med", "t_screenshot_med", "t_cover_big", "t_screenshot_big", "t_screenshot_huge", "t_720p", "t_1080p"]
    for s in sizes:
        if s in url:
            return url.replace(s, size)
    return url

def modify_images(game_details):
    for game in game_details:
        if 'cover' in game:
            game['cover']['url'] = modify_image_url(game['cover']['url'], 't_cover_big')
        if 'screenshots' in game:
            for screenshot in game['screenshots']:
                screenshot['url'] = modify_image_url(screenshot['url'], 't_screenshot_huge')

@routes.route('/get_games', methods=['GET'])
def get_games():
    try:
        # Debugging print
        print("Access Token:", current_app.config.get('ACCESS_TOKEN'))
        
        game_name = request.args.get('game_name')
        platform = request.args.get('platform')
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': current_app.config['TWITCH_CLIENT_ID'],
            'Authorization': f'Bearer {current_app.config["ACCESS_TOKEN"]}',
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

@routes.route('/game_details/<int:game_id>', methods=['GET'])
def game_details(game_id):
    try:
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': current_app.config['TWITCH_CLIENT_ID'],
            'Authorization': f'Bearer {current_app.config["ACCESS_TOKEN"]}',
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

@routes.route('/suggest_games', methods=['GET'])
def suggest_games():
    try:
        query = request.args.get('query')
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': current_app.config['TWITCH_CLIENT_ID'],
            'Authorization': f'Bearer {current_app.config["ACCESS_TOKEN"]}',
            'Accept': 'application/json'
        }
        data = (
            f'search "{query}"; '
            'fields name; '
            'limit 10;'
        )
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        suggestions = response.json()
        
        return jsonify(suggestions)
    except Exception as e:
        print("Error fetching game suggestions:", e)
        return jsonify([])

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            hashed_password = generate_password_hash(form.password.data)
            user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
            try:
                db.session.add(user)
                db.session.commit()
                flash('Your account has been created! You can now log in.', 'success')
                return redirect(url_for('routes.login'))
            except IntegrityError:
                db.session.rollback()
                flash('Email address already exists.', 'danger')
        else:
            flash('Email address already exists.', 'danger')
    return render_template('register.html', title='Register', form=form)

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login Successful.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('routes.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@routes.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()
    avatars = os.listdir(os.path.join(current_app.static_folder, 'profile_pics'))

    if form.validate_on_submit():
        avatar = form.selected_avatar.data
        if avatar:
            avatar_url = 'profile_pics/' + avatar
            if current_user.profile:
                current_user.profile.avatar_url = avatar_url
            else:
                profile = UserProfile(user_id=current_user.id, avatar_url=avatar_url)
                db.session.add(profile)
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('routes.profile'))
    
    num_favorites = len(current_user.favorites) if current_user.favorites else 0
    num_comments = len(current_user.comments) if current_user.comments else 0

    if current_user.profile and current_user.profile.avatar_url:
        avatar_path = os.path.join(current_app.static_folder, current_user.profile.avatar_url.replace('/', os.sep))

    return render_template('profile.html', form=form, user=current_user, num_favorites=num_favorites, num_comments=num_comments, avatars=avatars)


def fetch_game_from_igdb(game_id):
    url = 'https://api.igdb.com/v4/games'
    headers = {
        'Client-ID': current_app.config['TWITCH_CLIENT_ID'],
        'Authorization': f'Bearer {current_app.config["ACCESS_TOKEN"]}',
        'Accept': 'application/json'
    }
    data = f'fields id, name, cover.url, first_release_date, genres.name, platforms.name, summary; where id = {game_id};'
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    games = response.json()
    if games:
        return games[0]
    else:
        return None

def add_game_to_db(game_details):
    game = Game(
        id=game_details['id'],
        name=game_details['name'],
        description=game_details.get('summary', ''),
        release_date=datetime.utcfromtimestamp(game_details['first_release_date']).date() if 'first_release_date' in game_details else None,
        cover_url=game_details['cover']['url'] if 'cover' in game_details and 'url' in game_details['cover'] else None
    )
    db.session.add(game)
    db.session.commit()
    return game

@routes.route('/add_to_favorites', methods=['POST'])
@login_required
def add_to_favorites():
    try:
        print("Received request to add to favorites")  # Debugging
        data = request.get_json()
        print("Request data:", data)  # Debugging
        if not data or 'game_id' not in data:
            print("Missing game_id in request data")  # Debugging
            return jsonify({'error': 'Game ID is required!'}), 400

        game_id = int(data['game_id'])
        print("Game ID:", game_id)  # Debugging

        # Verify the existence of the game
        game = Game.query.get(game_id)
        if not game:
            print("Game not found in local DB, fetching from IGDB")  # Debugging
            game_details = fetch_game_from_igdb(game_id)
            if not game_details:
                print("Game not found in IGDB")  # Debugging
                return jsonify({'error': 'Game not found'}), 404
            print("Game fetched from IGDB, adding to local DB")  # Debugging
            game = add_game_to_db(game_details)
            print(f"Game {game.name} added to local DB")  # Debugging

        existing_favorite = Favorite.query.filter_by(user_id=current_user.id, game_id=game_id).first()
        if existing_favorite:
            print("Game is already in favorites")  # Debugging
            return jsonify({'message': 'Game is already in your favorites!'}), 200

        favorite = Favorite(user_id=current_user.id, game_id=game_id)
        db.session.add(favorite)
        db.session.commit()
        print("Game added to favorites")  # Debugging
        return jsonify({'message': 'Game added to favorites!'}), 200

    except Exception as e:
        db.session.rollback()
        print("Error adding game to favorites:", str(e))  # Debugging
        return jsonify({'error': 'Error adding game to favorites: ' + str(e)}), 500
    
    
@routes.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    try:
        data = request.get_json()
        if not data or 'game_id' not in data:
            return jsonify({'error': 'Game ID is required!'}), 400

        game_id = int(data['game_id'])
        game = Game.query.get(game_id)
        if not game:
            game_details = fetch_game_from_igdb(game_id)
            if not game_details:
                return jsonify({'error': 'Game not found'}), 404
            game = add_game_to_db(game_details)

        favorite = Favorite.query.filter_by(user_id=current_user.id, game_id=game_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({'message': 'Game removed from favorites!', 'action': 'removed'}), 200
        else:
            new_favorite = Favorite(user_id=current_user.id, game_id=game_id)
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({'message': 'Game added to favorites!', 'action': 'added'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error toggling favorite: ' + str(e)}), 500

@routes.app_template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    return datetime.fromtimestamp(value).strftime(format)
