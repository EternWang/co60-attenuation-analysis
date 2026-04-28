.PHONY: all analysis test

all: analysis

analysis:
	python src/analyze_co60.py

test:
	python -m unittest discover -s tests
