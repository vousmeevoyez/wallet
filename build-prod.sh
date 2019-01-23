#!/bin/bash

# this is custom bash script to run flask in prod app because we need to run the flask
# using gunicorn

make clean
make upgrade
make init
gunicorn --workers 1 --bind :5000 manage:app --log-level=debug
