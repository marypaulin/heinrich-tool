"""Tests for reading the time-tracking CSV file into typed rows."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from src.backend.csv_loader import load_csv_data
from src.backend.models import CsvRow

FIXTURE = Path(__file__).parents[1] / "fixtures" / "heinrich_zeiterfassung_sample.csv"
FIXTURE_DELIMITER = ";"


def write_lines(tmp_path: Path, lines: list[str]) -> Path:
    csv_path = tmp_path / "variant.csv"
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path


def write_variant(tmp_path: Path, row: int, column: str, value: str) -> Path:
    """Write the fixture with one field replaced; `row` counts data rows from 1."""
    lines = FIXTURE.read_text(encoding="utf-8").splitlines()
    header = lines[0].split(FIXTURE_DELIMITER)
    fields = lines[row].split(FIXTURE_DELIMITER)
    fields[header.index(column)] = f'"{value}"'
    lines[row] = FIXTURE_DELIMITER.join(fields)
    return write_lines(tmp_path, lines)


def write_without_column(tmp_path: Path, column: str) -> Path:
    lines = FIXTURE.read_text(encoding="utf-8").splitlines()
    index = lines[0].split(FIXTURE_DELIMITER).index(column)
    trimmed = []
    for line in lines:
        fields = line.split(FIXTURE_DELIMITER)
        del fields[index]
        trimmed.append(FIXTURE_DELIMITER.join(fields))
    return write_lines(tmp_path, trimmed)


# — Reading ———————————————————————————————————————————————————————————————————


def test_fixture_rows_are_numbered_like_excel(sample_config):
    rows = load_csv_data(FIXTURE, sample_config)

    assert [row.row_number for row in rows] == list(range(2, 13))


def test_first_row_is_read_completely(sample_config):
    rows = load_csv_data(FIXTURE, sample_config)

    assert rows[0] == CsvRow(
        row_number=2,
        date=date(2025, 7, 7),
        order_number="123",
        description="Zuschnitt Flachstahl",
        duration_hours=Decimal("1.00"),
        hourly_rate=Decimal("84.90"),
        material_cost=Decimal("95.00"),
        total_cost=Decimal("179.90"),
    )


def test_numbers_are_read_as_decimal(sample_config):
    """A float would still compare equal to the Decimal in the test above."""
    row = load_csv_data(FIXTURE, sample_config)[0]

    assert type(row.duration_hours) is Decimal
    assert type(row.hourly_rate) is Decimal
    assert type(row.material_cost) is Decimal
    assert type(row.total_cost) is Decimal


def test_umlauts_and_sharp_s_survive(sample_config):
    rows = load_csv_data(FIXTURE, sample_config)

    assert rows[3].description == "Aufmaß Halle 3"
    assert rows[5].description == "Filtergehäuse prüfen"
    assert rows[7].description == "Geländer schweißen Ost"


def test_empty_description_stays_empty(sample_config):
    rows = load_csv_data(FIXTURE, sample_config)

    assert rows[8].description == ""


def test_file_with_bom_reads_like_file_without(tmp_path, sample_config):
    csv_path = tmp_path / "with_bom.csv"
    csv_path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8-sig")

    assert load_csv_data(csv_path, sample_config) == load_csv_data(
        FIXTURE, sample_config
    )


def test_blank_order_number_becomes_empty(sample_config):
    rows = load_csv_data(FIXTURE, sample_config)

    assert rows[9].order_number == ""


# — Errors ————————————————————————————————————————————————————————————————————


@pytest.mark.parametrize(
    "column",
    [
        "Datum",
        "Auftrags-Nr.",
        "Beschreibung",
        "Dauer (Std)",
        "Stundensatz",
        "Material",
        "Gesamt",
    ],
)
def test_missing_column_is_rejected(tmp_path, column, sample_config):
    csv_path = write_without_column(tmp_path, column)

    with pytest.raises(ValueError):
        load_csv_data(csv_path, sample_config)


@pytest.mark.parametrize("column", ["Dauer (Std)", "Stundensatz", "Material"])
def test_missing_required_value_is_rejected(tmp_path, column, sample_config):
    csv_path = write_variant(tmp_path, row=1, column=column, value="")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, sample_config)


def test_broken_number_is_rejected(tmp_path, sample_config):
    csv_path = write_variant(tmp_path, row=1, column="Stundensatz", value="abc")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, sample_config)


@pytest.mark.parametrize("column", ["Stundensatz", "Material"])
def test_amount_with_more_than_two_decimals_is_rejected(
    tmp_path, column, sample_config
):
    csv_path = write_variant(tmp_path, row=1, column=column, value="84.905")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, sample_config)


def test_hours_off_the_half_hour_are_rejected(tmp_path, sample_config):
    csv_path = write_variant(tmp_path, row=1, column="Dauer (Std)", value="2.25")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, sample_config)


def test_broken_date_is_rejected(tmp_path, sample_config):
    csv_path = write_variant(tmp_path, row=1, column="Datum", value="2025-07-07")

    with pytest.raises(ValueError):
        load_csv_data(csv_path, sample_config)


def test_missing_file_is_rejected(tmp_path, sample_config):
    with pytest.raises(FileNotFoundError):
        load_csv_data(tmp_path / "missing.csv", sample_config)
