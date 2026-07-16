import argparse

import pytest

from templates import (
    count_rows,
    create_table,
    insert_rows,
    load_csv,
    load_json,
    positive_int,
    preview_rows,
    save_csv,
    save_json,
    connect_db,
)


def test_positive_int_accepts_positive_value():
    assert positive_int("3") == 3


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_positive_int_rejects_invalid_value(value):
    with pytest.raises(argparse.ArgumentTypeError):
        positive_int(value)


def test_csv_round_trip_creates_parent_directory(tmp_path):
    file_path = tmp_path / "nested" / "records.csv"
    rows = [{"name": "Alpha", "count": 2}]

    assert save_csv(file_path, rows) is True
    assert load_csv(file_path) == [{"name": "Alpha", "count": "2"}]


def test_json_round_trip_is_atomic(tmp_path):
    file_path = tmp_path / "nested" / "state.json"
    data = {"https://example.com": "abc123"}

    save_json(file_path, data)

    assert load_json(file_path) == data
    assert not file_path.with_suffix(".json.tmp").exists()


def test_sqlite_helpers_round_trip(tmp_path):
    connection = connect_db(tmp_path / "nested" / "records.db")
    headers = ["Product Name", "Price"]
    rows = [{"Product Name": "Keyboard", "Price": "49.90"}]

    create_table(connection, "Order", headers)
    assert insert_rows(connection, "Order", headers, rows) == 1
    assert count_rows(connection, "Order") == 1
    assert preview_rows(connection, "Order") == [("Keyboard", "49.90")]

    connection.close()
