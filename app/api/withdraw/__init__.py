from flask import Blueprint

bp = Blueprint('withdraw', __name__)

from app.withdraw import routes
