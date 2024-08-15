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
from sqlalchemy import func
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
    # Sprawdź, czy game_details to lista (więcej niż jedna gra)
    if isinstance(game_details, list):
        for game in game_details:
            if 'cover' in game and 'url' in game['cover']:
                game['cover']['url'] = modify_image_url(game['cover']['url'], 't_cover_big')
            if 'screenshots' in game:
                for screenshot in game['screenshots']:
                    screenshot['url'] = modify_image_url(screenshot['url'], 't_screenshot_big')
    # Jeśli to pojedyncza gra, zastosuj modyfikację bezpośrednio
    elif isinstance(game_details, dict):
        if 'cover' in game_details and 'url' in game_details['cover']:
            game_details['cover']['url'] = modify_image_url(game_details['cover']['url'], 't_cover_big')
        if 'screenshots' in game_details:
            for screenshot in game_details['screenshots']:
                screenshot['url'] = modify_image_url(screenshot['url'], 't_screenshot_big')

# Route to get games based on search criteria
@routes.route('/get_games', methods=['GET'])
def get_games():
    try:
        game_name = request.args.get('game_name')
        platform = request.args.get('platform')
        
        # Najpierw wyszukaj w lokalnej bazie danych
        local_games = Game.query.filter(
            Game.name.ilike(f'%{game_name}%')
        ).all()

        if local_games:
            # Tworzenie listy słowników dla gier z lokalnej bazy danych
            filtered_game_info = []
            for game in local_games:
                game_dict = {
                    'id': game.id,
                    'name': game.name,
                    'summary': game.description,
                    'first_release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
                    'cover': {'url': game.cover_url} if game.cover_url else None
                }
                filtered_game_info.append(game_dict)
        else:
            # Jeśli brak gier w lokalnej bazie danych, wykonaj zapytanie do API
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

    # Pobierz szczegóły gry bezpośrednio z API
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
        game_id = int(game_id)
        
        # Najpierw sprawdź lokalną bazę danych
        game = Game.query.get(game_id)
        if game and not game.is_deleted:
            # Przygotuj dane w formacie zgodnym z API IGDB
            game_details = {
                'id': game.id,
                'name': game.name,
                'summary': game.description,
                'first_release_date': game.release_date.strftime('%Y-%m-%d') if game.release_date else None,
                'cover': {'url': game.cover_url} if game.cover_url else None,
                'genres': [],  # Możesz dodać tutaj więcej szczegółów, jeśli są dostępne w lokalnej bazie
                'platforms': [],
                'storyline': game.description,
                'screenshots': [],
                'videos': [],
                'rating': None,
                'rating_count': None,
                'involved_companies': [],
                'game_modes': [],
                'themes': []
            }
            logging.debug(f"Local game details retrieved successfully for game_id {game_id}")
            return game_details

        # Jeśli gra nie istnieje lokalnie, pobierz dane z API IGDB
        logging.debug(f"Game with id {game_id} not found locally, fetching from IGDB API")

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
        
        game_details = game_details[0] 
        modify_images(game_details)# Zakładamy, że odpowiedź zawiera jeden element
        return game_details

    except ValueError as ve:
        logging.error(f"ValueError: game_id could not be converted to an integer: {ve}")
        return None
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
    user = User.query.get_or_404(user_id)
    
    # Check if the current user is trying to access their own profile
    if user.id != current_user.id:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('routes.index'))

    form = UpdateProfileForm()
    avatars = os.listdir(os.path.join(current_app.static_folder, 'profile_pics'))

    if form.validate_on_submit():
        # Update username if the user wants to change it
        new_username = form.username.data
        if new_username and new_username != current_user.username:
            current_user.username = new_username
            flash('Username updated successfully!', 'success')

        # Update avatar
        avatar = form.selected_avatar.data
        if avatar:
            avatar_url = 'profile_pics/' + avatar
            if current_user.profile:
                current_user.profile.avatar_url = avatar_url
            else:
                profile = UserProfile(user_id=current_user.id, avatar_url=avatar_url)
                db.session.add(profile)

        db.session.commit()
        return redirect(url_for('routes.profile', user_id=current_user.id))

    num_favorites = len(user.favorites) if user.favorites else 0
    num_comments = len(user.comments) if user.comments else 0

    favorite_games = user.favorites if user.favorites else []
    for game in favorite_games:
        if game.cover_url:
            game.cover_url = modify_image_url(game.cover_url, 't_cover_big')

    return render_template('profile.html', form=form, user=user, num_favorites=num_favorites, num_comments=num_comments, avatars=avatars, favorite_games=favorite_games)

@routes.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    try:
        user = User.query.get_or_404(current_user.id)
        
        # Delete all comments associated with the user
        Comment.query.filter_by(user_id=user.id).delete()

        # Delete user favorites if necessary
        db.session.execute(favorites.delete().where(favorites.c.user_id == user.id))
        
        # Delete the user profile
        if user.profile:
            db.session.delete(user.profile)
        
        # Finally, delete the user
        db.session.delete(user)
        db.session.commit()
        
        logout_user()
        flash('Your account has been successfully deleted.', 'success')
        return redirect(url_for('routes.index'))
    except Exception as e:
        db.session.rollback()
        flash('Error deleting your account: ' + str(e), 'danger')
        return redirect(url_for('routes.profile', user_id=current_user.id))


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
    if isinstance(value, (int, float)):
        # If it's a timestamp, convert it directly
        return datetime.fromtimestamp(value).strftime(format)
    elif isinstance(value, str):
        # Try to parse the string as a date
        try:
            dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime(format)
        except ValueError:
            # Return the original string if parsing fails
            return value
    else:
        return value

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
        # Ustal najwyższe ID gry w bazie danych, aby nadać nowe ID
        max_api_id = 1000000  # Zakładamy, że ID gier z API są mniejsze niż 1,000,000
        
        # Znajdź najwyższe ID lokalnej gry, które zostało już dodane
        max_local_id = db.session.query(func.max(Game.id)).filter(Game.id >= max_api_id).scalar()
        
        # Ustaw ID nowej gry na wartość większą niż maksymalne ID lokalne
        new_game_id = max_local_id + 1 if max_local_id else max_api_id + 1
        
        # Tworzenie nowej gry z ustalonym ID
        new_game = Game(
            id=new_game_id,
            name=form.name.data,
            description=form.description.data,
            release_date=form.release_date.data,
            cover_url=form.cover_url.data,
            is_local=True  # Dodajemy informację, że gra jest lokalna
        )
        db.session.add(new_game)
        db.session.commit()
        flash('Gra została dodana pomyślnie!', 'success')
        return redirect(url_for('routes.index'))
    return render_template('add_game.html', form=form)


@routes.route('/update_username/<int:user_id>', methods=['POST'])
@login_required
def update_username(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id != current_user.id:
        flash('You are not authorized to edit this profile.', 'danger')
        return redirect(url_for('routes.profile', user_id=user_id))

    new_username = request.form.get('username')
    if new_username:
        user.username = new_username
        db.session.commit()
        flash('Your username has been updated!', 'success')
    else:
        flash('Invalid username.', 'danger')

    return redirect(url_for('routes.profile', user_id=user_id))


