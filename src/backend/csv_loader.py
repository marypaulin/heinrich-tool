"""
CSV loading utility
"""

import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .config import Config
from .models import CsvRow
from .money import round_cents

CSV_COL_DATE = "Datum"
CSV_COL_ORDER_NUMBER = "Auftrags-Nr."
CSV_COL_DESC = "Beschreibung"
CSV_COL_DURATION = "Dauer (Std)"
CSV_COL_HOURLY_RATE = "Stundensatz"
CSV_COL_MATERIAL = "Material"
CSV_COL_TOTAL = "Gesamt"

REQUIRED_COLUMNS = [
    CSV_COL_DATE,
    CSV_COL_ORDER_NUMBER,
    CSV_COL_DESC,
    CSV_COL_DURATION,
    CSV_COL_HOURLY_RATE,
    CSV_COL_MATERIAL,
    CSV_COL_TOTAL,
]

# The client records time in half hours only
HOUR_STEP = Decimal("0.5")

# Order number is left out on purpose: csv_transformer skips rows without one
REQUIRED_VALUES = [
    CSV_COL_DURATION,
    CSV_COL_HOURLY_RATE,
    CSV_COL_MATERIAL,
]


def _parse_date(i: int, value: str, config: Config) -> date:
    """Parse str to date from config.date_format"""
    value = value.strip()
    try:
        return datetime.strptime(value, config.date_format).date()
    except ValueError:
        raise ValueError(f"Invalid date format in row {i}: {value}") from None


def _parse_decimal(i: int, value: str) -> Decimal:
    """Replace comma with dot, strip spaces, handle both ',' and '.'"""
    value = value.strip().replace(",", ".")
    try:
        return Decimal(value)
    except InvalidOperation:
        raise ValueError(f"Invalid numeric value in row {i}: {value}") from None


def _parse_hours(i: int, value: str) -> Decimal:
    """Parse a duration; anything off the half hour is taken for a typo."""
    hours = _parse_decimal(i, value)
    if hours % HOUR_STEP != 0:
        raise ValueError(f"Invalid hours in row {i}: {hours} (half hours only)")
    return hours


def _parse_amount(i: int, value: str) -> Decimal:
    """Parse a money amount; finer than cents is taken for a typo, not rounded."""
    amount = _parse_decimal(i, value)
    if round_cents(amount) != amount:
        raise ValueError(f"Amount with more than two decimals in row {i}: {amount}")
    return amount


def load_csv_data(csv_path: Path, config: Config) -> list[CsvRow]:
    """
    Load and parse a CSV file into a list of CsvRow objects.

    This function is responsible for:
    - reading the CSV file,
    - validating required columns and values,
    - parsing strings into typed values (date, Decimal),
    - and creating typed CsvRow domain objects.

    Parameters:
        csv_path: Path to the CSV file to load.
        config: Application configuration (used for date parsing).

    Returns:
        A list of CsvRow objects representing the parsed CSV rows.

    Raises:
        ValueError: If required fields are missing or values cannot be parsed.
        FileNotFoundError: If the CSV file does not exist.
    """
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
        header = reader.fieldnames or []

    missing_columns = [column for column in REQUIRED_COLUMNS if column not in header]
    if missing_columns:
        raise ValueError(
            f"Missing column(s) in CSV header: {', '.join(missing_columns)}"
        )

    result = []

    # Start at 2 so error messages match the row numbers Excel shows
    for row_number, row in enumerate(rows, start=2):
        missing_values = [field for field in REQUIRED_VALUES if not row.get(field)]
        if missing_values:
            raise ValueError(
                f"Missing value(s) in row {row_number}: {', '.join(missing_values)}"
            )

        csv_row = CsvRow(
            row_number=row_number,
            date=_parse_date(row_number, row[CSV_COL_DATE], config),
            order_number=row[CSV_COL_ORDER_NUMBER].strip(),
            description=row[CSV_COL_DESC],
            duration_hours=_parse_hours(row_number, row[CSV_COL_DURATION]),
            hourly_rate=_parse_amount(row_number, row[CSV_COL_HOURLY_RATE]),
            material_cost=_parse_amount(row_number, row[CSV_COL_MATERIAL]),
            total_cost=_parse_decimal(row_number, row[CSV_COL_TOTAL]),
        )
        result.append(csv_row)
    return result
