PYTHON ?= python3.12
UV ?= uv

.PHONY: check-python setup data analysis all ci test lint format-check audit dashboard clean

check-python:
	@$(PYTHON) -c 'import sys; expected=(3, 12); actual=sys.version_info[:2]; raise SystemExit(0 if actual == expected else "Python 3.12 is required; received %s.%s via $(PYTHON)" % actual)'

setup: check-python
	$(UV) sync --active --locked --extra dev --python $(PYTHON)

data: check-python
	$(PYTHON) scripts/generate_data.py

analysis: check-python
	$(PYTHON) scripts/run_analysis.py

# `make setup` creates the locked environment; `make all` rebuilds every case output.
all: data analysis test

# Mirrors .github/workflows/ci.yml. Run `make setup` once on a fresh clone;
# CI installs the committed lockfile before invoking this target.
ci: check-python data analysis lint test audit
	@test -z "$$(git status --porcelain -- artifacts)" || \
		(echo "Generated artifacts differ from the committed outputs" && \
		 git status --short -- artifacts && exit 1)

test: check-python
	$(PYTHON) -m pytest

# tests/conftest.py regenerates data and artifacts when they are missing, so
# `make test` also works on a fresh clone without running `make data analysis` first.

lint: check-python format-check
	$(PYTHON) -m ruff check src scripts dashboard tests

format-check: check-python
	$(PYTHON) -m ruff format --check src scripts dashboard tests

audit: check-python
	$(PYTHON) -m pip_audit --skip-editable

dashboard: check-python
	$(PYTHON) -m streamlit run dashboard/app.py

clean:
	$(PYTHON) -c "from pathlib import Path; [p.unlink() for d in ('data/processed','artifacts') for p in Path(d).glob('*') if p.is_file()]"
