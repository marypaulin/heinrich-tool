"""Config data model and loader for application settings."""

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


def load_config(path: Path) -> Config:
    raw = json.loads(path.read_text(encoding="utf-8"), parse_float=Decimal)

    rate_descriptions_raw = raw["RATE_DESCRIPTIONS"]
    rate_descriptions = {Decimal(k): v for k, v in rate_descriptions_raw.items()}

    default_rate_description = raw["DEFAULT_RATE_DESCRIPTION"]
    date_format = raw["DATE_FORMAT"]
    vat_rate = Decimal(raw["VAT_RATE"])

    documents_raw = raw["DOCUMENTS"]
    documents = {}
    for key, value in documents_raw.items():
        if key in ["ANGEBOT", "LIEFERSCHEIN"]:
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
