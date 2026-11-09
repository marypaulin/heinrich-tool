"""Reading of the JSON files the client edits or the app writes."""

import json
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ValidationError


def read_json_model[M: BaseModel](path: Path, model: type[M]) -> M:
    """Read a JSON file into a model, rejecting any problem with ValueError.

    The client may edit these files by hand, so problems are user errors to
    report, not crashes. The message names the file and, for invalid entries,
    every problem with its key path, e.g.
    "Invalid config.json: documents.invoice.filename: Field required".
    A missing file raises FileNotFoundError unchanged.
    """
    try:
        # Some Windows editors save UTF-8 with BOM
        raw = json.loads(path.read_text(encoding="utf-8-sig"), parse_float=Decimal)
    except UnicodeDecodeError as e:
        raise ValueError(f"{path.name} is not saved as UTF-8") from e
    except json.JSONDecodeError as e:
        raise ValueError(f"{path.name} is not valid JSON: {e}") from e
    try:
        return model.model_validate(raw)
    except ValidationError as e:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in e.errors()
        )
        raise ValueError(f"Invalid {path.name}: {problems}") from e
