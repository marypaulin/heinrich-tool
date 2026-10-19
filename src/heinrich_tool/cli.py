"""CLI entry point for document generation — run with --help for usage."""

import logging
import sys
from datetime import date

from heinrich_tool.backend.cli_args_parser import parse_cli_args
from heinrich_tool.backend.config import load_config
from heinrich_tool.backend.paths import CONFIG_PATH
from heinrich_tool.backend.services import (
    generate_delivery,
    generate_invoice_and_order,
    generate_offer,
)

logging.basicConfig(
    level=logging.WARNING, format="%(levelname)s (%(name)s): %(message)s"
)
logging.getLogger("heinrich_tool").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def main():
    args = parse_cli_args()
    config = load_config(CONFIG_PATH)

    if args.mode == "offer":
        generate_offer(args, date.today(), config)
    elif args.mode == "delivery":
        generate_delivery(args, date.today(), config)
    elif args.mode == "invoice":
        generate_invoice_and_order(args, date.today(), config)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        logger.error(e)
        sys.exit(1)
