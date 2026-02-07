from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Gebruikersnaam', validators=[
        DataRequired(message='Gebruikersnaam is verplicht'),
        Length(min=3, max=80, message='Gebruikersnaam moet tussen 3 en 80 karakters zijn')
    ])
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is verplicht'),
        Email(message='Ongeldig emailadres')
    ])
    
    # NIEUW: Role selectie
    role = SelectField('Ik ben een', choices=[
        ('freelancer', 'Freelancer / Bedrijf'),
        ('client', 'Klant')
    ], validators=[DataRequired()])
    
    password = PasswordField('Wachtwoord', validators=[
        DataRequired(message='Wachtwoord is verplicht'),
        Length(min=8, message='Wachtwoord moet minimaal 8 karakters zijn')
    ])
    
    password2 = PasswordField('Herhaal Wachtwoord', validators=[
        DataRequired(message='Herhaal je wachtwoord'),
        EqualTo('password', message='Wachtwoorden komen niet overeen')
    ])
    
    submit = SubmitField('Registreren')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Deze gebruikersnaam is al in gebruik.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError('Dit emailadres is al geregistreerd.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is verplicht'),
        Email(message='Ongeldig emailadres')
    ])
    
    password = PasswordField('Wachtwoord', validators=[
        DataRequired(message='Wachtwoord is verplicht')
    ])
    
    remember_me = BooleanField('Onthoud mij')
    submit = SubmitField('Inloggen')