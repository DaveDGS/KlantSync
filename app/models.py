from datetime import datetime, timedelta
import secrets
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model voor zowel freelancers als clients"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='freelancer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaties voor freelancers
    owned_projects = db.relationship('Project', foreign_keys='Project.freelancer_id', 
                                     backref='freelancer', lazy='dynamic', cascade='all, delete-orphan')
    
    # Relaties voor clients
    assigned_projects = db.relationship('Project', foreign_keys='Project.client_id', 
                                       backref='client', lazy='dynamic')
    
    # Updates die deze user heeft geschreven
    updates = db.relationship('Update', backref='author', lazy='dynamic')
    
    # NIEUW: Client-Freelancer relaties
    my_clients = db.relationship('ClientFreelancerRelation',
                                  foreign_keys='ClientFreelancerRelation.freelancer_id',
                                  backref='freelancer_user',
                                  lazy='dynamic')
    
    my_freelancers = db.relationship('ClientFreelancerRelation',
                                     foreign_keys='ClientFreelancerRelation.client_id',
                                     backref='client_user',
                                     lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_freelancer(self):
        return self.role == 'freelancer'
    
    def is_client(self):
        return self.role == 'client'
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Project(db.Model):
    """Project model met freelancer en client"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(100), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='actief')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    updates = db.relationship('Update', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.project_name}>'


class Update(db.Model):
    """Update/Comment model"""
    __tablename__ = 'updates'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Update {self.id} by User {self.author_id}>'


class ClientFreelancerRelation(db.Model):
    """Many-to-many relatie tussen clients en freelancers"""
    __tablename__ = 'client_freelancer_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('client_id', 'freelancer_id', name='unique_client_freelancer'),)
    
    def __repr__(self):
        return f'<Relation Client:{self.client_id} ↔ Freelancer:{self.freelancer_id}>'


class ClientInvite(db.Model):
    """Uitnodigingen van freelancer naar client"""
    __tablename__ = 'client_invites'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    
    freelancer = db.relationship('User', foreign_keys=[freelancer_id], backref='sent_invites')
    project = db.relationship('Project', backref='invites')
    
    @staticmethod
    def generate_token():
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        return f'<Invite {self.email} by Freelancer:{self.freelancer_id}>'