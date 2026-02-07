from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.models import db, Project, Update, User, ClientInvite, ClientFreelancerRelation
from app.projects.forms import ProjectForm

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if not current_user.is_freelancer():
        flash('Alleen freelancers kunnen projecten aanmaken', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = ProjectForm()
    
    # Haal alle clients van deze freelancer op
    my_client_relations = ClientFreelancerRelation.query.filter_by(freelancer_id=current_user.id).all()
    my_client_ids = [r.client_id for r in my_client_relations]
    my_clients = User.query.filter(User.id.in_(my_client_ids)).all() if my_client_ids else []
    
    # Populate dropdown
    form.existing_client_id.choices = [(0, '-- Geen client toewijzen --')] + [(c.id, f"{c.username} ({c.email})") for c in my_clients]
    
    if form.validate_on_submit():
        project = Project(
            client_name=form.client_name.data,
            project_name=form.project_name.data,
            description=form.description.data,
            status=form.status.data,
            freelancer_id=current_user.id
        )
        
        # Check welke mode geselecteerd is
        if form.client_mode.data == 'existing':
            # Bestaande client geselecteerd
            if form.existing_client_id.data and form.existing_client_id.data != 0:
                project.client_id = form.existing_client_id.data
                flash('✅ Project aangemaakt en gekoppeld aan bestaande client', 'success')
        
        elif form.client_mode.data == 'new' and form.client_email.data:
            # Nieuwe client uitnodigen
            client_email = form.client_email.data.lower()
            existing_client = User.query.filter_by(email=client_email, role='client').first()
            
            if existing_client:
                # Client bestaat al
                project.client_id = existing_client.id
                
                # Maak relatie
                relation = ClientFreelancerRelation.query.filter_by(
                    client_id=existing_client.id,
                    freelancer_id=current_user.id
                ).first()
                
                if not relation:
                    relation = ClientFreelancerRelation(
                        client_id=existing_client.id,
                        freelancer_id=current_user.id
                    )
                    db.session.add(relation)
                
                flash(f'✅ Project aangemaakt en gekoppeld aan {existing_client.username}', 'success')
            else:
                # Client bestaat nog niet - maak invite
                db.session.add(project)
                db.session.flush()  # Get project.id
                
                existing_invite = ClientInvite.query.filter_by(
                    email=client_email,
                    freelancer_id=current_user.id,
                    status='pending'
                ).first()
                
                if not existing_invite:
                    invite = ClientInvite(
                        email=client_email,
                        token=ClientInvite.generate_token(),
                        freelancer_id=current_user.id,
                        project_id=project.id
                    )
                    db.session.add(invite)
                    flash(f'📧 Uitnodiging verstuurd naar {client_email}', 'info')
                else:
                    # Update bestaande invite met project_id
                    existing_invite.project_id = project.id
                    flash(f'ℹ️ Bestaande uitnodiging gekoppeld aan dit project', 'info')
        
        db.session.add(project)
        db.session.commit()
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('projects/new.html', form=form, my_clients=my_clients)


@projects_bp.route('/<int:project_id>')
@login_required
def detail(project_id):
    project = Project.query.get_or_404(project_id)
    
    if current_user.is_freelancer():
        if project.freelancer_id != current_user.id:
            abort(403)
    elif current_user.is_client():
        if project.client_id != current_user.id:
            abort(403)
    else:
        abort(403)
    
    updates = project.updates.order_by(Update.created_at.desc()).all()
    
    return render_template('projects/detail.html', project=project, updates=updates)


@projects_bp.route('/<int:project_id>/add-update', methods=['POST'])
@login_required
def add_update(project_id):
    project = Project.query.get_or_404(project_id)
    
    has_access = False
    if current_user.is_freelancer() and project.freelancer_id == current_user.id:
        has_access = True
    elif current_user.is_client() and project.client_id == current_user.id:
        has_access = True
    
    if not has_access:
        abort(403)
    
    content = request.form.get('content')
    
    if not content or len(content.strip()) == 0:
        flash('Update mag niet leeg zijn', 'danger')
        return redirect(url_for('projects.detail', project_id=project_id))
    
    update = Update(
        content=content.strip(),
        project_id=project_id,
        author_id=current_user.id
    )
    
    db.session.add(update)
    db.session.commit()
    
    flash('✅ Update geplaatst!', 'success')
    return redirect(url_for('projects.detail', project_id=project_id))


@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not current_user.is_freelancer() or project.freelancer_id != current_user.id:
        abort(403)
    
    form = ProjectForm(obj=project)
    
    # Haal clients op voor dropdown
    my_client_relations = ClientFreelancerRelation.query.filter_by(freelancer_id=current_user.id).all()
    my_client_ids = [r.client_id for r in my_client_relations]
    my_clients = User.query.filter(User.id.in_(my_client_ids)).all() if my_client_ids else []
    
    form.existing_client_id.choices = [(0, '-- Geen client toewijzen --')] + [(c.id, f"{c.username} ({c.email})") for c in my_clients]
    
    if form.validate_on_submit():
        project.client_name = form.client_name.data
        project.project_name = form.project_name.data
        project.description = form.description.data
        project.status = form.status.data
        
        if form.client_mode.data == 'existing':
            if form.existing_client_id.data and form.existing_client_id.data != 0:
                project.client_id = form.existing_client_id.data
        elif form.client_mode.data == 'new' and form.client_email.data:
            client_email = form.client_email.data.lower()
            existing_client = User.query.filter_by(email=client_email, role='client').first()
            
            if existing_client:
                if project.client_id != existing_client.id:
                    project.client_id = existing_client.id
                    
                    relation = ClientFreelancerRelation.query.filter_by(
                        client_id=existing_client.id,
                        freelancer_id=current_user.id
                    ).first()
                    
                    if not relation:
                        relation = ClientFreelancerRelation(
                            client_id=existing_client.id,
                            freelancer_id=current_user.id
                        )
                        db.session.add(relation)
                    
                    flash(f'✅ Project bijgewerkt en gekoppeld aan {existing_client.username}', 'success')
        
        db.session.commit()
        flash('✅ Project succesvol bijgewerkt!', 'success')
        return redirect(url_for('projects.detail', project_id=project.id))
    
    # Pre-fill
    if project.client:
        form.existing_client_id.data = project.client_id
        form.client_email.data = project.client.email
    
    return render_template('projects/edit.html', form=form, project=project, my_clients=my_clients)


@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not current_user.is_freelancer() or project.freelancer_id != current_user.id:
        abort(403)
    
    project_name = project.project_name
    
    db.session.delete(project)
    db.session.commit()
    
    flash(f'🗑️ Project "{project_name}" verwijderd', 'success')
    return redirect(url_for('main.dashboard'))