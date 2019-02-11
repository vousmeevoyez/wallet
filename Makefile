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
