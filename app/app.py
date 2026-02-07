from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- CONFIGURATIE ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_geheim_productie_wachtwoord'
# Hier maken we de database aan (een bestand genaamd klantsync.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///klantsync.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODELS (DE STRUCTUUR) ---
# Dit bepaalt hoe de data wordt opgeslagen

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Nieuw')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relatie met updates (één project heeft meerdere updates)
    updates = db.relationship('Update', backref='project', lazy=True)

class Update(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Voor nu simuleren we nog steeds login, maar in V3 maken we dit echt met wachtwoorden
    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            flash(f'Welkom terug, {username}!', 'success')
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # HAAL PROJECTEN UIT DE DATABASE IN PLAATS VAN EEN LIJST
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('dashboard.html', projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@app.route('/create-project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        client = request.form.get('client_name')
        name = request.form.get('project_name')
        desc = request.form.get('description')
        
        # MAAK EEN NIEUW PROJECT AAN IN DE DATABASE
        new_project = Project(client_name=client, project_name=name, description=desc)
        db.session.add(new_project)
        db.session.commit()
        
        flash('Project succesvol aangemaakt!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('create_project.html') # Deze maken we zo

@app.route('/add-update/<int:project_id>', methods=['POST'])
def add_update(project_id):
    project = Project.query.get_or_404(project_id)
    content = request.form.get('update_text')
    
    if content:
        new_update = Update(content=content, project_id=project.id)
        db.session.add(new_update)
        db.session.commit()
        flash('Update geplaatst', 'success')
        
    return redirect(url_for('project_detail', project_id=project.id))

# --- DATABASE INITIALISATIE ---
# Dit stukje code zorgt ervoor dat de database wordt aangemaakt als je de app start
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)