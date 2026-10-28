"""Input validation and argument object creation for CLI and UI entry points."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from heinrich_tool.backend.settings import Settings

# Project number should be exactly four digits
PROJECT_NUMBER_RE = re.compile(r"\d{4}")


@dataclass(frozen=True)
class OfferArgs:
    mode: Literal["offer"]
    project_number: str


@dataclass(frozen=True)
class DeliveryNoteArgs:
    mode: Literal["delivery"]
    project_number: str
    receipt_number: str | None


@dataclass(frozen=True)
class InvoiceArgs:
    mode: Literal["invoice"]
    project_number: str
    receipt_number: str


InputArgs = OfferArgs | DeliveryNoteArgs | InvoiceArgs


def _parse_project_number(project_number: str) -> str:
    project_number = project_number.strip()
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    return project_number


def _parse_receipt_number_optional(receipt_number: str | None) -> str | None:
    return (receipt_number or "").strip() or None


def _parse_receipt_number_required(receipt_number: str) -> str:
    receipt_number = receipt_number.strip()
    if not receipt_number:
        raise ValueError("RECEIPT_NUMBER is required")
    return receipt_number


def create_offer_args(project_number: str) -> OfferArgs:
    project_number = _parse_project_number(project_number)
    return OfferArgs(mode="offer", project_number=project_number)


def create_delivery_note_args(
    project_number: str, receipt_number: str | None = None
) -> DeliveryNoteArgs:
    project_number = _parse_project_number(project_number)
    receipt_number = _parse_receipt_number_optional(receipt_number)
    return DeliveryNoteArgs(
        mode="delivery", project_number=project_number, receipt_number=receipt_number
    )


def create_invoice_args(project_number: str, receipt_number: str) -> InvoiceArgs:
    project_number = _parse_project_number(project_number)
    receipt_number = _parse_receipt_number_required(receipt_number)
    return InvoiceArgs(
        mode="invoice", project_number=project_number, receipt_number=receipt_number
    )


def _parse_path(path: str, name: str) -> Path:
    # Windows' "Copy as path" wraps the path in double quotes.
    path = path.strip().strip('"')
    if not path:
        raise ValueError(f"{name} is required")
    return Path(path)


def _parse_dir(path: str, name: str) -> Path:
    dir_path = _parse_path(path, name)
    if not dir_path.is_dir():
        raise FileNotFoundError(f"{name} not found: {dir_path}")
    return dir_path


def _parse_file(path: str, name: str) -> Path:
    file_path = _parse_path(path, name)
    if not file_path.is_file():
        raise FileNotFoundError(f"{name} not found: {file_path}")
    return file_path


def create_settings(data_root: str, config_path: str, template_path: str) -> Settings:
    return Settings(
        data_root=_parse_dir(data_root, "DATA_ROOT"),
        config_path=_parse_file(config_path, "CONFIG_PATH"),
        template_path=_parse_file(template_path, "TEMPLATE_PATH"),
    )
