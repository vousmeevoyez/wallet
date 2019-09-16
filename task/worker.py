"""
    Start Celery worker by creating a new flask application context and make this accessible through all task
"""
import os
from app.api import create_app, celery

app = create_app(os.getenv("ENVIRONMENT") or "test")
app.app_context().push()
