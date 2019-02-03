#!/bin/bash

# this is custom bash script to run flask in prod app because we need to run the flask
# using uwsgi

make build
uwsgi --http :5000 --wsgi-file manage.py --callable app --master --processes 2 --threads 1
