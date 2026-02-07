from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models import Project

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Redirect naar juiste dashboard op basis van rol"""
    if current_user.is_freelancer():
        return render_template('main/freelancer_dashboard.html', 
                             projects=current_user.owned_projects.order_by(Project.created_at.desc()).all())
    else:
        return render_template('main/client_dashboard.html',
                             projects=current_user.assigned_projects.order_by(Project.created_at.desc()).all())


@main_bp.route('/dashboard/freelancer')
@login_required
def freelancer_dashboard():
    """Dashboard voor freelancers"""
    if not current_user.is_freelancer():
        abort(403)  # Forbidden
    
    projects = current_user.owned_projects.order_by(Project.created_at.desc()).all()
    return render_template('main/freelancer_dashboard.html', projects=projects)


@main_bp.route('/dashboard/client')
@login_required
def client_dashboard():
    """Dashboard voor clients"""
    if not current_user.is_client():
        abort(403)  # Forbidden
    
    projects = current_user.assigned_projects.order_by(Project.created_at.desc()).all()
    return render_template('main/client_dashboard.html', projects=projects)