import os
from flask import Blueprint, render_template, session, request, jsonify, url_for, redirect, flash, current_app
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from project import db
from project.forms import RegistrationForm, LoginForm, UpdateProfileForm, CommentForm, AddGameForm
from project.models import User, Game, Comment, UserProfile, favorites
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import logging

logging.basicConfig(level=logging.DEBUG)

# Define Blueprint for routing
routes = Blueprint('routes', __name__)

# Retrieve environment variables
CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')

# Function to get access token from IGDB
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
        
        # Get access token
        access_token = get_igdb_access_token(client_id, client_secret)
        current_app.config['ACCESS_TOKEN'] = access_token
        
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
        
        # Fetch popular games from IGDB
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        popular_games = response.json()
        
        # Pobierz listę usuniętych gier
        deleted_games = Game.query.with_entities(Game.id).filter_by(is_deleted=True).all()
        deleted_game_ids = {game.id for game in deleted_games}

        # Filtruj usunięte gry
        filtered_popular_games = [game for game in popular_games if game['id'] not in deleted_game_ids]
        
        # Modyfikacja URL obrazków dla lepszego wyświetlania
        modify_images(filtered_popular_games)
        favorite_game_ids = [fav.id for fav in current_user.favorites] if current_user.is_authenticated else []

        return render_template('index.html', popular_games=filtered_popular_games, favorite_game_ids=favorite_game_ids)
    except Exception as e:
        print("Error fetching popular games:", e)
        return render_template('error.html', error=str(e))


# Function to modify image URL size
def modify_image_url(url, size):
    sizes = ["t_thumb", "t_cover_small", "t_logo_med", "t_screenshot_med", "t_cover_big", "t_screenshot_big", "t_screenshot_huge", "t_720p", "t_1080p"]
    for s in sizes:
        if s in url:
            return url.replace(s, size)
    return url

# Function to modify images in game details
def modify_images(game_details):
    for game in game_details:
        if 'cover' in game:
            game['cover']['url'] = modify_image_url(game['cover']['url'], 't_cover_big')
        if 'screenshots' in game:
            for screenshot in game['screenshots']:
                screenshot['url'] = modify_image_url(screenshot['url'], 't_screenshot_big')

# Route to get games based on search criteria
@routes.route('/get_games', methods=['GET'])
def get_games():
    try:
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
        
        # Fetch games based on search criteria
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        game_info = response.json()
        
        # Pobierz listę usuniętych gier
        deleted_games = Game.query.with_entities(Game.id).filter_by(is_deleted=True).all()
        deleted_game_ids = {game.id for game in deleted_games}

        # Filtruj usunięte gry
        filtered_game_info = [game for game in game_info if game['id'] not in deleted_game_ids]
        
        # Modyfikacja URL obrazków dla lepszego wyświetlania
        modify_images(filtered_game_info)
        favorite_game_ids = [fav.id for fav in current_user.favorites] if current_user.is_authenticated else []
        return render_template('games.html', game_info=filtered_game_info, favorite_game_ids=favorite_game_ids)
    except Exception as e:
        print("Error fetching game data:", e)
        return render_template('error.html', error=str(e))


   
   
   
   # game_details = fetch_game_details(game_id)  # Assume a function `fetch_game_details` handles API logic
# Route for game details
@routes.route('/game_details/<int:game_id>', methods=['GET', 'POST'])
def game_details(game_id):
    logging.debug(f"Accessing game details for game_id {game_id}")
    form = CommentForm()

    # Pobierz szczegóły gry z lokalnej bazy danych
    game = Game.query.filter_by(id=game_id).first()

    # Sprawdź, czy gra istnieje i czy nie jest oznaczona jako usunięta
    if not game or game.is_deleted:
        logging.warning(f"Game with id {game_id} not found or is marked as deleted")
        return render_template('404.html'), 404

    # Użyj `fetch_game_details`, aby uzyskać więcej informacji o grze z API lub bazy
    game_details = fetch_game_details(game_id)
    
    if game_details is None:
        logging.error(f"Failed to retrieve game details for game_id {game_id}")
        flash('Nie udało się pobrać szczegółów gry.', 'danger')
        return render_template('error.html', error="Nie udało się pobrać szczegółów gry.")
    
    logging.debug(f"Game details retrieved successfully for game_id {game_id}")

    if form.validate_on_submit():
        if current_user.is_authenticated:
            comment = Comment(content=form.content.data, user_id=current_user.id, game_id=game_id)
            db.session.add(comment)
            db.session.commit()
            flash('Your comment has been added!', 'success')
        else:
            flash('You need to be logged in to comment.', 'danger')
        return redirect(url_for('routes.game_details', game_id=game_id))

    comments = Comment.query.filter_by(game_id=game_id).order_by(Comment.created_at.desc()).all()
    favorite_game_ids = [fav.id for fav in current_user.favorites] if current_user.is_authenticated else []

    return render_template('game_details.html', game_details=game_details, form=form, comments=comments, favorite_game_ids=favorite_game_ids)





# Function to fetch game details from IGDB
def fetch_game_details(game_id):
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

        logging.debug(f"Sending request to IGDB for game_id {game_id}")
        logging.debug(f"Request data: {data}")
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        game_details = response.json()
        logging.debug(f"Response received: {game_details}")
        
        if not game_details:
            logging.error(f"No game details found for game_id {game_id}")
            return None
        
        game_details = game_details[0]  # Assume the response is a list containing one element
        modify_images([game_details])  # Modify image URLs
        return game_details
    
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException while fetching game details for game_id {game_id}: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error while fetching game details for game_id {game_id}: {e}")
        return None


# Route to suggest games based on a query
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

# Route for user registration
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

# Route for user login
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

# Route for user logout
@routes.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

