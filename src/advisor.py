"""Which account the customer can actually have.

The product page presents NRE (PIS) and NRO (Non-PIS) as a two-column
comparison, which frames the choice as a preference. Read the columns
carefully and most of it isn't: several rows are hard constraints that rule
one option out entirely, and the customer already knows the answer to each.

That matters for the product. A comparison table asks the customer to become
briefly expert in Indian exchange control before they can proceed. The same
facts, asked as four questions, resolve the choice for them -- and the ones
that resolve it are the constraints, not the pricing.

Every rule below comes from rupeeflo.com/product (read 22 November 2026).
Nothing here is tax advice; it reproduces what the page states.
"""
from __future__ import annotations

from dataclasses import dataclass, field

NRE = "nre_pis"
NRO = "nro_non_pis"

#: Published on rupeeflo.com/product, 22 November 2026.
PUBLISHED_FACTS = {
    NRE: {
        "suited_to": "income earned abroad",
        "interest_tax": "tax-free in India",
        "repatriation": "full",
        "instruments": ("equity", "mutual_funds", "etf"),
        "banks": "HDFC, ICICI, Axis, IDFC, IndusInd, Yes Bank",
        "needs_pis_letter": True,
    },
    NRO: {
        "suited_to": "income earned in India, or full trading access",
        "interest_tax": "31.2% TDS",
        "repatriation": "up to $1M per year",
        "instruments": ("equity", "mutual_funds", "etf",
                        "fno", "intraday", "btst"),
        "banks": "any Indian bank",
        "needs_pis_letter": False,
    },
}

#: Instruments the NRE (PIS) route does not cover.
NRO_ONLY_INSTRUMENTS = ("fno", "intraday", "btst")

#: The page states only NRO-linked conversions are supported "for now".
CONVERSION_SUPPORTED = (NRO,)

#: Published repatriation ceiling on the NRO route, in US dollars per year.
NRO_REPATRIATION_LIMIT_USD = 1_000_000


@dataclass(frozen=True)
class Profile:
    """What the customer already knows about themselves."""

    converting_existing_zerodha_account: bool = False
    wants_instruments: tuple[str, ...] = ("equity",)
    has_indian_source_income: bool = False
    annual_repatriation_need_usd: float = 0.0
    bank_is_pis_enabled: bool = True


@dataclass(frozen=True)
class Recommendation:
    account: str | None
    binding_constraints: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    #: True when a hard constraint settled it, so no preference was involved.
    determined_by_constraint: bool = False
    needs_both: bool = False
    notes: tuple[str, ...] = field(default_factory=tuple)


def recommend(p: Profile) -> Recommendation:
    """Resolve the account choice, constraints first."""
    constraints: list[str] = []
    reasons: list[str] = []
    notes: list[str] = []

    # --- hard constraints: these rule an option out, whatever anyone prefers.
    if p.converting_existing_zerodha_account:
        constraints.append(
            "Converting an existing Zerodha account: only NRO-linked "
            "conversion is supported")
    blocked = [i for i in p.wants_instruments if i in NRO_ONLY_INSTRUMENTS]
    if blocked:
        constraints.append(
            f"{', '.join(blocked).upper()} is not available on the NRE (PIS) route")
    if not p.bank_is_pis_enabled:
        constraints.append(
            "Bank is not on the PIS-enabled list, so the NRE (PIS) route is closed")

    if constraints:
        if p.annual_repatriation_need_usd > NRO_REPATRIATION_LIMIT_USD:
            notes.append(
                "Repatriation need exceeds the $1M/year NRO ceiling, but the "
                "constraints above still rule out NRE (PIS). Worth a human "
                "conversation rather than a form.")
        return Recommendation(
            account=NRO,
            binding_constraints=tuple(constraints),
            reasons=("The choice was settled by constraint, not preference.",),
            determined_by_constraint=True,
            notes=tuple(notes),
        )

    # --- no constraints bind: now it is a genuine choice.
    if p.has_indian_source_income:
        reasons.append(
            "Indian-source income has to be routed through an NRO account")
        if p.annual_repatriation_need_usd > NRO_REPATRIATION_LIMIT_USD:
            return Recommendation(
                account=None, needs_both=True,
                reasons=tuple(reasons + [
                    "Repatriation need exceeds the $1M/year NRO ceiling, so "
                    "foreign earnings belong in an NRE account alongside it"]),
            )
        return Recommendation(account=NRO, reasons=tuple(reasons))

    reasons.append("Only foreign earnings are being invested")
    reasons.append("NRE interest is tax-free in India against 31.2% TDS on NRO")
    reasons.append("NRE repatriation is full, with no annual ceiling")
    return Recommendation(account=NRE, reasons=tuple(reasons))


# --- what the wizard would have to ask -----------------------------------------

QUESTIONS = (
    "Are you converting an existing Zerodha account, or opening a new one?",
    "Do you need F&O, intraday or BTST?",
    "Do you have income arising in India (rent, pension, dividends)?",
    "Will you need to repatriate more than $1M in a year?",
)


def constraint_share(profiles: list[Profile]) -> dict:
    """How often the choice is settled by constraint rather than preference.

    If most customers are constrained, the comparison table is answering a
    question they never actually get to ask.
    """
    recs = [recommend(p) for p in profiles]
    determined = sum(1 for r in recs if r.determined_by_constraint)
    return {
        "profiles": len(recs),
        "settled_by_constraint": determined,
        "share": round(determined / len(recs), 4) if recs else 0.0,
        "questions_needed": len(QUESTIONS),
    }
