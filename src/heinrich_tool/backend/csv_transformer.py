"""CSV row transformation into document-ready LineItem objects."""

import logging
from collections.abc import Iterable
from decimal import Decimal

from heinrich_tool.backend.config import Config
from heinrich_tool.backend.messages import Messages
from heinrich_tool.backend.models import CsvRow, LineItem
from heinrich_tool.backend.money import round_cents

logger = logging.getLogger(__name__)


def _get_hourly_description(csv_row: CsvRow, config: Config, messages: Messages) -> str:
    """Get description based on hourly rate"""
    if csv_row.hourly_rate in config.rate_descriptions:
        return config.rate_descriptions[csv_row.hourly_rate]
    logger.warning(
        f"Unknown hourly rate {csv_row.hourly_rate} in row {csv_row.row_number}, "
        f"using default description '{config.default_rate_description}'"
    )
    messages.warning(
        f"Zeile {csv_row.row_number} mit unbekanntem Stundensatz {csv_row.hourly_rate}, "
        f"nutze Standardbeschreibung ‚{config.default_rate_description}‘"
    )
    return config.default_rate_description


def _hours_item(csv_row: CsvRow, config: Config, messages: Messages) -> LineItem:
    logger.info(f"Creating hours item for order number: {csv_row.order_number}")
    hourly_description = _get_hourly_description(csv_row, config, messages)
    return LineItem(
        kind="hours",
        order_number=csv_row.order_number,
        quantity=csv_row.duration_hours,
        description=f"{hourly_description} zu Auftrag Nr. {csv_row.order_number}",
        unit_price=csv_row.hourly_rate,
        total_price=round_cents(csv_row.hourly_rate * csv_row.duration_hours),
    )


def _material_item(csv_row: CsvRow) -> LineItem:
    logger.info(f"Creating material item for order number: {csv_row.order_number}")
    return LineItem(
        kind="material",
        order_number=csv_row.order_number,
        quantity=Decimal(1),
        # NOTE: Original CSV description currently not used upon client request
        description=f"Material zu Auftrag Nr. {csv_row.order_number}",
        unit_price=csv_row.material_cost,
        total_price=csv_row.material_cost,
    )


def csv_rows_to_line_items(
    csv_rows: Iterable[CsvRow],
    config: Config,
) -> tuple[list[LineItem], list[str]]:
    """
    Transform CsvRow objects into LineItem domain objects.

    This function contains the business logic for converting raw CSV data
    into document-ready line items.

    Transformation rules:
    - If duration_hours is non-zero, an "hours" LineItem is created.
    - If material_cost is non-zero, a "material" LineItem is created after it.
    - LineItems are enriched with calculated totals and derived descriptions.

    Data lineage:
    - Hours LineItem:
        quantity    <- CsvRow.duration_hours
        unit_price  <- CsvRow.hourly_rate
        total_price <- hourly_rate * duration, rounded to cents
    - Material LineItem:
        quantity    <- 1
        unit_price  <- CsvRow.material_cost
        total_price <- material_cost

    Validation and filtering:
    - Rows without an order number are skipped.
    - Rows with neither hours nor material are skipped.
    - All numeric values are assumed to be already parsed and validated
      in the CSV loader.

    Parameters:
        csv_rows: Iterable of parsed CsvRow objects.
        config: Application configuration (hourly rate descriptions, defaults).

    Returns:
        A list of LineItem objects ready for document generation or export.
        A list of info and warning messages to display in UI.
    """
    messages = Messages()
    result = []
    for csv_row in csv_rows:
        if not csv_row.order_number:
            logger.info(f"Skipping row {csv_row.row_number} without order number")
            messages.warning(
                f"Zeile {csv_row.row_number} übersprungen, keine Auftrags-Nr. angegeben"
            )
            continue

        if csv_row.duration_hours == 0 and csv_row.material_cost == 0:
            logger.info(f"Skipping row {csv_row.row_number} without hours or material")
            messages.warning(
                f"Zeile {csv_row.row_number} übersprungen, "
                "weder Stunden noch Material angegeben"
            )
            continue

        if csv_row.duration_hours != 0:
            result.append(_hours_item(csv_row, config, messages))
        if csv_row.material_cost != 0:
            result.append(_material_item(csv_row))

    return result, messages.items
