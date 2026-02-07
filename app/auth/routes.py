from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from app.models import db, User
from app.auth.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # Redirect naar juiste dashboard op basis van rol
        if current_user.is_freelancer():
            return redirect(url_for('main.freelancer_dashboard'))
        else:
            return redirect(url_for('main.client_dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            role=form.role.data  # NIEUW: Sla rol op
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Account succesvol aangemaakt als {form.role.data}! Je kunt nu inloggen.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirect naar juiste dashboard op basis van rol
        if current_user.is_freelancer():
            return redirect(url_for('main.freelancer_dashboard'))
        else:
            return redirect(url_for('main.client_dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Ongeldig emailadres of wachtwoord', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        
        # Redirect naar juiste dashboard
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            if user.is_freelancer():
                next_page = url_for('main.freelancer_dashboard')
            else:
                next_page = url_for('main.client_dashboard')
        
        flash(f'Welkom terug, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('Je bent uitgelogd', 'info')
    return redirect(url_for('main.index'))