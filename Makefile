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

payment-worker:
	celery worker -A task.worker.celery --loglevel=info --autoscale=4,2 -Q payment -n paymentworker@%h

bank-worker:
	celery worker -A task.worker.celery --loglevel=info --autoscale=4,2 -Q bank -n bankworker@%h

transaction-worker:
	celery worker -A task.worker.celery --loglevel=info --autoscale=4,2 -Q transaction -n transactionworker@h

utility-worker:
	celery worker -A task.worker.celery --loglevel=info --autoscale=4,2 -Q utility -n utilityworker@%h

flower:
	flower -A task.worker.celery --port=5555
