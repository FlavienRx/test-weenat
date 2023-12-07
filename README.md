# Installation

## Requirements

To install project, you need to have Python 3.11, [Pipenv](https://pipenv.pypa.io/en/latest/install/) and [Docker](https://docs.docker.com/desktop/install/linux-install/) with [Compose](https://docs.docker.com/compose/install/) .


## Pipenv

* Install dependencies:

```bash
pipenv install --dev
```

Pipenv will create a virtual env.

* Activate the virtual env

```bash
pipenv shell
```

## Database

* Create database and run it:

```bash
docker compose up -d
```

# Run

## Import data

* Import data from node server:

```bash
uvicorn application.import_data:main
```

## FastApi server

* Run FatsApi server:

```bash
uvicorn application.main:app
```

# Test

* Run tests:

```bash
pytest
```

# Format code

* Auto format code and check:

```bash
isort . && black . && flake8 .
```