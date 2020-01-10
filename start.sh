#!/bin/bash
set -e

echo "Start docker in which environment? [dev/prod]:"
read stage
if [ "$stage" == "dev" ]; then
	export ENV="dev"
	export APP_PORT=5000
	docker-compose up -d --build
else
	export ENV="prod"
	export APP_PORT=6000
	docker-compose up -d --build
fi
