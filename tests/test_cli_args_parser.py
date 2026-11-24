"""Tests for the argparse rules the CLI enforces before the argument objects are built."""

import pytest

from heinrich_tool.backend.config import DocumentKind
from heinrich_tool.backend.input_args import DocumentArgs
from heinrich_tool.cli_args_parser import parse_cli_args

PROJECT_NUMBER = "1408"
RECEIPT_NUMBER = "8100045372"


def test_cli_builds_offer_args():
    args = parse_cli_args(["-m", "offer", "-p", PROJECT_NUMBER])

    assert args == DocumentArgs(
        kind=DocumentKind.OFFER, project_number=PROJECT_NUMBER, receipt_number=None
    )


@pytest.mark.parametrize(
    ("mode", "kind"),
    [
        ("offer", DocumentKind.OFFER),
        ("delivery_note", DocumentKind.DELIVERY_NOTE),
        ("invoice", DocumentKind.INVOICE),
        ("order_confirmation", DocumentKind.ORDER_CONFIRMATION),
    ],
)
def test_cli_builds_args_with_receipt_number(mode, kind):
    args = parse_cli_args(["-m", mode, "-p", PROJECT_NUMBER, "-r", RECEIPT_NUMBER])

    assert args == DocumentArgs(
        kind=kind, project_number=PROJECT_NUMBER, receipt_number=RECEIPT_NUMBER
    )


@pytest.mark.parametrize("mode", ["invoice", "order_confirmation"])
def test_cli_requires_a_receipt_number_for_invoice_and_order_confirmation(mode):
    with pytest.raises(SystemExit):
        parse_cli_args(["-m", mode, "-p", PROJECT_NUMBER])


def test_cli_exits_on_invalid_input_instead_of_raising():
    with pytest.raises(SystemExit):
        parse_cli_args(["-m", "offer", "-p", "140"])
