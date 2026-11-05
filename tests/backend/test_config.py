"""Tests for loading the client's business config."""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from heinrich_tool.backend.config import load_config
from samples import SAMPLE_CONFIG_PATH


def write_config_text(tmp_path: Path, text: str) -> Path:
    config_path = tmp_path / "config.json"
    config_path.write_text(text, encoding="utf-8")
    return config_path


def read_sample_raw() -> dict:
    return json.loads(SAMPLE_CONFIG_PATH.read_text(encoding="utf-8"))


def write_raw(tmp_path: Path, raw: dict) -> Path:
    return write_config_text(tmp_path, json.dumps(raw))


# — Rates —————————————————————————————————————————————————————————————————————


def test_vat_rate_is_read_as_decimal():
    config = load_config(SAMPLE_CONFIG_PATH)

    assert config.vat_rate == Decimal("0.19")
    assert type(config.vat_rate) is Decimal


def test_hourly_rates_are_looked_up_by_decimal():
    mapping = load_config(SAMPLE_CONFIG_PATH).rate_descriptions

    assert mapping[Decimal("84.90")] == "Meisterstunde"
    assert mapping[Decimal("48.00")] == "Helferstunde"


def test_old_and_raised_rate_share_a_description():
    """The client adds raised rates next to the old ones so older CSVs still work."""
    mapping = load_config(SAMPLE_CONFIG_PATH).rate_descriptions

    assert mapping[Decimal("84.90")] == mapping[Decimal("92.00")]


# — Documents —————————————————————————————————————————————————————————————————


def test_offer_and_delivery_note_get_their_delivery_days():
    documents = load_config(SAMPLE_CONFIG_PATH).documents

    assert documents["offer"].delivery_days == 14
    assert documents["delivery_note"].delivery_days == 0


@pytest.mark.parametrize("key", ["invoice", "order_confirmation"])
def test_invoice_and_order_confirmation_are_due_on_document_date(key):
    assert load_config(SAMPLE_CONFIG_PATH).documents[key].delivery_days == 0


# — Errors ————————————————————————————————————————————————————————————————————


def test_new_rate_without_comma_is_rejected(tmp_path):
    text = SAMPLE_CONFIG_PATH.read_text(encoding="utf-8")
    last_rate = '"151.00": "Meisterstunde Sonntag"'
    new_rate = '"99.00": "Meisterstunde"'
    broken = text.replace(last_rate, f"{last_rate}\n{new_rate}")
    config_path = write_config_text(tmp_path, broken)

    with pytest.raises(ValueError):
        load_config(config_path)


def test_missing_key_is_rejected(tmp_path):
    raw = read_sample_raw()
    del raw["vat_rate"]

    with pytest.raises(ValueError):
        load_config(write_raw(tmp_path, raw))


def test_missing_document_is_rejected(tmp_path):
    raw = read_sample_raw()
    del raw["documents"]["invoice"]

    with pytest.raises(ValueError):
        load_config(write_raw(tmp_path, raw))


def test_missing_filename_is_rejected(tmp_path):
    raw = read_sample_raw()
    del raw["documents"]["invoice"]["filename"]

    with pytest.raises(ValueError):
        load_config(write_raw(tmp_path, raw))


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "config.json")
