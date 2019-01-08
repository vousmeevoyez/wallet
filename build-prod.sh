#!/bin/bash

make build
uwsgi --ini app.ini
