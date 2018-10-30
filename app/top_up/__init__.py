from flask import Blueprint

bp = Blueprint('top_up', __name__)

from app.top_up import routes
