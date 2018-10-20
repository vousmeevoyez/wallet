from flask import Blueprint

bp = Blueprint('va', __name__)

from app.va import handler, routes
