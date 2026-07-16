from __future__ import annotations

import argparse
import logging
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read a text file, apply a project-specific transformation, and save the result."
    )
    parser.add_argument("input_file", type=Path, help="Path to the input text file")
    parser.add_argument("output_file", type=Path, help="Path for the processed output")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable detailed logging",
    )
    return parser


def transform_text(text: str) -> str:
    """Replace this identity transformation with project-specific logic."""
    return text


def run(input_file: Path, output_file: Path) -> int:
    """Process one file and return the number of written characters."""
    if not input_file.is_file():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    content = input_file.read_text(encoding="utf-8")
    processed = transform_text(content)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(processed, encoding="utf-8")
    return len(processed)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    try:
        written = run(args.input_file, args.output_file)
    except OSError as error:
        logging.error("Processing failed: %s", error)
        return 1

    logging.info("Saved %s characters to %s", written, args.output_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
