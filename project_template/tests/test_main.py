from pathlib import Path

import pytest

from src.main import build_parser, run


def test_parser_converts_paths():
    args = build_parser().parse_args(["input.txt", "output.txt"])

    assert args.input_file == Path("input.txt")
    assert args.output_file == Path("output.txt")
    assert args.verbose is False


def test_run_writes_processed_output(tmp_path):
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "nested" / "output.txt"
    input_file.write_text("Example data\n", encoding="utf-8")

    written = run(input_file, output_file)

    assert written == len("Example data\n")
    assert output_file.read_text(encoding="utf-8") == "Example data\n"


def test_run_rejects_missing_input(tmp_path):
    with pytest.raises(FileNotFoundError):
        run(tmp_path / "missing.txt", tmp_path / "output.txt")
