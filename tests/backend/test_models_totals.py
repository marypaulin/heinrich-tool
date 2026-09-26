"""Tests for net, VAT and gross calculation and their rendering as placeholders."""

from decimal import Decimal

import pytest

from src.backend.models import LineItem, Totals
from src.backend.placeholders import PH_SUM_GROSS, PH_SUM_NET, PH_VAT

VAT_RATE = Decimal("0.19")


def hours_item(quantity: Decimal, unit_price: Decimal) -> LineItem:
    return LineItem(
        kind="hours",
        order_number="90010001",
        quantity=quantity,
        description="Meisterstunde zu Auftrag Nr. 90010001",
        unit_price=unit_price,
        total_price=quantity * unit_price,
    )


def material_item(unit_price: Decimal) -> LineItem:
    return LineItem(
        kind="material",
        order_number="90010001",
        quantity=Decimal(1),
        description="Material zu Auftrag Nr. 90010001",
        unit_price=unit_price,
        total_price=unit_price,
    )


def test_totals_of_a_single_hours_item():
    totals = Totals.calculate_sums_and_vat(
        [hours_item(Decimal("8.00"), Decimal("84.90"))], VAT_RATE
    )

    assert totals.sum_net == Decimal("679.20")
    assert totals.vat == Decimal("129.05")
    assert totals.sum_gross == Decimal("808.25")


def test_totals_sum_hours_and_material():
    line_items = [
        hours_item(Decimal("8.00"), Decimal("84.90")),
        hours_item(Decimal("3.50"), Decimal("48.00")),
        material_item(Decimal("212.35")),
    ]

    totals = Totals.calculate_sums_and_vat(line_items, VAT_RATE)

    assert totals.sum_net == Decimal("1059.55")
    assert totals.vat == Decimal("201.31")
    assert totals.sum_gross == Decimal("1260.86")


def test_totals_of_no_line_items_are_zero():
    totals = Totals.calculate_sums_and_vat([], VAT_RATE)

    assert totals.sum_net == Decimal("0.00")
    assert totals.vat == Decimal("0.00")
    assert totals.sum_gross == Decimal("0.00")


def test_vat_on_a_half_cent_is_rounded_up():
    totals = Totals.calculate_sums_and_vat([material_item(Decimal("13.50"))], VAT_RATE)

    assert totals.vat == Decimal("2.57")


@pytest.mark.parametrize(
    "unit_price",
    [
        Decimal("13.50"),
        Decimal("0.50"),
        Decimal("2.50"),
        Decimal("4.50"),
        Decimal("17.50"),
        Decimal("288.75"),
        Decimal("1234.50"),
        Decimal("4210.00"),
    ],
)
def test_printed_amounts_add_up(unit_price):
    """Net, VAT and gross are printed side by side; a customer can add them up."""
    totals = Totals.calculate_sums_and_vat([material_item(unit_price)], VAT_RATE)
    mapping = totals.to_mapping()

    def cents(amount: str) -> int:
        return int(amount.removesuffix("€").replace(".", "").replace(",", ""))

    assert cents(mapping[PH_SUM_NET]) + cents(mapping[PH_VAT]) == cents(
        mapping[PH_SUM_GROSS]
    )


def test_to_mapping_formats_every_placeholder():
    totals = Totals.calculate_sums_and_vat(
        [hours_item(Decimal("8.00"), Decimal("84.90"))], VAT_RATE
    )

    assert totals.to_mapping() == {
        PH_SUM_NET: "679,20€",
        PH_VAT: "129,05€",
        PH_SUM_GROSS: "808,25€",
    }
