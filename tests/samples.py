"""Invented sample files standing in for client's real data, and CSV variants."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CONFIG_PATH = FIXTURES_DIR / "config_sample.json"
SAMPLE_CSV_PATH = FIXTURES_DIR / "heinrich_zeiterfassung_sample.csv"
SAMPLE_TEMPLATE_PATH = FIXTURES_DIR / "Vordruck_sample.docx"

FIXTURE_DELIMITER = ";"


def _write_lines(directory: Path, lines: list[str]) -> Path:
    # Overwrites copied sample; a second CSV would compete as newest
    csv_path = directory / SAMPLE_CSV_PATH.name
    csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path


def write_variant(
    directory: Path, column: str, value: str, row: int | None = None
) -> Path:
    """Write the sample CSV with `column` set to `value`, in one row or in all rows.

    `row=1` is the first row after the header. Without `row`, every row gets `value`.
    """
    lines = SAMPLE_CSV_PATH.read_text(encoding="utf-8").splitlines()
    index = lines[0].split(FIXTURE_DELIMITER).index(column)
    rows = [row] if row is not None else range(1, len(lines))
    for line_number in rows:
        fields = lines[line_number].split(FIXTURE_DELIMITER)
        fields[index] = f'"{value}"'
        lines[line_number] = FIXTURE_DELIMITER.join(fields)
    return _write_lines(directory, lines)


def write_without_column(directory: Path, column: str) -> Path:
    lines = SAMPLE_CSV_PATH.read_text(encoding="utf-8").splitlines()
    index = lines[0].split(FIXTURE_DELIMITER).index(column)
    trimmed = []
    for line in lines:
        fields = line.split(FIXTURE_DELIMITER)
        del fields[index]
        trimmed.append(FIXTURE_DELIMITER.join(fields))
    return _write_lines(directory, trimmed)
