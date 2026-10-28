"""
Path and file discovery utilities for heinrich-tool.
"""

import logging
from pathlib import Path

from heinrich_tool.backend.config import Config
from heinrich_tool.backend.messages import Messages

logger = logging.getLogger(__name__)


def _format_filename(template: str, **values: str) -> str:
    """Fill the filename template placeholders with values"""
    try:
        return template.format(**values)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(
            f"Missing placeholder '{missing}' in config filename template"
        ) from e


def get_project_dir(data_root: Path, project_number: str, messages: Messages) -> Path:
    """Find the folder with the given 4-digit project number as prefix."""
    for folder in data_root.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{project_number} "):
            logger.info(f"Found project folder: {folder.name}")
            messages.info(f"Projektordner gefunden ({folder.name})")
            return folder
    raise FileNotFoundError(f"No folder found for project number {project_number}")


def get_latest_csv_path(project_dir: Path, config: Config, messages: Messages) -> Path:
    """Find the latest CSV file in the order folder."""
    csv_files = list(project_dir.glob(config.filenames["CSV_GLOB"]))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {project_dir}")
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Using CSV file: {latest.name}")
    messages.info(f"CSV-Datei gefunden ({latest.name})")
    return latest


def get_offer_target_path(
    project_dir: Path,
    project_number: str,
    config: Config,
) -> Path:
    """Create filepath for Angebot using filename template from config"""
    filename = _format_filename(
        config.filenames["ANGEBOT"],
        project_number=project_number,
    )
    path = project_dir / filename
    return path


def get_delivery_note_target_path(
    project_dir: Path,
    project_number: str,
    config: Config,
) -> Path:
    """Create filepath for Lieferschein using filename template from config"""
    filename = _format_filename(
        config.filenames["LIEFERSCHEIN"],
        project_number=project_number,
    )
    path = project_dir / filename
    return path


def get_invoice_target_path(
    project_dir: Path,
    project_number: str,
    receipt_number: str,
    config: Config,
) -> Path:
    """Create filepath for Rechnung using filename template from config"""
    filename = _format_filename(
        config.filenames["RECHNUNG"],
        project_number=project_number,
        receipt_number=receipt_number,
    )
    path = project_dir / filename
    return path


def get_order_confirmation_target_path(
    project_dir: Path,
    project_number: str,
    receipt_number: str,
    config: Config,
) -> Path:
    """Create filepath for Auftragsbestätigung using filename template from config"""
    filename = _format_filename(
        config.filenames["AUFTRAG"],
        project_number=project_number,
        receipt_number=receipt_number,
    )
    path = project_dir / filename
    return path
