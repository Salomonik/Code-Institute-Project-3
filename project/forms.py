from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField,TextAreaField, StringField, TextAreaField, DateField, URLField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, URL
from project.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
def validate_username(self, username):
    user = User.query.filter_by(username = username.data).first()
    if user:
        raise ValidationError('That username is taken. Please choose different one.')

def validate_email(self, email):
    user = User.query.filter_by(email = email.data).first()
    if user:
        raise ValidationError('That email is taken. Please choose different one.')
    
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class UpdateProfileForm(FlaskForm):
    selected_avatar = HiddenField('Selected Avatar', validators=[DataRequired()])
    submit = SubmitField('Update')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')
    
class AddGameForm(FlaskForm):
    name = StringField('Game Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    release_date = DateField('Release Date', format='%Y-%m-%d', validators=[Optional()])
    cover_url = URLField('Cover Image URL', validators=[Optional(), URL()])
    platforms = SelectMultipleField('Platforms', validators=[Optional()])
    genres = SelectMultipleField('Genres', validators=[Optional()])
    game_modes = SelectMultipleField('Game Modes', validators=[Optional()])
    involved_companies = TextAreaField('Involved Companies', validators=[Optional()])
    storyline = TextAreaField('Storyline', validators=[Optional()])
    rating = StringField('Rating', validators=[Optional()])  # Może być FloatField jeśli chcesz przechowywać ocenę jako liczbę zmiennoprzecinkową
    submit = SubmitField('Add Game')