"""Command line parser for the CLI entry point."""

import argparse
from collections.abc import Iterable

from heinrich_tool.backend.config import DocumentKind
from heinrich_tool.backend.input_args import DocumentArgs, create_document_args


def parse_cli_args(argv: Iterable[str] | None = None) -> DocumentArgs:
    parser = argparse.ArgumentParser(
        description="Generate documents from CSV and Word template."
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str.lower,
        required=True,
        choices=list(DocumentKind),
        help="Document to generate",
    )
    parser.add_argument(
        "-p", "--project-number", required=True, help="4-digit project number"
    )
    parser.add_argument(
        "-r",
        "--receipt-number",
        help=(
            "Receipt number (optional for delivery_note, "
            "required for invoice and order_confirmation)"
        ),
    )

    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.mode == "offer" and args.receipt_number is not None:
        parser.error("RECEIPT_NUMBER should not be provided for offer mode")

    try:
        return create_document_args(
            DocumentKind(args.mode), args.project_number, args.receipt_number
        )
    except ValueError as e:
        parser.error(str(e))
