from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms import BooleanField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=2, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(), Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Sign Up')
    
    is_host = BooleanField('ホストとして登録する')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Login')
    
class ProblemForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired()])
    description = StringField('説明', validators=[DataRequired()])
    tile_options = StringField('選択肢（カンマ区切り）', validators=[DataRequired()])
    submit = SubmitField('問題を作成')
