"""Client's business config: rates, VAT, document texts and filenames."""

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class DocumentConfig:
    doctype: str
    header: str
    filename: str
    delivery_days: int


@dataclass(frozen=True)
class Config:
    rate_descriptions: dict[Decimal, str]
    default_rate_description: str
    date_format: str
    vat_rate: Decimal
    csv_glob: str
    documents: dict[str, DocumentConfig]

    def document(self, doc_key: str) -> DocumentConfig:
        return self.documents[doc_key]


DOCUMENT_KEYS = ("offer", "delivery_note", "invoice", "order_confirmation")


def _require_keys(raw: dict, parent_key: str, keys: tuple[str, ...]) -> None:
    missing = [f"{parent_key}.{key}" for key in keys if key not in raw[parent_key]]
    if missing:
        raise ValueError(f"Missing key in config.json: {', '.join(missing)}")


def load_config(path: Path) -> Config:
    """Load the config, rejecting a missing key with ValueError.

    The client edits the file directly, so a missing key is a user error to report,
    not a crash. All documents are checked up front; otherwise a gap would
    only surface when that document is generated.
    """
    raw = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)
    try:
        return _parse_config(raw)
    except KeyError as e:
        raise ValueError(f"Missing key in config.json: {e.args[0]}") from e


def _parse_config(raw: dict) -> Config:
    _require_keys(raw, "documents", DOCUMENT_KEYS)

    rate_descriptions_raw = raw["rate_descriptions"]
    rate_descriptions = {Decimal(k): v for k, v in rate_descriptions_raw.items()}

    documents = {}
    for key, value in raw["documents"].items():
        if key in ["offer", "delivery_note"]:
            delivery_days = value.get("delivery_days", 21)
        else:
            delivery_days = 0
        documents[key] = DocumentConfig(
            doctype=value["doctype"],
            header=value["header"],
            filename=value["filename"],
            delivery_days=delivery_days,
        )

    return Config(
        rate_descriptions=rate_descriptions,
        default_rate_description=raw["default_rate_description"],
        date_format=raw["date_format"],
        vat_rate=Decimal(raw["vat_rate"]),
        csv_glob=raw["csv_glob"],
        documents=documents,
    )
