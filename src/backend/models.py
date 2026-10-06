"""Domain models for CSV data and document generation."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal

from .formatting import format_price
from .money import round_cents
from .placeholders import (
    PH_DATE_TODAY,
    PH_DELIVERY_DATE,
    PH_DOCTYPE,
    PH_HEADER,
    PH_PROJECT_NO,
    PH_RECEIPT_NO,
    PH_SUM_GROSS,
    PH_SUM_NET,
    PH_VAT,
)


@dataclass(frozen=True)
class CsvRow:
    row_number: int
    date: date
    order_number: str
    description: str
    duration_hours: Decimal
    hourly_rate: Decimal
    material_cost: Decimal
    total_cost: Decimal  # Not used, totals are always recomputed


@dataclass(frozen=True)
class LineItem:
    kind: Literal["hours", "material"]
    order_number: str
    quantity: Decimal
    description: str
    unit_price: Decimal
    total_price: Decimal


@dataclass(frozen=True)
class Totals:
    sum_net: Decimal
    vat: Decimal
    sum_gross: Decimal

    @staticmethod
    def calculate_sums_and_vat(
        line_items: list[LineItem], vat_rate: Decimal
    ) -> Totals:
        """Calculate sum_net, vat, and sum_gross from LineItems.

        Each value is rounded to cents in order, and the VAT is calculated from
        the already rounded net sum. Rounding all three independently from the
        raw sums would let the three amounts printed on the document differ by a cent.
        """
        sum_net = round_cents(
            sum((line_item.total_price for line_item in line_items), Decimal(0))
        )
        vat = round_cents(sum_net * vat_rate)
        sum_gross = sum_net + vat
        return Totals(sum_net=sum_net, vat=vat, sum_gross=sum_gross)

    def to_mapping(self) -> dict[str, str]:
        return {
            PH_SUM_NET: format_price(self.sum_net),
            PH_VAT: format_price(self.vat),
            PH_SUM_GROSS: format_price(self.sum_gross),
        }


@dataclass(frozen=True)
class DocxMeta:
    project_number: str
    receipt_number: str | None
    doctype: str
    header: str
    document_date: date

    def to_mapping(self, date_format: str) -> dict[str, str]:
        return {
            PH_DATE_TODAY: self.document_date.strftime(date_format),
            PH_PROJECT_NO: self.project_number,
            PH_RECEIPT_NO: self.receipt_number or "",
            PH_DOCTYPE: self.doctype,
            PH_HEADER: self.header,
        }


@dataclass(frozen=True)
class DocxDeliveryDate:
    value: date

    def to_mapping(self, date_format: str) -> dict[str, str]:
        return {
            PH_DELIVERY_DATE: self.value.strftime(date_format),
        }
