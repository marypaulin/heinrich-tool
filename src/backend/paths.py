"""
Path and file discovery utilities for heinrich-tool.
"""

import logging
from pathlib import Path

from .config import Config
from .messages import Messages

HEINRICH_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = HEINRICH_ROOT / "config.json"

TEMPLATES_DIR = HEINRICH_ROOT / "templates"
VORDRUCK_PATH = TEMPLATES_DIR / "Vordruck.docx"
INTERMEDIATE_ROOT = TEMPLATES_DIR / "intermediate"
INTERMEDIATE_FILENAME = "Vordruck_Rechnung_{project_number}.docx"


def _format_filename(template: str, **values: str) -> str:
    """Fill the filename template placeholders with values"""
    try:
        return template.format(**values)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(
            f"Missing placeholder '{missing}' in config filename template"
        ) from e


def get_project_dir(data_root: Path, project_number: str) -> tuple[Path, list[str]]:
    """Find the folder with the given 4-digit project number as prefix."""
    messages = Messages()
    for folder in data_root.iterdir():
        if folder.is_dir() and folder.name.startswith(f"{project_number} "):
            display_folder = get_display_path(folder)
            logging.info(f"Found project folder: {display_folder}")
            messages.info(f"Projektordner gefunden ({display_folder})")
            return folder, messages.items
    raise FileNotFoundError(f"No folder found for project number {project_number}")


def get_latest_csv_path(project_dir: Path, config: Config) -> tuple[Path, list[str]]:
    """Find the latest CSV file in the order folder."""
    messages = Messages()
    csv_files = list(project_dir.glob(config.filenames["CSV_NAME_RE"]))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {project_dir}")
    latest = max(csv_files, key=lambda p: p.stat().st_mtime)
    display_latest = latest.name
    logging.info(f"Using CSV file: {display_latest}")
    messages.info(f"CSV-Datei gefunden ({display_latest})")
    return latest, messages.items


def get_intermediate_project_dir(project_number: str) -> Path:
    """templates/intermediate/<project_number>/"""
    path = INTERMEDIATE_ROOT / project_number
    return path


def get_intermediate_template_path(project_number: str) -> Path:
    """templates/intermediate/<project_number>/Vordruck_Rechnung_<project_number>.docx"""
    filename = _format_filename(
        INTERMEDIATE_FILENAME,
        project_number=project_number,
    )
    path = get_intermediate_project_dir(project_number) / filename
    return path


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


def get_delivery_target_path(
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


def get_order_target_path(
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


def get_display_path(path: Path) -> str:
    """Get relative grandparent path for logging purposes"""
    display_path = f"{path.parent.parent.name}/{path.parent.name}/{path.name}"
    return display_path
