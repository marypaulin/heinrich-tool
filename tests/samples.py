"""Paths to invented sample files standing in for client's real data."""

from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_CONFIG_PATH = FIXTURES_DIR / "config_sample.json"
SAMPLE_CSV_PATH = FIXTURES_DIR / "heinrich_zeiterfassung_sample.csv"
SAMPLE_TEMPLATE_PATH = FIXTURES_DIR / "Vordruck_sample.docx"
