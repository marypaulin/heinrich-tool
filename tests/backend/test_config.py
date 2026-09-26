"""Tests for loading the application settings from the JSON config file."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from src.backend.config import load_config

FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"
SAMPLE_CONFIG_PATH = FIXTURES_DIR / "config_sample.json"


def write_config_text(tmp_path: Path, text: str) -> Path:
    config_path = tmp_path / "config.json"
    config_path.write_text(text, encoding="utf-8")
    return config_path


def write_variant(tmp_path: Path, **changes) -> Path:
    """Write the sample config with top-level entries replaced."""
    raw = json.loads(SAMPLE_CONFIG_PATH.read_text(encoding="utf-8"))
    raw.update(changes)
    return write_config_text(tmp_path, json.dumps(raw))


# — Data root —————————————————————————————————————————————————————————————————


def test_relative_data_root_is_resolved_against_the_config_file():
    config = load_config(SAMPLE_CONFIG_PATH)

    assert config.data_root == FIXTURES_DIR


def test_absolute_data_root_is_kept(tmp_path):
    data_root = Path(tmp_path.anchor) / "Datenordner"
    config_path = write_variant(tmp_path, DATA_ROOT=str(data_root))

    assert load_config(config_path).data_root == data_root


# — Money —————————————————————————————————————————————————————————————————————


def test_vat_rate_is_read_as_decimal():
    config = load_config(SAMPLE_CONFIG_PATH)

    assert config.vat_rate == Decimal("0.19")
    assert type(config.vat_rate) is Decimal


def test_hourly_rates_are_looked_up_by_decimal():
    mapping = load_config(SAMPLE_CONFIG_PATH).hourly_rate_mapping

    assert mapping[Decimal("84.90")] == "Meisterstunde"
    assert mapping[Decimal("48.00")] == "Helferstunde"


def test_old_and_raised_rate_share_a_description():
    """The client adds raised rates next to the old ones so older CSVs still work."""
    mapping = load_config(SAMPLE_CONFIG_PATH).hourly_rate_mapping

    assert mapping[Decimal("84.90")] == mapping[Decimal("92.00")]


# — Documents —————————————————————————————————————————————————————————————————


def test_offer_and_delivery_note_get_their_delivery_days():
    documents = load_config(SAMPLE_CONFIG_PATH).documents

    assert documents["ANGEBOT"].delivery_days == 14
    assert documents["LIEFERSCHEIN"].delivery_days == 0


@pytest.mark.parametrize("key", ["RECHNUNG", "AUFTRAG"])
def test_invoice_and_order_confirmation_have_no_delivery_days(key):
    assert load_config(SAMPLE_CONFIG_PATH).documents[key].delivery_days is None


# — Errors ————————————————————————————————————————————————————————————————————


def test_new_rate_without_comma_is_rejected(tmp_path):
    text = SAMPLE_CONFIG_PATH.read_text(encoding="utf-8")
    last_rate = '"151.00": "Meisterstunde Sonntag"'
    new_rate = '"99.00": "Meisterstunde"'
    broken = text.replace(last_rate, f"{last_rate}\n{new_rate}")
    config_path = write_config_text(tmp_path, broken)

    with pytest.raises(ValueError):
        load_config(config_path)


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "config.json")
