from flask import Blueprint

bp = Blueprint('wallet', __name__)

from app.wallet import routes
