"""Tests for rounding money amounts to cents."""

from decimal import Decimal

from heinrich_tool.backend.money import round_cents


def test_half_cent_is_rounded_up():
    assert round_cents(Decimal("2.565")) == Decimal("2.57")


def test_less_than_half_cent_is_rounded_down():
    assert round_cents(Decimal("83.6019")) == Decimal("83.60")


def test_whole_amount_gets_two_decimals():
    assert str(round_cents(Decimal(95))) == "95.00"
