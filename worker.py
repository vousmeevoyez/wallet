"""
    Celery Worker
"""
import os

from celery import Celery

from app.api import create_app

def make_celery(app):
    """ create celery instances """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL'],
        include=["task.bank.tasks"]
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery
#end def

app = create_app(os.getenv("ENVIRONMENT") or 'dev')
celery = make_celery(app)
app.app_context().push()
