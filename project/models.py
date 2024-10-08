from . import db
from datetime import datetime
from flask_login import UserMixin

# Tabela pomocnicza dla relacji wiele-do-wielu między użytkownikami a grami
favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    comments = db.relationship('Comment', back_populates='author', lazy=True)
    favorites = db.relationship('Game', secondary=favorites, backref=db.backref('favorited_by', lazy='dynamic'))
    profile = db.relationship('UserProfile', uselist=False, backref='user_profile')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    cover_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_local = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Game {self.name}>'

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    author = db.relationship('User', back_populates='comments')
    game = db.relationship('Game', backref='game_comments')

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    avatar_url = db.Column(db.String(256))

