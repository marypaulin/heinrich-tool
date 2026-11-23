"""Tests for reading the time-tracking CSV file into typed rows."""

from decimal import Decimal

import pytest

from heinrich_tool.backend.csv_loader import load_csv_data
from heinrich_tool.backend.models import CsvRow
from samples import SAMPLE_CSV_PATH, write_variant, write_without_column

# — Reading ———————————————————————————————————————————————————————————————————


def test_fixture_rows_are_numbered_like_excel():
    rows = load_csv_data(SAMPLE_CSV_PATH)

    assert [row.row_number for row in rows] == list(range(2, 13))


def test_first_row_is_read_completely():
    rows = load_csv_data(SAMPLE_CSV_PATH)

    assert rows[0] == CsvRow(
        row_number=2,
        order_number="123",
        description="Zuschnitt Flachstahl",
        duration_hours=Decimal("1.00"),
        hourly_rate=Decimal("84.90"),
        material_cost=Decimal("95.00"),
    )


def test_numbers_are_read_as_decimal():
    """A float would still compare equal to the Decimal in the test above."""
    row = load_csv_data(SAMPLE_CSV_PATH)[0]

    assert type(row.duration_hours) is Decimal
    assert type(row.hourly_rate) is Decimal
    assert type(row.material_cost) is Decimal


def test_umlauts_and_sharp_s_survive():
    rows = load_csv_data(SAMPLE_CSV_PATH)

    assert rows[3].description == "Aufmaß Halle 3"
    assert rows[5].description == "Filtergehäuse prüfen"
    assert rows[7].description == "Geländer schweißen Ost"


def test_empty_description_stays_empty():
    rows = load_csv_data(SAMPLE_CSV_PATH)

    assert rows[8].description == ""


def test_file_with_bom_reads_like_file_without(tmp_path):
    csv_path = tmp_path / "with_bom.csv"
    csv_path.write_text(
        SAMPLE_CSV_PATH.read_text(encoding="utf-8"), encoding="utf-8-sig"
    )

    assert load_csv_data(csv_path) == load_csv_data(SAMPLE_CSV_PATH)


def test_blank_order_number_becomes_empty():
    rows = load_csv_data(SAMPLE_CSV_PATH)

    assert rows[9].order_number == ""


# — Errors ————————————————————————————————————————————————————————————————————


@pytest.mark.parametrize(
    "column",
    [
        "Auftrags-Nr.",
        "Beschreibung",
        "Dauer (Std)",
        "Stundensatz",
        "Material",
    ],
)
def test_missing_column_is_rejected(tmp_path, column):
    csv_path = write_without_column(tmp_path, column)

    with pytest.raises(ValueError):
        load_csv_data(csv_path)


@pytest.mark.parametrize("column", ["Dauer (Std)", "Stundensatz", "Material"])
def test_missing_required_value_is_rejected(tmp_path, column):
    csv_path = write_variant(tmp_path, row=1, column=column, value="")

    with pytest.raises(ValueError):
        load_csv_data(csv_path)


def test_broken_number_is_rejected(tmp_path):
    csv_path = write_variant(tmp_path, row=1, column="Stundensatz", value="abc")

    with pytest.raises(ValueError):
        load_csv_data(csv_path)


@pytest.mark.parametrize("column", ["Stundensatz", "Material"])
def test_amount_with_more_than_two_decimals_is_rejected(tmp_path, column):
    csv_path = write_variant(tmp_path, row=1, column=column, value="84.905")

    with pytest.raises(ValueError):
        load_csv_data(csv_path)


def test_hours_off_the_half_hour_are_rejected(tmp_path):
    csv_path = write_variant(tmp_path, row=1, column="Dauer (Std)", value="2.25")

    with pytest.raises(ValueError):
        load_csv_data(csv_path)


@pytest.mark.parametrize("column", ["Datum", "Gesamt"])
def test_unused_column_is_not_checked(tmp_path, column):
    csv_path = write_variant(tmp_path, row=1, column=column, value="")

    assert load_csv_data(csv_path) == load_csv_data(SAMPLE_CSV_PATH)


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_csv_data(tmp_path / "missing.csv")