# Route for user profile
@routes.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    form = UpdateProfileForm()
    user = User.query.get_or_404(user_id)
    avatars = os.listdir(os.path.join(current_app.static_folder, 'profile_pics'))

    if user.id == current_user.id and form.validate_on_submit():
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
            return redirect(url_for('routes.profile', user_id=current_user.id))

    num_favorites = len(user.favorites) if user.favorites else 0
    num_comments = len(user.comments) if user.comments else 0

    favorite_games = user.favorites if user.favorites else []
    for game in favorite_games:
        if game.cover_url:
            game.cover_url = modify_image_url(game.cover_url, 't_cover_big')

    return render_template('profile.html', form=form, user=user, num_favorites=num_favorites, num_comments=num_comments, avatars=avatars, favorite_games=favorite_games)



# Function to fetch game details from IGDB
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

# Function to add game to the database
def add_game_to_db(game_details):
    game = Game(
        id=game_details['id'],
        name=game_details['name'],
        description=game_details.get('summary', ''),
        release_date=datetime.fromtimestamp(game_details['first_release_date']).date() if 'first_release_date' in game_details else None,
        cover_url=game_details['cover']['url'] if 'cover' in game_details and 'url' in game_details['cover'] else None
    )
    db.session.add(game)
    db.session.commit()
    return game

# Route to add a game to favorites
@routes.route('/add_to_favorites', methods=['POST'])
@login_required
def add_to_favorites():
    try:
        data = request.get_json()
        if not data or 'game_id' not in data:
            return jsonify({'error': 'Game ID is required!', 'category': 'error'}), 400

        game_id = int(data['game_id'])
        game = Game.query.get(game_id)
        if not game:
            game_details = fetch_game_from_igdb(game_id)
            if not game_details:
                return jsonify({'error': 'Game not found', 'category': 'error'}), 404
            game = add_game_to_db(game_details)

        existing_favorite = db.session.query(favorites).filter_by(user_id=current_user.id, game_id=game_id).first()
        if existing_favorite:
            return jsonify({'message': 'Game is already in your favorites!', 'category': 'info'}), 200

        db.session.execute(favorites.insert().values(user_id=current_user.id, game_id=game_id))
        db.session.commit()
        return jsonify({'message': 'Game added to favorites!', 'category': 'success'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error adding game to favorites: ' + str(e), 'category': 'error'}), 500

# Route to toggle a game as favorite
@routes.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    try:
        data = request.get_json()
        if not data or 'game_id' not in data:
            return jsonify({'error': 'Game ID is required!', 'category': 'error'}), 400

        game_id = int(data['game_id'])
        game = Game.query.get(game_id)
        if not game:
            game_details = fetch_game_from_igdb(game_id)
            if not game_details:
                return jsonify({'error': 'Game not found', 'category': 'error'}), 404
            game = add_game_to_db(game_details)

        favorite = db.session.query(favorites).filter_by(user_id=current_user.id, game_id=game_id).first()
        if favorite:
            db.session.execute(favorites.delete().where(favorites.c.user_id == current_user.id).where(favorites.c.game_id == game_id))
            db.session.commit()
            flash('Game removed from favorites!', 'success')
            return jsonify({'message': 'Game removed from favorites!', 'action': 'removed', 'category': 'success'}), 200
        else:
            db.session.execute(favorites.insert().values(user_id=current_user.id, game_id=game_id))
            db.session.commit()
            flash('Game added to favorites!', 'success')
            return jsonify({'message': 'Game added to favorites!', 'action': 'added', 'category': 'success'}), 200

    except Exception as e:
        db.session.rollback()
        flash('Error toggling favorite: ' + str(e), 'error')
        return jsonify({'error': 'Error toggling favorite: ' + str(e), 'category': 'error'}), 500

# Custom template filter for date formatting
@routes.app_template_filter('dateformat')
def dateformat(value, format='%Y-%m-%d'):
    return datetime.fromtimestamp(value).strftime(format)

# Route to clear flash messages
@routes.route('/clear_flash_messages', methods=['POST'])
def clear_flash_messages():
    session.pop('_flashes', None)
    return jsonify({'status': 'success'})

# Route to delete a comment
@routes.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash('You are not authorized to delete this comment.', 'danger')
        return redirect(url_for('routes.game_details', game_id=comment.game_id))
    
    db.session.delete(comment)
    db.session.commit()
    flash('Your comment has been deleted.', 'success')
    return redirect(url_for('routes.game_details', game_id=comment.game_id))

# Route to update a comment
@routes.route('/update_comment/<int:comment_id>', methods=['POST'])
@login_required
def update_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        return jsonify({'error': 'You are not authorized to edit this comment.'}), 403
    
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Content is required.'}), 400

    comment.content = data['content']
    comment.updated_at = datetime.now()
    db.session.commit()
    return jsonify({'message': 'Comment updated successfully.', 'content': comment.content}), 200

@routes.route('/delete_game/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    try:
        game = Game.query.get_or_404(game_id)
        game.is_deleted = True
        db.session.commit()

        flash('Game has been successfully deleted.', 'success')
        return redirect(url_for('routes.index'))
    except Exception as e:
        db.session.rollback()
        flash('Error deleting the game: ' + str(e), 'danger')
        return redirect(url_for('routes.index'))


@routes.route('/add_game', methods=['GET', 'POST'])
@login_required
def add_game():
    form = AddGameForm()
    if form.validate_on_submit():
        new_game = Game(
            name=form.name.data,
            description=form.description.data,
            release_date=form.release_date.data,
            cover_url=form.cover_url.data,
        )
        db.session.add(new_game)
        db.session.commit()
        flash('Game added successfully!', 'success')
        return redirect(url_for('routes.index'))
    
    return render_template('add_game.html', form=form)

