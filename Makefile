clean:
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.log' -delete

upgrade:
	python manage.py db upgrade

tests:
	python manage.py test

run:
	python manage.py run

init:
	python manage.py init

shell:
	python manage.py shell

coverage:
	coverage run --source app/api -m unittest discover -s app/test/

worker:
	celery worker -A task.worker.celery --loglevel=info --concurrency=2

scheduler:
	celery beat -A task.worker.celery --loglevel=info

flower:
	flower -A task.worker.celery --port=5555
