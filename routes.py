from flask import render_template, request
from . import app, db
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_games', methods=['GET'])
def get_games():
    game_name = request.args.get('game_name')
    return render_template('games.html')