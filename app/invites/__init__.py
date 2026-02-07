from flask import Blueprint

invites_bp = Blueprint('invites', __name__)

from app.invites import routes