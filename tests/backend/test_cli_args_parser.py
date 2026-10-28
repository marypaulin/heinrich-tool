"""Tests for the argparse rules the CLI enforces before the argument objects are built."""

import pytest

from heinrich_tool.backend.cli_args_parser import parse_cli_args
from heinrich_tool.backend.input_args import DeliveryNoteArgs, InvoiceArgs, OfferArgs

PROJECT_NUMBER = "1408"
RECEIPT_NUMBER = "8100045372"


def test_cli_builds_offer_args():
    args = parse_cli_args(["-m", "offer", "-p", PROJECT_NUMBER])

    assert args == OfferArgs(mode="offer", project_number=PROJECT_NUMBER)


def test_cli_builds_delivery_note_args():
    args = parse_cli_args(
        ["-m", "delivery", "-p", PROJECT_NUMBER, "-r", RECEIPT_NUMBER]
    )

    assert args == DeliveryNoteArgs(
        mode="delivery",
        project_number=PROJECT_NUMBER,
        receipt_number=RECEIPT_NUMBER,
    )


def test_cli_builds_invoice_args():
    args = parse_cli_args(["-m", "invoice", "-p", PROJECT_NUMBER, "-r", RECEIPT_NUMBER])

    assert args == InvoiceArgs(
        mode="invoice",
        project_number=PROJECT_NUMBER,
        receipt_number=RECEIPT_NUMBER,
    )


def test_cli_rejects_a_receipt_number_for_offer():
    with pytest.raises(SystemExit):
        parse_cli_args(["-m", "offer", "-p", PROJECT_NUMBER, "-r", RECEIPT_NUMBER])


def test_cli_requires_a_receipt_number_for_invoice():
    with pytest.raises(SystemExit):
        parse_cli_args(["-m", "invoice", "-p", PROJECT_NUMBER])


def test_cli_exits_on_invalid_input_instead_of_raising():
    with pytest.raises(SystemExit):
        parse_cli_args(["-m", "offer", "-p", "140"])
