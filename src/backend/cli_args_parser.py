"""
CLI Argument parsing and validation for heinrich-tool CLI.
"""

import argparse
from collections.abc import Iterable

from .input_args import (
    InputArgs,
    create_delivery_args,
    create_invoice_args,
    create_offer_args,
)


def parse_cli_args(argv: Iterable[str] | None = None) -> InputArgs:
    parser = argparse.ArgumentParser(
        description="Generate documents from CSV and Word template."
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str.lower,
        required=True,
        choices=["offer", "delivery", "invoice"],
        help="Mode: offer, delivery or invoice",
    )
    parser.add_argument(
        "-p", "--project-number", type=str, required=True, help="4-digit project number"
    )
    parser.add_argument(
        "-r",
        "--receipt-number",
        type=str,
        required=False,
        default=None,
        help="Receipt number (optional for delivery, required for invoice)",
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.mode == "offer" and args.receipt_number is not None:
        parser.error("RECEIPT_NUMBER should not be provided for offer mode")

    try:
        if args.mode == "offer":
            return create_offer_args(args.project_number)
        elif args.mode == "delivery":
            return create_delivery_args(args.project_number, args.receipt_number)
        else:
            if args.receipt_number is None:
                parser.error("RECEIPT_NUMBER is required for invoice mode")
            return create_invoice_args(args.project_number, args.receipt_number)
    except ValueError as e:
        parser.error(str(e))
