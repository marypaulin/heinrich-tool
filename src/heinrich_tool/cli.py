"""CLI entry point for document generation — run with --help for usage."""

import logging
import sys
from datetime import date

from heinrich_tool.backend.services import (
    SETTINGS_PATH,
    generate_document,
    load_settings,
)
from heinrich_tool.cli_args_parser import parse_cli_args

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

    generate_document(args, date.today(), settings)


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, ValueError) as e:
        logger.error(e)
        sys.exit(1)
