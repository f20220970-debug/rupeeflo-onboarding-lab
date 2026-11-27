"""What the account choice actually costs, from Rupeeflo's published brokerage.

Every figure here is taken from rupeeflo.com/product (read 22 November 2026)
and is restated in PUBLISHED below. Nothing is estimated.

    NRE (PIS)      0.5% of trade value, or Rs 200, whichever is LOWER
    NRO (Non-PIS)  0.5% of trade value, or Rs 50,  whichever is LOWER

Two caps on the same percentage look like a minor difference on a comparison
table. They are not: a cap changes the cost curve's shape, and the gap it
opens depends entirely on how large the customer's trades are. This module
works out where it starts to bite and where it stops growing, because that is
what decides whether brokerage belongs anywhere near the top of an onboarding
flow.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Published on rupeeflo.com/product, 22 November 2026.
PUBLISHED = {
    "nre_pis": {"rate": 0.005, "cap_inr": 200.0},
    "nro_non_pis": {"rate": 0.005, "cap_inr": 50.0},
}

ACCOUNTS = tuple(PUBLISHED)


def brokerage(account: str, trade_value_inr: float) -> float:
    """Cost of one trade. 'Whichever is lower' means min(percentage, cap)."""
    spec = PUBLISHED[account]
    return min(spec["rate"] * trade_value_inr, spec["cap_inr"])


def cap_binds_above(account: str) -> float:
    """Trade value at which the flat cap starts beating the percentage."""
    spec = PUBLISHED[account]
    return spec["cap_inr"] / spec["rate"]


@dataclass(frozen=True)
class Divergence:
    trade_value_inr: float
    nre_cost: float
    nro_cost: float
    ratio: float
    identical: bool


def compare(trade_value_inr: float) -> Divergence:
    nre = brokerage("nre_pis", trade_value_inr)
    nro = brokerage("nro_non_pis", trade_value_inr)
    return Divergence(
        trade_value_inr=trade_value_inr,
        nre_cost=round(nre, 2),
        nro_cost=round(nro, 2),
        ratio=round(nre / nro, 4) if nro else float("inf"),
        identical=bool(abs(nre - nro) < 1e-9),
    )


def indifference_ceiling() -> float:
    """Below this trade value the two accounts cost exactly the same.

    The percentage binds for both, so the caps never come into play.
    """
    return min(cap_binds_above(a) for a in ACCOUNTS)


def max_ratio() -> float:
    """The largest the cost gap ever gets, once both caps bind."""
    return PUBLISHED["nre_pis"]["cap_inr"] / PUBLISHED["nro_non_pis"]["cap_inr"]


def annual_cost(account: str, trades_per_year: int,
                trade_value_inr: float) -> float:
    return round(brokerage(account, trade_value_inr) * trades_per_year, 2)


def annual_gap(trades_per_year: int, trade_value_inr: float) -> float:
    """What the account choice costs a customer over a year, in rupees."""
    return round(annual_cost("nre_pis", trades_per_year, trade_value_inr)
                 - annual_cost("nro_non_pis", trades_per_year, trade_value_inr), 2)


def curve(values: list[float] | None = None) -> list[Divergence]:
    values = values or [2_000, 5_000, 10_000, 25_000, 40_000, 100_000, 500_000]
    return [compare(v) for v in values]
