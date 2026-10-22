.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check for errors with ruff"
	@echo "test - run tests with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release to PyPI"
	@echo "dist - package"

clean: clean-build clean-pyc
	rm -fr htmlcov/

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	ruff check polyglot tests tools

test:
	python -m pytest

docs:
	rm -f docs/polyglot.rst
	rm -f docs/modules.rst
	sphinx-apidoc -o docs/ polyglot
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	rm -f docs/*tests*rst

release: dist
	python -m twine upload dist/*

dist: clean
	python -m build
	python -m twine check dist/*
	ls -l dist
