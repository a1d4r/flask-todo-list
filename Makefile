TESTS = tests

VENV ?= .venv
CODE = tests todo_list

.PHONY: venv
venv:
	python3 -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

.PHONY: test
test:
	$(VENV)/bin/pytest -v tests

.PHONY: lint
lint:
	$(VENV)/bin/flake8 --jobs 4 --statistics --show-source $(CODE)
	$(VENV)/bin/pylint --jobs 4 --load-plugins pylint_flask_sqlalchemy --rcfile=setup.cfg $(CODE)
	$(VENV)/bin/black --skip-string-normalization --check $(CODE)

.PHONY: format
format:
	$(VENV)/bin/isort $(CODE)
	$(VENV)/bin/black --skip-string-normalization $(CODE)
	$(VENV)/bin/autoflake --recursive --in-place --remove-all-unused-imports $(CODE)
	$(VENV)/bin/unify --in-place --recursive $(CODE)

.PHONY: ci
ci:	lint test

.PHONY: up
up:
	FLASK_APP=todo_list.app \
	FLASK_ENV=production \
	FLASK_CONFIG=production \
	SECRET_KEY='very secret key' \
	$(VENV)/bin/flask run
