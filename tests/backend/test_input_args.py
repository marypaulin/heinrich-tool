"""Tests for input validation and the argument objects both entry points build."""

from pathlib import Path

import pytest

from heinrich_tool.backend.config import DocumentKind
from heinrich_tool.backend.input_args import create_document_args, create_settings

PROJECT_NUMBER = "1408"
RECEIPT_NUMBER = "8100045372"


# — Project number ————————————————————————————————————————————————————————————


def test_four_digit_project_number_is_accepted():
    args = create_document_args(DocumentKind.OFFER, PROJECT_NUMBER)

    assert args.project_number == PROJECT_NUMBER


def test_project_number_is_trimmed():
    args = create_document_args(DocumentKind.OFFER, f"  {PROJECT_NUMBER}  ")

    assert args.project_number == PROJECT_NUMBER


@pytest.mark.parametrize(
    "project_number", ["140", "14082", "1408 - Allgemein Juli", ""]
)
def test_invalid_project_number_is_rejected(project_number):
    with pytest.raises(ValueError):
        create_document_args(DocumentKind.OFFER, project_number)


# — Receipt number ————————————————————————————————————————————————————————————


def test_delivery_works_without_receipt_number():
    args = create_document_args(DocumentKind.DELIVERY_NOTE, PROJECT_NUMBER)

    assert args.receipt_number is None


@pytest.mark.parametrize("receipt_number", ["", "   "])
def test_delivery_turns_a_blank_receipt_number_into_none(receipt_number):
    """Streamlit submits an untouched text input as an empty string, not as None."""
    args = create_document_args(
        DocumentKind.DELIVERY_NOTE, PROJECT_NUMBER, receipt_number
    )

    assert args.receipt_number is None


@pytest.mark.parametrize("kind", [DocumentKind.DELIVERY_NOTE, DocumentKind.INVOICE])
def test_receipt_number_is_trimmed(kind):
    args = create_document_args(kind, PROJECT_NUMBER, f" {RECEIPT_NUMBER} ")

    assert args.receipt_number == RECEIPT_NUMBER


@pytest.mark.parametrize(
    "kind", [DocumentKind.INVOICE, DocumentKind.ORDER_CONFIRMATION]
)
@pytest.mark.parametrize("receipt_number", [None, "", "   "])
def test_invoice_and_order_confirmation_require_a_receipt_number(kind, receipt_number):
    with pytest.raises(ValueError):
        create_document_args(kind, PROJECT_NUMBER, receipt_number)


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
