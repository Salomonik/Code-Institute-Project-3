import os
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash, current_app
from werkzeug.utils import secure_filename
from project import db
from project.forms import RegistrationForm, LoginForm, UpdateProfileForm
from project.models import User, Game, Favorite, Comment, Like, Friend, GameGenre, GameGenreAssociation, UserProfile
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename




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
        # Pobierz client_id i client_secret z konfiguracji aplikacji
        
        client_id = current_app.config['TWITCH_CLIENT_ID']
        client_secret = current_app.config['TWITCH_CLIENT_SECRET']
        
        # Uzyskaj access_token i przechowaj go w konfiguracji aplikacji
        
        access_token = get_igdb_access_token(client_id, client_secret)
        current_app.config['ACCESS_TOKEN'] = access_token
        
        # Fetch popular games
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

@routes.route('/get_games', methods=['GET'])
def get_games():
    try:
        game_name = request.args.get('game_name')
        platform = request.args.get('platform')
        url = 'https://api.igdb.com/v4/games'
        headers = {
            'Client-ID': current_app.config['TWITCH_CLIENT_ID'],  # Używaj client_id z konfiguracji aplikacji
            'Authorization': f'Bearer {current_app.config["ACCESS_TOKEN"]}',  # Użyj access_token z current_app.config
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
            'Client-ID': current_app.config['TWITCH_CLIENT_ID'],  # Używaj client_id z konfiguracji aplikacji
            'Authorization': f'Bearer {current_app.config["ACCESS_TOKEN"]}',  # Użyj access_token z current_app.config
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
            'Client-ID': current_app.config['TWITCH_CLIENT_ID'],  # Używaj client_id z konfiguracji aplikacji
            'Authorization': f'Bearer {current_app.config["ACCESS_TOKEN"]}',  # Użyj access_token z current_app.config
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

@routes.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
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
        avatar = request.form.get('selected_avatar')
        if avatar:
            avatar_url = os.path.join('profile_pics', avatar)
            if current_user.profile:
                current_user.profile.avatar_url = avatar_url
            else:
                profile = UserProfile(user_id=current_user.id, avatar_url=avatar_url)
                db.session.add(profile)
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('routes.profile'))     

    # Initialize num_favorites
    num_favorites = 0
    
    # Calculate number of favorites
    if current_user.favorites:
        num_favorites = len(current_user.favorites)
        
    num_comments = 0
    
    if current_user.comments:
        num_comments = len(current_user.comments)
    return render_template('profile.html', form=form, user=current_user, num_favorites=num_favorites, num_comments=num_comments,avatars=avatars)






@routes.route('/add_to_favorites', methods=['POST'])
@login_required
def add_to_favorites():
    game_id = request.form.get('game_id')
    if game_id:
        favorite = Favorite(user_id=current_user.id, game_id=game_id)
        db.session.add(favorite)
        try:
            db.session.commit()
            flash('Game added to favorites!', 'success')
        except IntegrityError:
            db.session.rollback()
            flash('This game is already in your favorites.', 'danger')
    return redirect(url_for('routes.get_games'))



# Definiowanie filtra dateformat
@routes.app_template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    return datetime.fromtimestamp(value).strftime(format)
