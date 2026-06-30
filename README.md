# Python CLI Templates

Reusable templates and snippets for Python CLI data tools.

This repository stores small project templates and common code patterns that I reuse across Python automation, scraping, CSV/JSON, and SQLite projects.

## What is inside

python-cli-templates/
  project_template/
    data/
    src/
    .gitignore
    config_example.json
    README.md
    requirements.txt

  templates.py
  README.md

## Project Template

`project_template/` is a basic starting structure for new Python CLI projects.

It includes:

- `src/` folder for Python code
- `data/` folder for local input/output files
- `.gitignore` for Python projects and local data files
- `requirements.txt`
- `config_example.json`
- basic README structure

## Snippets

`templates.py` contains reusable code snippets for common tasks:

- argparse setup
- logging setup
- summary output
- CSV load/save helpers
- JSON load/save helpers
- text file helpers
- SQLite helpers

## Why I use this

Instead of copying code from old projects every time, I keep common patterns here and reuse them when starting new tools.

This makes future projects faster to set up and keeps my project structure more consistent.

## Typical use cases

- Python CLI tools
- CSV/JSON data processing
- web scraping utilities
- SQLite import/export tools
- small automation scripts

## Tech

- Python
- argparse
- logging
- csv
- json
- sqlite3