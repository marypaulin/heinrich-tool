"""Tests for input validation and the argument objects both entry points build."""

from pathlib import Path

import pytest

from heinrich_tool.backend.input_args import (
    create_delivery_args,
    create_invoice_args,
    create_offer_args,
    create_settings,
)

PROJECT_NUMBER = "1408"
RECEIPT_NUMBER = "8100045372"


# — Project number ————————————————————————————————————————————————————————————


def test_four_digit_project_number_is_accepted():
    assert create_offer_args(PROJECT_NUMBER).project_number == PROJECT_NUMBER


def test_project_number_is_trimmed():
    assert create_offer_args(f"  {PROJECT_NUMBER}  ").project_number == PROJECT_NUMBER


@pytest.mark.parametrize(
    "project_number", ["140", "14082", "1408 - Allgemein Juli", ""]
)
def test_invalid_project_number_is_rejected(project_number):
    with pytest.raises(ValueError):
        create_offer_args(project_number)


@pytest.mark.parametrize(
    "create",
    [
        create_offer_args,
        create_delivery_args,
        lambda project_number: create_invoice_args(project_number, RECEIPT_NUMBER),
    ],
)
def test_every_mode_validates_the_project_number(create):
    with pytest.raises(ValueError):
        create("140")


# — Receipt number ————————————————————————————————————————————————————————————


def test_delivery_works_without_receipt_number():
    assert create_delivery_args(PROJECT_NUMBER).receipt_number is None


@pytest.mark.parametrize("receipt_number", ["", "   "])
def test_delivery_turns_a_blank_receipt_number_into_none(receipt_number):
    """Streamlit submits an untouched text input as an empty string, not as None."""
    assert create_delivery_args(PROJECT_NUMBER, receipt_number).receipt_number is None


def test_receipt_number_is_trimmed():
    padded = f" {RECEIPT_NUMBER} "

    assert create_delivery_args(PROJECT_NUMBER, padded).receipt_number == RECEIPT_NUMBER
    assert create_invoice_args(PROJECT_NUMBER, padded).receipt_number == RECEIPT_NUMBER


@pytest.mark.parametrize("receipt_number", ["", "   "])
def test_invoice_requires_a_receipt_number(receipt_number):
    with pytest.raises(ValueError):
        create_invoice_args(PROJECT_NUMBER, receipt_number)


def test_each_factory_sets_its_own_mode():
    assert create_offer_args(PROJECT_NUMBER).mode == "offer"
    assert create_delivery_args(PROJECT_NUMBER).mode == "delivery"
    assert create_invoice_args(PROJECT_NUMBER, RECEIPT_NUMBER).mode == "invoice"


# — Settings ——————————————————————————————————————————————————————————————————


@pytest.fixture
def sample_paths(tmp_path) -> tuple[str, str, str]:
    """An existing data root with config and template in a subfolder."""
    tool_dir = tmp_path / "Daten" / "Tool"
    tool_dir.mkdir(parents=True)
    (tool_dir / "config.json").touch()
    (tool_dir / "Vordruck.docx").touch()
    return (
        str(tmp_path / "Daten"),
        str(tool_dir / "config.json"),
        str(tool_dir / "Vordruck.docx"),
    )


def test_existing_paths_are_accepted(sample_paths):
    data_root, config_path, template_path = sample_paths

    settings = create_settings(data_root, config_path, template_path)

    assert settings.data_root == Path(data_root)
    assert settings.config_path == Path(config_path)
    assert settings.template_path == Path(template_path)


def test_surrounding_quotes_are_removed(sample_paths):
    data_root, config_path, template_path = sample_paths

    settings = create_settings(f' "{data_root}" ', config_path, template_path)

    assert settings.data_root == Path(data_root)


def test_blank_path_is_rejected(sample_paths):
    _, config_path, template_path = sample_paths

    with pytest.raises(ValueError):
        create_settings(" ", config_path, template_path)


def test_missing_data_root_is_rejected(sample_paths, tmp_path):
    _, config_path, template_path = sample_paths

    with pytest.raises(FileNotFoundError):
        create_settings(str(tmp_path / "Fehlt"), config_path, template_path)


def test_missing_file_is_rejected(sample_paths, tmp_path):
    data_root, config_path, _ = sample_paths

    with pytest.raises(FileNotFoundError):
        create_settings(data_root, config_path, str(tmp_path / "fehlt.docx"))
