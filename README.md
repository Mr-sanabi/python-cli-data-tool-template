# Python CLI Data Tool Template

A Python 3.11+ starter for small CLI tools, plus reusable helpers for logging, files, CSV, JSON, and SQLite.

## Run

Copy [`project_template/`](project_template/) into a new project, rename it, and replace the example logic in `src/main.py`.
Run inside your copied project:

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m src.main data/input.txt data/processed/output.txt
python -m pytest -q
```

For individual helpers, copy only what you need from [`templates.py`](templates.py). The template is a starting point, not a framework; add project-specific validation and error handling.

## Test the helpers

From this repository's root:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The copied template has its own test suite, run separately as shown above.
