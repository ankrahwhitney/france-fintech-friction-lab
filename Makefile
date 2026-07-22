PYTHON ?= python3

.PHONY: setup data analysis all ci test lint dashboard clean

setup:
	$(PYTHON) -m pip install -e ".[dev]"

data:
	$(PYTHON) scripts/generate_data.py

analysis:
	$(PYTHON) scripts/run_analysis.py

# setup is idempotent (pip skips an already-installed package), so `make all`
# also works on a fresh clone without a separate install step.
all: setup data analysis test

# Mirrors .github/workflows/ci.yml so the full CI pipeline can be run locally.
ci: setup data analysis lint test
	@test -z "$$(git status --porcelain -- artifacts)" || \
		(echo "Generated artifacts differ from the committed outputs" && \
		 git status --short -- artifacts && exit 1)

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
