"""File system lookups: project folder, latest CSV, document target path."""

import logging
from pathlib import Path

from heinrich_tool.backend.config import Config, DocumentKind
from heinrich_tool.backend.messages import Messages

logger = logging.getLogger(__name__)


def _format_filename(template: str, **values: str) -> str:
    try:
        return template.format(**values)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(
            f"Missing placeholder '{missing}' in config filename template"
        ) from e


def get_project_dir(data_root: Path, project_number: str, messages: Messages) -> Path:
    # Settings are not rechecked on startup, the folder may have moved since
    if not data_root.is_dir():
        raise FileNotFoundError(f"Data folder not found: {data_root}")
    for folder in data_root.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{project_number} "):
            logger.info(f"Found project folder: {folder.name}")
            messages.info(f"Projektordner gefunden ({folder.name})")
            return folder
    raise FileNotFoundError(f"No folder found for project number {project_number}")


def get_latest_csv_path(project_dir: Path, config: Config, messages: Messages) -> Path:
    csv_files = list(project_dir.glob(config.csv_glob))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {project_dir}")
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Using CSV file: {latest.name}")
    messages.info(f"CSV-Datei gefunden ({latest.name})")
    return latest


def get_target_path(
    project_dir: Path,
    kind: DocumentKind,
    project_number: str,
    receipt_number: str | None,
    config: Config,
) -> Path:
    """Build document path from filename template of `kind`.

    Receipt number is passed only when given: a template asking for it then
    fails with a clear error instead of naming the file "... None".
    """
    values = {"project_number": project_number}
    if receipt_number is not None:
        values["receipt_number"] = receipt_number
    filename = _format_filename(config.document(kind).filename, **values)
    return project_dir / filename
