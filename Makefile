PYTHON ?= python3

.PHONY: setup data analysis all test lint dashboard clean

setup:
	$(PYTHON) -m pip install -e ".[dev]"

data:
	$(PYTHON) scripts/generate_data.py

analysis:
	$(PYTHON) scripts/run_analysis.py

all: data analysis test

test:
	$(PYTHON) -m pytest

# tests/conftest.py regenerates data and artifacts when they are missing, so
# `make test` also works on a fresh clone without running `make data analysis` first.

lint:
	$(PYTHON) -m ruff check src scripts dashboard tests

dashboard:
	$(PYTHON) -m streamlit run dashboard/app.py

clean:
	$(PYTHON) -c "from pathlib import Path; [p.unlink() for d in ('data/processed','artifacts') for p in Path(d).glob('*') if p.is_file()]"

