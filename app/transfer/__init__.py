from flask import Blueprint

bp = Blueprint('transfer', __name__)

from app.transfer import routes
