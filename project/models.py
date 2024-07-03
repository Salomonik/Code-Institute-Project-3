from . import db
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password_hash = db.Column(db.String(256), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now)
    comments = db.relationship('Comment', backref='author', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)
    friends = db.relationship('Friend', 
                              foreign_keys='[Friend.user_id]', 
                              backref='user', 
                              lazy=True)
    friend_of = db.relationship('Friend', 
                                foreign_keys='[Friend.friend_id]', 
                                backref='friend', 
                                lazy=True)
    profile = db.relationship('UserProfile', uselist=False, backref='user')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Game(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    cover_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default = datetime.now)
    favorites = db.relationship('Favorite', backref='game', lazy=True)
    
    def __repr__(self):
        return f'<Game {self.name}>'
    
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now)
    user = db.relationship('User', backref=db.backref('user_favorites', lazy=True))
    game = db.relationship('Game', backref=db.backref('game_favorites', lazy=True))
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable = False)
    content = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now)
    
class Friend(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    friend_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now)
    
class GameGenre(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64), unique = True, nullable = False)

class GameGenreAssociation(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable = False)
    genre_id = db.Column(db.Integer, db.ForeignKey('game_genre.id'), nullable = False)
    
class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    avatar_url = db.Column(db.String(256))
    bio = db.Column(db.Text)
    location = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default = datetime.now)