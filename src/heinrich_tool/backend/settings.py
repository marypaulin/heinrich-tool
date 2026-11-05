"""Machine-local settings: where data root, config and template lie on this computer."""

from pathlib import Path

from platformdirs import user_config_dir
from pydantic import BaseModel, ConfigDict

# Local, not roaming: the paths differ per computer and must not travel with
# the Windows profile.
SETTINGS_PATH = Path(user_config_dir("HeinrichTool", appauthor=False)) / "settings.json"


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    data_root: Path
    config_path: Path
    template_path: Path


def read_settings(path: Path) -> Settings | None:
    """Return the stored settings, or None before they have been set on this computer."""
    if not path.exists():
        return None
    return Settings.model_validate_json(path.read_text(encoding="utf-8"))


def write_settings(path: Path, settings: Settings) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(settings.model_dump_json(), encoding="utf-8")
