#!/bin/bash
set -e

echo "Start docker in which environment? [dev/prod]:"
read stage
if [ "$stage" == "dev" ]; then
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
else
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
fi
