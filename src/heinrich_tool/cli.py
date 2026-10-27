"""CLI entry point for document generation — run with --help for usage."""

import logging
import sys
from datetime import date

from heinrich_tool.backend.cli_args_parser import parse_cli_args
from heinrich_tool.backend.services import (
    SETTINGS_PATH,
    generate_delivery,
    generate_invoice_and_order,
    generate_offer,
    load_settings,
)

logging.basicConfig(
    level=logging.WARNING, format="%(levelname)s (%(name)s): %(message)s"
)
logging.getLogger("heinrich_tool").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def main():
    args = parse_cli_args()
    settings = load_settings()
    if settings is None:
        raise FileNotFoundError(
            f"No settings found at {SETTINGS_PATH}, set the paths in the app first"
        )

    if args.mode == "offer":
        generate_offer(args, date.today(), settings)
    elif args.mode == "delivery":
        generate_delivery(args, date.today(), settings)
    elif args.mode == "invoice":
        generate_invoice_and_order(args, date.today(), settings)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        logger.error(e)
        sys.exit(1)
