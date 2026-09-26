"""Tests for turning parsed CSV rows into document line items."""

from datetime import date
from decimal import Decimal

from src.backend.csv_transformer import csv_rows_to_line_items
from src.backend.models import CsvRow, LineItem


def csv_row(
    order_number: str = "90010001",
    duration_hours: Decimal = Decimal("3.00"),
    hourly_rate: Decimal = Decimal("84.90"),
    material_cost: Decimal = Decimal("0.00"),
    row_number: int = 2,
) -> CsvRow:
    return CsvRow(
        row_number=row_number,
        date=date(2025, 7, 24),
        order_number=order_number,
        description="Rahmen Baugruppe 4",
        duration_hours=duration_hours,
        hourly_rate=hourly_rate,
        material_cost=material_cost,
        total_cost=duration_hours * hourly_rate + material_cost,
    )


# — Hours ———————————————————————————————————————————————————————————————————————


def test_row_without_material_becomes_one_hours_item(sample_config):
    line_items, messages = csv_rows_to_line_items([csv_row()], sample_config)

    assert line_items == [
        LineItem(
            kind="hours",
            order_number="90010001",
            quantity=Decimal("3.00"),
            description="Meisterstunde zu Auftrag Nr. 90010001",
            unit_price=Decimal("84.90"),
            total_price=Decimal("254.70"),
        )
    ]
    assert messages == []


def test_each_row_gets_the_description_of_its_hourly_rate(sample_config):
    rows = [
        csv_row(hourly_rate=Decimal("84.90")),
        csv_row(hourly_rate=Decimal("48.00")),
    ]

    line_items, _ = csv_rows_to_line_items(rows, sample_config)

    assert [item.description for item in line_items] == [
        "Meisterstunde zu Auftrag Nr. 90010001",
        "Helferstunde zu Auftrag Nr. 90010001",
    ]


def test_unknown_hourly_rate_falls_back_to_default_with_warning(sample_config):
    line_items, messages = csv_rows_to_line_items(
        [csv_row(hourly_rate=Decimal("65.00"))], sample_config
    )

    assert line_items[0].description == "Arbeitsstunde zu Auftrag Nr. 90010001"
    assert line_items[0].total_price == Decimal("195.00")
    assert len(messages) == 1


def test_line_total_is_rounded_to_cents_half_up(sample_config):
    # No rate in the sample config has odd cents, so none reaches a half cent on
    # half hours; this rate is invented for the rounding case.
    line_items, _ = csv_rows_to_line_items(
        [csv_row(duration_hours=Decimal("0.50"), hourly_rate=Decimal("60.25"))],
        sample_config,
    )

    assert line_items[0].total_price == Decimal("30.13")


# — Material ————————————————————————————————————————————————————————————————————


def test_material_adds_a_material_item_after_the_hours(sample_config):
    line_items, messages = csv_rows_to_line_items(
        [csv_row(duration_hours=Decimal("1.00"), material_cost=Decimal("95.00"))],
        sample_config,
    )

    assert [item.kind for item in line_items] == ["hours", "material"]
    assert line_items[1] == LineItem(
        kind="material",
        order_number="90010001",
        quantity=Decimal(1),
        description="Material zu Auftrag Nr. 90010001",
        unit_price=Decimal("95.00"),
        total_price=Decimal("95.00"),
    )
    assert messages == []


def test_row_without_hours_becomes_only_a_material_item(sample_config):
    line_items, messages = csv_rows_to_line_items(
        [csv_row(duration_hours=Decimal("0.00"), material_cost=Decimal("95.00"))],
        sample_config,
    )

    assert line_items == [
        LineItem(
            kind="material",
            order_number="90010001",
            quantity=Decimal(1),
            description="Material zu Auftrag Nr. 90010001",
            unit_price=Decimal("95.00"),
            total_price=Decimal("95.00"),
        )
    ]
    assert messages == []


# — Skipped rows ————————————————————————————————————————————————————————————————


def test_row_without_order_number_is_skipped_with_warning(sample_config):
    rows = [
        csv_row(order_number="90010001", row_number=2),
        csv_row(order_number="", row_number=3),
        csv_row(order_number="90010002", row_number=4),
    ]

    line_items, messages = csv_rows_to_line_items(rows, sample_config)

    assert [item.order_number for item in line_items] == ["90010001", "90010002"]
    assert len(messages) == 1


def test_row_without_hours_and_material_is_skipped_with_warning(sample_config):
    line_items, messages = csv_rows_to_line_items(
        [csv_row(duration_hours=Decimal("0.00"), material_cost=Decimal("0.00"))],
        sample_config,
    )

    assert line_items == []
    assert len(messages) == 1


# — Order of items ——————————————————————————————————————————————————————————————


def test_items_follow_the_csv_order(sample_config):
    rows = [
        csv_row(order_number="90010001", material_cost=Decimal("30.00")),
        csv_row(order_number="90010002"),
    ]

    line_items, _ = csv_rows_to_line_items(rows, sample_config)

    assert [(item.order_number, item.kind) for item in line_items] == [
        ("90010001", "hours"),
        ("90010001", "material"),
        ("90010002", "hours"),
    ]
