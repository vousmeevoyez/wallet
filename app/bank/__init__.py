from flask import Blueprint

bp = Blueprint('bank', __name__)

from app.bank import handler, routes
