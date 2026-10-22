.PHONY: help clean clean-build clean-pyc format lint test docs release dist

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "format - format code with ruff"
	@echo "lint - check for errors and formatting with ruff"
	@echo "test - run tests with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release to PyPI"
	@echo "dist - package"

clean: clean-build clean-pyc
	rm -fr htmlcov/ .pytest_cache/ .ruff_cache/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -type d -prune -exec rm -fr {} +

format:
	ruff format .

lint:
	ruff check polyglot3 tests tools
	ruff format --check .

test:
	python -m pytest -W error

docs:
	$(MAKE) -C docs clean
	$(MAKE) -C docs html

release: dist
	python -m twine upload dist/*

dist: clean
	python -m build
	python -m twine check --strict dist/*
	ls -l dist
