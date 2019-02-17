#!/bin/bash

# this is custom bash script to run flask in prod app because we need to run the flask
# using uwsgi

make clean
make upgrade
make init
uwsgi --http :5000 --wsgi-file manage.py --callable app --master --processes 4 --threads 2