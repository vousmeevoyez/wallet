# Modana Wallet

Modana Wallet is a system provide API for Modana system to interact with Local & External Bank and also provide balancing for every user transaction

## Code style
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

## Tech Used
<b>Built with</b>
- [Flask](http://flask.pocoo.org)
- [RabbitMQ](http://flask.pocoo.org)
- [Celery](http://flask.pocoo.org)
- [Requests](http://flask.pocoo.org)
- [Docker](https://www.docker.com)
- [Postgresql](https://www.postgresql.org)


## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Prerequisite

* Python 3 +
* PIP 
* Docker
* Docker Compose


### Running Locally

```bash
git clone https://gitlab.com/modana/wallet/wallet-be
pip install -r requirements-dev.txt
make run or python manage.py run
```

### Running via Docker Compose

to run just execute but make sure you choose and provide right env settings:
```bash
./start.sh
```

### Run Unittest + Coverage
Modana Wallet uses pytest so to run unittest and coverage you can just
```
make coverage
make tests
```

### Makefile
All commands that can be executed on the apps it's registered in Makefile
please checkout the makefile to know more.


## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 
version 1.0

## Authors

* ** Kelvin ** - (https://github.com/vousmeevoyez)
