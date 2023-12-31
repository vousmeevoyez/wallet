#!/bin/bash

# this is custom bash script to run flask in prod app because we need to run the flask
# using uwsgi

make clean
make migrate
make upgrade
make init
#uwsgi --http-socket flask:5000 --wsgi-file manage.py --callable app --master --processes 4 --threads 2  --disable-logging --enable-threads --vacuum
gunicorn -b flask:5000 -w 4 manage:app --log-level INFO --access-logfile -
