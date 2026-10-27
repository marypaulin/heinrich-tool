"""Machine-local settings: where data root, config and template lie on this computer."""

import json
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_config_dir

# Local, not roaming: the paths differ per computer and must not travel with
# the Windows profile.
SETTINGS_PATH = Path(user_config_dir("HeinrichTool", appauthor=False)) / "settings.json"


@dataclass(frozen=True)
class Settings:
    data_root: Path
    config_path: Path
    template_path: Path


def read_settings(path: Path) -> Settings | None:
    """Return the stored settings, or None before they have been set on this computer."""
    if not path.exists():
        return None
    raw = json.loads(path.read_text(encoding="utf-8"))
    return Settings(
        data_root=Path(raw["data_root"]),
        config_path=Path(raw["config_path"]),
        template_path=Path(raw["template_path"]),
    )


def write_settings(path: Path, settings: Settings) -> None:
    raw = {
        "data_root": str(settings.data_root),
        "config_path": str(settings.config_path),
        "template_path": str(settings.template_path),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw), encoding="utf-8")
