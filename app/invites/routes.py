from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user, login_user
from app.models import db, ClientInvite, User, ClientFreelancerRelation
from datetime import datetime

invites_bp = Blueprint('invites', __name__)

@invites_bp.route('/my-invites')
@login_required
def my_invites():
    """Overzicht van alle uitnodigingen (alleen voor freelancers)"""
    if not current_user.is_freelancer():
        abort(403)
    
    pending = ClientInvite.query.filter_by(
        freelancer_id=current_user.id,
        status='pending'
    ).order_by(ClientInvite.created_at.desc()).all()
    
    accepted = ClientInvite.query.filter_by(
        freelancer_id=current_user.id,
        status='accepted'
    ).order_by(ClientInvite.created_at.desc()).limit(10).all()
    
    return render_template('invites/my_invites.html', pending=pending, accepted=accepted)


@invites_bp.route('/accept/<token>', methods=['GET', 'POST'])
def accept_invite(token):
    """Client accepteert uitnodiging en registreert"""
    invite = ClientInvite.query.filter_by(token=token).first_or_404()
    
    # Check of invite expired is
    if invite.is_expired():
        flash('❌ Deze uitnodiging is verlopen', 'danger')
        return redirect(url_for('main.index'))
    
    # Check of invite al accepted is
    if invite.status == 'accepted':
        flash('✅ Deze uitnodiging is al gebruikt', 'info')
        return redirect(url_for('auth.login'))
    
    # Als user al ingelogd is en het een client is
    if current_user.is_authenticated:
        if current_user.is_client() and current_user.email.lower() == invite.email.lower():
            # Accepteer invite en koppel
            invite.status = 'accepted'
            
            # Maak relatie
            relation = ClientFreelancerRelation(
                client_id=current_user.id,
                freelancer_id=invite.freelancer_id
            )
            db.session.add(relation)
            
            # Koppel aan project als die er is
            if invite.project_id:
                project = invite.project
                project.client_id = current_user.id
            
            db.session.commit()
            
            flash(f'✅ Je bent gekoppeld aan {invite.freelancer.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('⚠️ Log uit en gebruik de uitnodigingslink opnieuw', 'warning')
            return redirect(url_for('main.index'))
    
    # Toon registratie pagina met pre-filled email
    return render_template('invites/accept.html', invite=invite)


@invites_bp.route('/register-from-invite/<token>', methods=['POST'])
def register_from_invite(token):
    """Verwerk registratie via invite"""
    invite = ClientInvite.query.filter_by(token=token).first_or_404()
    
    if invite.is_expired() or invite.status == 'accepted':
        flash('❌ Deze uitnodiging is niet meer geldig', 'danger')
        return redirect(url_for('main.index'))
    
    # Haal form data op
    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('password2')
    
    # Validatie
    errors = []
    if not username or len(username) < 3:
        errors.append('Gebruikersnaam moet minimaal 3 karakters zijn')
    if not password or len(password) < 8:
        errors.append('Wachtwoord moet minimaal 8 karakters zijn')
    if password != password2:
        errors.append('Wachtwoorden komen niet overeen')
    
    # Check of username/email al bestaat
    if User.query.filter_by(username=username).first():
        errors.append('Deze gebruikersnaam is al in gebruik')
    if User.query.filter_by(email=invite.email).first():
        errors.append('Dit emailadres is al geregistreerd')
    
    if errors:
        for error in errors:
            flash(error, 'danger')
        return render_template('invites/accept.html', invite=invite)
    
    # Maak client account aan
    user = User(
        username=username,
        email=invite.email.lower(),
        role='client'
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # Get user.id
    
    # Accepteer invite
    invite.status = 'accepted'
    
    # Maak relatie
    relation = ClientFreelancerRelation(
        client_id=user.id,
        freelancer_id=invite.freelancer_id
    )
    db.session.add(relation)
    
    # Koppel aan project
    if invite.project_id:
        project = invite.project
        project.client_id = user.id
    
    db.session.commit()
    
    # Log client in
    login_user(user)
    
    flash(f'✅ Account aangemaakt! Welkom bij {invite.freelancer.username}', 'success')
    return redirect(url_for('main.dashboard'))