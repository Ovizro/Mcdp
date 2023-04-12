.PHONY: build build_cython install build_dist test clean
refresh: clean build install lint

MODULE := mcdp
PIP_MODULE := Mcdp

all: clean build lint build_dist
refresh: clean develop test lint

build_cython:
	USE_CYTHON=true python setup.py build_ext --inplace
	find ./${MODULE} -name "*.h" -type f -exec mv {} ./${MODULE}/include \;

build:
	python setup.py build_ext --inplace

install: build
	python setup.py install

develop: build
	python setup.py develop

build_dist: test
	python setup.py sdist bdist_wheel

lint:
	flake8 ${MODULE}/ tests/ --exclude __init__.py --count --max-line-length=127 --extend-ignore=W293,F402 || true

test:
	python -m unittest

clean:
	rm -rf build
	rm -rf dist
	rm -rf ${PIP_MODULE}.egg-info

uninstall:
	pip uninstall ${PIP_MODULE} -y || true
