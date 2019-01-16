"""
    Auth Package Initialization
"""
#pylint: disable=wrong-import-position
from app.api.namespace import AuthNamespace
api = AuthNamespace.api #pylint: disable=invalid-name
from app.api.authentication import routes, decorator
