"""German locale formatters for prices and quantities."""

from decimal import Decimal

from heinrich_tool.backend.money import round_cents


def format_quantity(value: Decimal) -> str:
    """Format a quantity value with one decimal,
    German locale (e.g. 1.5 -> 1,5; 2.0 -> 2)."""
    if value % 1 == 0:
        return str(int(value))
    return f"{value:.1f}".replace(".", ",")


def format_price(value: Decimal) -> str:
    """Format a price value with thousands separator and two decimals,
    German locale (e.g. 1234.5 -> 1.234,50€).

    Rejects amounts finer than cents instead of rounding them: every amount is
    rounded where it is calculated, so one arriving here unrounded is a bug.
    """
    cents = round_cents(value)
    if cents != value:
        raise ValueError(f"Price not rounded to cents: {value}")
    return f"{cents:,f}".replace(",", "X").replace(".", ",").replace("X", ".") + "€"
