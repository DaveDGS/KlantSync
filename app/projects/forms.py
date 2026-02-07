from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, RadioField
from wtforms.validators import DataRequired, Length, Email, Optional

class ProjectForm(FlaskForm):
    client_name = StringField('Klant Naam (Display)', validators=[
        DataRequired(message='Klant naam is verplicht'),
        Length(max=100)
    ])
    
    project_name = StringField('Project Naam', validators=[
        DataRequired(message='Project naam is verplicht'),
        Length(max=100)
    ])
    
    description = TextAreaField('Beschrijving', validators=[
        DataRequired(message='Beschrijving is verplicht')
    ])
    
    status = SelectField('Status', choices=[
        ('actief', 'Actief'),
        ('afgerond', 'Afgerond'),
        ('gepauzeerd', 'Gepauzeerd')
    ])
    
    # NIEUW: Keuze tussen bestaande client of nieuwe
    client_mode = RadioField('Client Toewijzing', choices=[
        ('existing', 'Selecteer bestaande client'),
        ('new', 'Nieuwe client uitnodigen')
    ], default='existing')
    
    # Dropdown voor bestaande clients
    existing_client_id = SelectField('Bestaande Client', coerce=int)
    
    # Email input voor nieuwe client
    client_email = StringField('Client Email', validators=[
        Optional(),
        Email(message='Ongeldig emailadres')
    ])
    
    submit = SubmitField('Project Opslaan')