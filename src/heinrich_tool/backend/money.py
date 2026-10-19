"""Cent precision and commercial rounding for money amounts."""

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def round_cents(amount: Decimal) -> Decimal:
    """Round to cents the commercial way (half up), not half to even."""
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)
