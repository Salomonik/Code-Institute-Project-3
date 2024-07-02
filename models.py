from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password_hash = db.Column(db.String(128), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.UTC)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
class Game(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(128), nullable = False)
    description = db.Column(db.Text)
    release_date = db.Column(db.Date)
    cover_url = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default = datetime.UTC)
    
    def __repr__(self):
        return f'<Game {self.name}'
    
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.UTC)
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable = False)
    game_id = db.Column(db.Integer, ForeignKey('game.id'), nullable = False)
    content = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.UTC)

class Like(db.Model):
    id db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable = False)
    comment_id = db.Column(db.Integer, ForeignKey('comment.id'), nullable = False)
    created_at = db.Column(db.DateTime, defaulf = datetime.UTC)
    

    