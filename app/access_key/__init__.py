from flask import Blueprint

bp = Blueprint('access_key', __name__)

from app.access_key import routes
