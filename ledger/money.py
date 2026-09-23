"""ISO 4217 money: currency code + integer minor units. Never float."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping

# ISO 4217 minor-unit exponents (Table A.1).
EXPONENTS: Mapping[str, int] = {
    "AED": 2,  # United Arab Emirates dirham
    "BHD": 3,  # Bahraini dinar
}

ISO_NUMERIC: Mapping[str, str] = {
    "AED": "784",
    "BHD": "048",
}


class MoneyError(ValueError):
    """Invalid currency or amount for ISO 4217 scale."""


@dataclass(frozen=True, slots=True)
class Money:
    """Amount in a single ISO 4217 currency, stored as integer minor units."""

    currency: str
    minor: int

    def __post_init__(self) -> None:
        if self.currency not in EXPONENTS:
            raise MoneyError(f"unsupported currency: {self.currency!r}")
        if not isinstance(self.minor, int) or isinstance(self.minor, bool):
            raise MoneyError(f"minor must be int, got {type(self.minor)!r}")

    @property
    def exponent(self) -> int:
        return EXPONENTS[self.currency]

    def __str__(self) -> str:
        return format_money(self)

    def __neg__(self) -> Money:
        return Money(self.currency, -self.minor)

    def _same_ccy(self, other: Money) -> None:
        if self.currency != other.currency:
            raise MoneyError(
                f"currency mismatch: {self.currency} vs {other.currency}"
            )

    def __add__(self, other: Money) -> Money:
        self._same_ccy(other)
        return Money(self.currency, self.minor + other.minor)

    def __sub__(self, other: Money) -> Money:
        self._same_ccy(other)
        return Money(self.currency, self.minor - other.minor)

    def __lt__(self, other: Money) -> bool:
        self._same_ccy(other)
        return self.minor < other.minor

    def __le__(self, other: Money) -> bool:
        self._same_ccy(other)
        return self.minor <= other.minor

    def __gt__(self, other: Money) -> bool:
        self._same_ccy(other)
        return self.minor > other.minor

    def __ge__(self, other: Money) -> bool:
        self._same_ccy(other)
        return self.minor >= other.minor


def zero(currency: str) -> Money:
    return Money(currency, 0)


def from_display(currency: str, text: str) -> Money:
    """Parse a display string that must already match the currency's scale.

    Examples: from_display("AED", "1200.00"), from_display("BHD", "10.000").
    Rejects wrong fraction length (e.g. AED "1.2" or AED "1.234").
    """
    if currency not in EXPONENTS:
        raise MoneyError(f"unsupported currency: {currency!r}")
    exp = EXPONENTS[currency]
    if "." in text:
        whole, frac = text.split(".", 1)
        if not whole or (whole[0] == "-" and len(whole) == 1):
            raise MoneyError(f"malformed amount: {text!r}")
        if not frac.isdigit() or len(frac) != exp:
            raise MoneyError(
                f"{currency} requires exactly {exp} decimal place(s), got {text!r}"
            )
        sign = -1 if whole.startswith("-") else 1
        digits = whole.lstrip("-")
        if not digits.isdigit():
            raise MoneyError(f"malformed amount: {text!r}")
        minor = sign * (int(digits) * (10**exp) + int(frac))
    else:
        if exp != 0:
            raise MoneyError(
                f"{currency} requires exactly {exp} decimal place(s), got {text!r}"
            )
        minor = int(text)
    return Money(currency, minor)


def format_money(m: Money) -> str:
    exp = m.exponent
    sign = "-" if m.minor < 0 else ""
    abs_minor = abs(m.minor)
    whole = abs_minor // (10**exp)
    frac = abs_minor % (10**exp)
    return f"{m.currency} {sign}{whole}.{frac:0{exp}d}"


def round_interest_minor(balance_minor: int, rate_bps: int, currency: str) -> int:
    """0.04% per day = 4 / 10_000 of balance. ROUND_HALF_UP to currency scale."""
    if balance_minor <= 0:
        return 0
    # rate_bps here means basis points of a percent? Spec: 0.04% = 4/10000.
    # We pass numerator 4 and denominator 10000.
    raw = (Decimal(balance_minor) * Decimal(rate_bps)) / Decimal(10_000)
    quantized = raw.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(quantized)


def split_equal_with_remainder(total_minor: int, parts: int) -> list[int]:
    """Largest-remainder split so parts sum exactly to total_minor."""
    if parts <= 0:
        raise MoneyError("parts must be positive")
    base = total_minor // parts
    rem = total_minor % parts
    # Put remainder fils on the last instalment(s).
    out = [base] * parts
    for i in range(rem):
        out[parts - 1 - i] += 1
    return out
