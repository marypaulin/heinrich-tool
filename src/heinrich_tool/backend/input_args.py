"""Input validation and argument object creation for CLI and UI entry points."""

import re
from dataclasses import dataclass
from typing import Literal

# Project number should be exactly four digits
PROJECT_NUMBER_RE = re.compile(r"\d{4}")


@dataclass(frozen=True)
class OfferArgs:
    mode: Literal["offer"]
    project_number: str


@dataclass(frozen=True)
class DeliveryArgs:
    mode: Literal["delivery"]
    project_number: str
    receipt_number: str | None


@dataclass(frozen=True)
class InvoiceArgs:
    mode: Literal["invoice"]
    project_number: str
    receipt_number: str


InputArgs = OfferArgs | DeliveryArgs | InvoiceArgs


def _format_project_number(project_number: str) -> str:
    project_number = project_number.strip()
    if not PROJECT_NUMBER_RE.fullmatch(project_number):
        raise ValueError("PROJECT_NUMBER must be exactly four digits")
    return project_number


def _format_receipt_number_optional(receipt_number: str | None) -> str | None:
    return (receipt_number or "").strip() or None


def _format_receipt_number_required(receipt_number: str) -> str:
    receipt_number = receipt_number.strip()
    if not receipt_number:
        raise ValueError("RECEIPT_NUMBER is required")
    return receipt_number


def create_offer_args(project_number: str) -> OfferArgs:
    project_number = _format_project_number(project_number)
    return OfferArgs(mode="offer", project_number=project_number)


def create_delivery_args(
    project_number: str, receipt_number: str | None = None
) -> DeliveryArgs:
    project_number = _format_project_number(project_number)
    receipt_number = _format_receipt_number_optional(receipt_number)
    return DeliveryArgs(
        mode="delivery", project_number=project_number, receipt_number=receipt_number
    )


def create_invoice_args(project_number: str, receipt_number: str) -> InvoiceArgs:
    project_number = _format_project_number(project_number)
    receipt_number = _format_receipt_number_required(receipt_number)
    return InvoiceArgs(
        mode="invoice", project_number=project_number, receipt_number=receipt_number
    )
