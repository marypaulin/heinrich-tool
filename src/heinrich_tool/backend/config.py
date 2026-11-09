"""Client's business config: rates, VAT, document texts and filenames."""

from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from heinrich_tool.backend.json_files import read_json_model


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


def read_config(path: Path) -> Config:
    return read_json_model(path, Config)
