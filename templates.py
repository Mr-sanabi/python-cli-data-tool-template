"""Reusable standard-library helpers for small Python CLI data tools.

The module intentionally stays in one file so individual functions can be copied
into new automation, scraping, CSV/JSON, and SQLite projects.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sqlite3
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


PathLike = str | Path


def ensure_parent_directory(file_path: PathLike) -> Path:
    """Create the parent directory for a file path and return the Path object."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging(
    log_file: PathLike | None = None,
    level: int = logging.INFO,
) -> None:
    """Configure UTC console logging and optional UTF-8 file logging."""
    handlers: list[logging.Handler] = [logging.StreamHandler()]

    if log_file is not None:
        path = ensure_parent_directory(log_file)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))

    logging.Formatter.converter = time.gmtime
    logging.basicConfig(
        level=level,
        format="%(asctime)sZ (%(levelname)s) %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        handlers=handlers,
        force=True,
    )


def positive_int(value: str) -> int:
    """Argparse type for integers greater than zero."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Value must be an integer") from error

    if number <= 0:
        raise argparse.ArgumentTypeError("Value must be greater than 0")
    return number


def non_negative_int(value: str) -> int:
    """Argparse type for integers greater than or equal to zero."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Value must be an integer") from error

    if number < 0:
        raise argparse.ArgumentTypeError("Value must be greater than or equal to 0")
    return number


def build_parser() -> argparse.ArgumentParser:
    """Return a small parser that can be adapted for a new CLI project."""
    parser = argparse.ArgumentParser(description="Process a local data file.")
    parser.add_argument("input_file", type=Path, help="Path to the input file")
    parser.add_argument("output_file", type=Path, help="Path to the output file")
    parser.add_argument(
        "--limit",
        type=positive_int,
        default=None,
        help="Optional maximum number of records to process",
    )
    return parser


def format_summary(metrics: Mapping[str, object], title: str = "SUMMARY") -> str:
    """Render a compact terminal summary from a mapping of metric names to values."""
    width = max(52, len(title) + 4)
    lines = [title.center(width, "=")]
    lines.extend(f"{name}: {value}" for name, value in metrics.items())
    lines.append("=" * width)
    return "\n".join(lines)


def load_csv(file_path: PathLike) -> list[dict[str, str]]:
    """Load a UTF-8 CSV file as a list of dictionaries."""
    try:
        with Path(file_path).open("r", encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))
    except FileNotFoundError:
        logging.error("CSV file not found: %s", file_path)
        return []
    except csv.Error as error:
        logging.error("Failed to read CSV file %s: %s", file_path, error)
        return []


def save_csv(
    file_path: PathLike,
    rows: Sequence[Mapping[str, object]],
    fieldnames: Sequence[str] | None = None,
) -> bool:
    """Save dictionary rows to CSV. Return False when there is nothing to write."""
    if not rows:
        return False

    fields = list(fieldnames or rows[0].keys())
    path = ensure_parent_directory(file_path)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return True


def load_json(file_path: PathLike, default: Any = None) -> Any:
    """Load JSON, returning a caller-provided default for missing or invalid files."""
    fallback = {} if default is None else default
    path = Path(file_path)

    if not path.exists():
        return fallback

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        logging.error("Failed to load JSON file %s: %s", path, error)
        return fallback


def save_json(file_path: PathLike, data: Any) -> Path:
    """Atomically save JSON so an interrupted write does not corrupt the old file."""
    path = ensure_parent_directory(file_path)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    temporary_path.replace(path)
    return path


def load_text(file_path: PathLike) -> str:
    """Load a UTF-8 text file, returning an empty string when it is missing."""
    try:
        return Path(file_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        logging.error("Text file not found: %s", file_path)
        return ""


def load_lines(file_path: PathLike) -> list[str]:
    """Load non-empty stripped lines from a UTF-8 text file."""
    text = load_text(file_path)
    return [line.strip() for line in text.splitlines() if line.strip()]


def save_text(file_path: PathLike, content: str) -> Path:
    """Save UTF-8 text and create missing parent directories."""
    path = ensure_parent_directory(file_path)
    path.write_text(content, encoding="utf-8")
    return path


def append_text(file_path: PathLike, content: str) -> Path:
    """Append UTF-8 text and create missing parent directories."""
    path = ensure_parent_directory(file_path)
    with path.open("a", encoding="utf-8") as file:
        file.write(content)
    return path


def connect_db(db_file: PathLike) -> sqlite3.Connection:
    """Open a SQLite connection after creating the database directory."""
    path = ensure_parent_directory(db_file)
    return sqlite3.connect(path)


def clean_identifier(name: str) -> str:
    """Normalize a table or column name into a safe SQLite identifier."""
    cleaned = name.strip().lower().replace(" ", "_").replace("-", "_")
    cleaned = "".join(char for char in cleaned if char.isalnum() or char == "_")

    if not cleaned:
        cleaned = "column"
    if cleaned[0].isdigit():
        cleaned = "col_" + cleaned
    return cleaned


def _quote_identifier(name: str) -> str:
    return f'"{clean_identifier(name)}"'


def create_table(
    connection: sqlite3.Connection,
    table_name: str,
    headers: Sequence[str],
    replace: bool = True,
) -> list[str]:
    """Create a TEXT-column table and return the normalized header names."""
    if not headers:
        raise ValueError("At least one header is required")

    clean_headers = [clean_identifier(header) for header in headers]
    if len(clean_headers) != len(set(clean_headers)):
        raise ValueError("Headers must remain unique after normalization")

    table = _quote_identifier(table_name)
    columns_sql = ", ".join(f'{_quote_identifier(header)} TEXT' for header in headers)

    if replace:
        connection.execute(f"DROP TABLE IF EXISTS {table}")
    connection.execute(f"CREATE TABLE IF NOT EXISTS {table} ({columns_sql})")
    connection.commit()
    return clean_headers


def insert_rows(
    connection: sqlite3.Connection,
    table_name: str,
    headers: Sequence[str],
    rows: Iterable[Mapping[str, object]],
) -> int:
    """Insert dictionary rows and return the number of inserted records."""
    table = _quote_identifier(table_name)
    columns_sql = ", ".join(_quote_identifier(header) for header in headers)
    placeholders = ", ".join("?" for _ in headers)
    sql = f"INSERT INTO {table} ({columns_sql}) VALUES ({placeholders})"
    values = [tuple(row.get(header, "") for header in headers) for row in rows]

    connection.executemany(sql, values)
    connection.commit()
    return len(values)


def count_rows(connection: sqlite3.Connection, table_name: str) -> int:
    """Return the number of rows in a SQLite table."""
    cursor = connection.execute(f"SELECT COUNT(*) FROM {_quote_identifier(table_name)}")
    result = cursor.fetchone()
    return int(result[0]) if result else 0


def preview_rows(
    connection: sqlite3.Connection,
    table_name: str,
    limit: int = 5,
) -> list[tuple[Any, ...]]:
    """Return a limited preview from a SQLite table."""
    if limit <= 0:
        raise ValueError("Limit must be greater than 0")

    cursor = connection.execute(
        f"SELECT * FROM {_quote_identifier(table_name)} LIMIT ?",
        (limit,),
    )
    return cursor.fetchall()
