from flask import Blueprint

bp = Blueprint('callback', __name__)

from app.callback import routes, helper
