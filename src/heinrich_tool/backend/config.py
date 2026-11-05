"""Client's business config: rates, VAT, document texts and filenames."""

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class DocumentConfig:
    doctype: str
    header: str
    delivery_days: int


@dataclass(frozen=True)
class Config:
    rate_descriptions: dict[Decimal, str]
    default_rate_description: str
    date_format: str
    vat_rate: Decimal
    documents: dict[str, DocumentConfig]
    filenames: dict[str, str]


DOCUMENT_KEYS = ("OFFER", "DELIVERY_NOTE", "INVOICE", "ORDER_CONFIRMATION")


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
    _require_keys(raw, "DOCUMENTS", DOCUMENT_KEYS)
    _require_keys(raw, "FILENAMES", (*DOCUMENT_KEYS, "CSV_GLOB"))

    rate_descriptions_raw = raw["RATE_DESCRIPTIONS"]
    rate_descriptions = {Decimal(k): v for k, v in rate_descriptions_raw.items()}

    default_rate_description = raw["DEFAULT_RATE_DESCRIPTION"]
    date_format = raw["DATE_FORMAT"]
    vat_rate = Decimal(raw["VAT_RATE"])

    documents_raw = raw["DOCUMENTS"]
    documents = {}
    for key, value in documents_raw.items():
        if key in ["OFFER", "DELIVERY_NOTE"]:
            delivery_days = value.get("DELIVERY_DAYS", 21)
        else:
            delivery_days = 0
        documents[key] = DocumentConfig(
            doctype=value["DOCTYPE"],
            header=value["HEADER"],
            delivery_days=delivery_days,
        )

    filenames = raw["FILENAMES"]

    return Config(
        rate_descriptions=rate_descriptions,
        default_rate_description=default_rate_description,
        date_format=date_format,
        vat_rate=vat_rate,
        documents=documents,
        filenames=filenames,
    )
