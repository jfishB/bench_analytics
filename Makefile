# Makefile for common developer tasks (backend-focused)

VENV?=venv
PY=python3
PIP=$(VENV)/bin/pip
ACTIVATE=. $(VENV)/bin/activate && \

.PHONY: venv install migrate test pytest clean

venv:
	@echo "Creating virtualenv at $(VENV)..."
	$(PY) -m venv $(VENV)
	$(ACTIVATE) $(PY) -m pip install --upgrade pip setuptools

install: venv
	@echo "Installing Python requirements into $(VENV)..."
	$(ACTIVATE) $(PIP) install -r requirements.txt

migrate: install
	@echo "Applying Django migrations..."
	$(ACTIVATE) $(PY) backend/manage.py migrate --noinput

pytest: migrate
	@echo "Running pytest..."
	$(ACTIVATE) $(PY) -m pytest -q

test: pytest

clean:
	@echo "Removing virtualenv and .pyc files (careful)"
	rm -rf $(VENV) || true
	find . -name "*.pyc" -delete
