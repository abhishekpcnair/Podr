.PHONY: clean build test install

clean:
	rm -rf build/ dist/ *.egg-info/

build: clean
	python -m build

test:
	pytest

install: build
	pip install dist/*.whl

dev-install:
	pip install -e .