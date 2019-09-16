"""
    Package Initialization
"""
from app.api.namespace import PlanNamespace

api = PlanNamespace.api
from app.api.plans import routes
