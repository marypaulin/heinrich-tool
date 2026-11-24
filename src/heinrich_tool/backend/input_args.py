"""Input validation and argument object creation for CLI and UI entry points."""

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from heinrich_tool.backend.config import DocumentKind
from heinrich_tool.backend.settings import Settings

PROJECT_NUMBER_RE = re.compile(r"\d{4}")


# — Document arguments ————————————————————————————————————————————————————————


@dataclass(frozen=True)
class DocumentArgs:
    kind: DocumentKind
    project_number: str
    receipt_number: str | None
    delivery_date: date


def _parse_project_number(project_number: str) -> str:
    project_number = project_number.strip()
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("Project number must be exactly four digits")
    return project_number


# Format unchecked, unlike project number: pasted from an email, not typed
def _parse_receipt_number_optional(receipt_number: str | None) -> str | None:
    return (receipt_number or "").strip() or None


def _parse_receipt_number_required(receipt_number: str | None) -> str:
    receipt_number = (receipt_number or "").strip()
    if not receipt_number:
        raise ValueError("Receipt number is required")
    return receipt_number


def create_document_args(
    kind: DocumentKind,
    project_number: str,
    receipt_number: str | None,
    delivery_date: date,
) -> DocumentArgs:
    project_number = _parse_project_number(project_number)
    if kind in (DocumentKind.INVOICE, DocumentKind.ORDER_CONFIRMATION):
        receipt_number = _parse_receipt_number_required(receipt_number)
    else:
        receipt_number = _parse_receipt_number_optional(receipt_number)
    return DocumentArgs(
        kind=kind,
        project_number=project_number,
        receipt_number=receipt_number,
        delivery_date=delivery_date,
    )


# — Settings ——————————————————————————————————————————————————————————————————


def _parse_path(path: str, name: str) -> Path:
    # Windows' "Copy as path" wraps the path in double quotes
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
        data_root=_parse_dir(data_root, "Data folder"),
        config_path=_parse_file(config_path, "Config file"),
        template_path=_parse_file(template_path, "Template"),
    )
