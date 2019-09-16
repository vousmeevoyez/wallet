"""
    Transaction Package Initialization
"""
# pylint: disable=wrong-import-position
from app.api.namespace import TransactionNamespace

api = TransactionNamespace.api  # pylint: disable=invalid-name
from app.api.transactions import routes
