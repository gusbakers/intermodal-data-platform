PYTHON ?= python

.PHONY: install pipeline database test lint verify stop
install:
	$(PYTHON) -m pip install -r requirements-dev.txt
pipeline:
	$(PYTHON) run_full_pipeline.py
database:
	$(PYTHON) run_full_pipeline.py --with-database
test:
	$(PYTHON) -m pytest --cov=src --cov-report=term-missing
lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .
verify: lint test
stop:
	docker compose down
