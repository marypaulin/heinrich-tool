"""Config data model and loader for application settings."""

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


@dataclass(frozen=True)
class DocumentConfig:
    doctype: str
    header: str
    delivery_days: int | None = None


@dataclass(frozen=True)
class Config:
    data_root: Path
    hourly_rate_mapping: dict[Decimal, str]
    hourly_rate_default: str
    date_format: str
    vat_rate: Decimal
    documents: dict[str, DocumentConfig]
    filenames: dict[str, str]


def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)

    # The client's config holds an absolute path; a relative one resolves
    # against the config file's folder.
    data_root = path.parent / raw["DATA_ROOT"]

    mapping_raw = raw["HOURLY_RATE_MAPPING"]
    mapping_converted = {Decimal(k): v for k, v in mapping_raw.items()}

    default_description = raw["HOURLY_RATE_DEFAULT"]
    date_format = raw["DATE_FORMAT"]
    vat_rate = Decimal(raw["VAT_RATE"])

    documents_raw = raw["DOCUMENTS"]
    documents = {}
    for key, value in documents_raw.items():
        if key in ["ANGEBOT", "LIEFERSCHEIN"]:
            delivery_days = value.get("DELIVERY_DAYS", 21)
        else:
            delivery_days = None
        documents[key] = DocumentConfig(
            doctype=value["DOCTYPE"],
            header=value["HEADER"],
            delivery_days=delivery_days,
        )

    filenames = raw["FILENAMES"]

    return Config(
        data_root=data_root,
        hourly_rate_mapping=mapping_converted,
        hourly_rate_default=default_description,
        date_format=date_format,
        vat_rate=vat_rate,
        documents=documents,
        filenames=filenames,
    )
