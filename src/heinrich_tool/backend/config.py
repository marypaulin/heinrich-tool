"""Client's business config: rates, VAT, document texts and filenames."""

import json
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict, ValidationError


class _ConfigModel(BaseModel):
    # Unknown keys are typos in the client's file, e.g. a misspelled
    # delivery_days that would otherwise silently fall back to its default
    model_config = ConfigDict(frozen=True, extra="forbid")


class DocumentConfig(_ConfigModel):
    doctype: str
    header: str
    filename: str
    delivery_days: int = 0


class Documents(_ConfigModel):
    offer: DocumentConfig
    delivery_note: DocumentConfig
    invoice: DocumentConfig
    order_confirmation: DocumentConfig


class Config(_ConfigModel):
    rate_descriptions: dict[Decimal, str]
    default_rate_description: str
    date_format: str
    vat_rate: Decimal
    csv_glob: str
    documents: Documents

    def document(self, doc_key: str) -> DocumentConfig:
        return getattr(self.documents, doc_key)


def load_config(path: Path) -> Config:
    """Load the config, rejecting any invalid entry with ValueError.

    The client edits the file directly, so problems are user errors to
    report, not crashes. The message lists every problem with its key path,
    e.g. "documents.invoice.filename: Field required".
    """
    # Some Windows editors save UTF-8 with BOM
    raw = json.loads(path.read_text(encoding="utf-8-sig"), parse_float=Decimal)
    try:
        return Config.model_validate(raw)
    except ValidationError as e:
        problems = "; ".join(
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in e.errors()
        )
        raise ValueError(f"Invalid config.json: {problems}") from e
