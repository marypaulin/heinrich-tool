"""Client's business config: rates, VAT, document texts and filenames."""

from decimal import Decimal
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from heinrich_tool.backend.json_files import read_json_model


# Values match the fields of Documents
class DocumentKind(StrEnum):
    OFFER = "offer"
    DELIVERY_NOTE = "delivery_note"
    INVOICE = "invoice"
    ORDER_CONFIRMATION = "order_confirmation"


class _ConfigModel(BaseModel):
    # Unknown keys are typos or keys an older config still carries; both must surface
    model_config = ConfigDict(frozen=True, extra="forbid")


class DocumentConfig(_ConfigModel):
    doctype: str
    header: str
    filename: str


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

    def document(self, kind: DocumentKind) -> DocumentConfig:
        return getattr(self.documents, kind)


def read_config(path: Path) -> Config:
    return read_json_model(path, Config)
