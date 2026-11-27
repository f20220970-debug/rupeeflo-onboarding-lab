"""Where the seven days actually go.

Rupeeflo's product page publishes the whole flow and its timings, which is
unusual and useful: you can decompose the headline "about 7 days" without
access to a single internal metric.

The decomposition matters because the three steps fail in different ways. One
costs the customer effort, one costs them a scheduled appointment with another
human, and one costs them nothing but elapsed time in which they hear nothing.
A product team that treats "7 days" as one number will try to make the whole
thing faster. The decomposition says which part is even addressable.

Every duration below is published on rupeeflo.com/product (read 22 November
2026). The customer-effort column is the only thing inferred, and it is marked.
"""
from __future__ import annotations

from dataclasses import dataclass

#: Documents the page lists for the standard route.
DOCUMENTS = ("PAN", "passport", "overseas address proof",
             "visa or residence permit", "income proof",
             "NRE/NRO bank statement")

#: Published headline.
HEADLINE_DAYS = 7


@dataclass(frozen=True)
class Step:
    name: str
    elapsed_days: float
    #: Minutes the customer personally spends. Inferred where the page gives
    #: no figure; see `inferred`.
    customer_minutes: float
    #: True when the step needs the customer to coordinate with another person
    #: at a specific time -- the only kind of step that can fail on scheduling.
    needs_appointment: bool
    inferred: bool
    source: str


STEPS = (
    Step("Upload documents", 1.0, 20.0, False, True,
         "page: six documents, verification about one working day"),
    Step("Notary video call", 1.0, 30.0, True, False,
         "page: 15-minute call, notarisation about another 15 minutes"),
    Step("Courier to Zerodha", 5.0, 5.0, False, True,
         "page: documents reach Zerodha in about five days"),
)


def total_elapsed_days() -> float:
    return sum(s.elapsed_days for s in STEPS)


def total_customer_minutes() -> float:
    return sum(s.customer_minutes for s in STEPS)


def waiting_share() -> dict:
    """How much of the wait is the customer having already finished.

    This is the number that decides whether the lever is speed or communication.
    """
    total = total_elapsed_days()
    active_days = total_customer_minutes() / (60 * 24)
    longest_passive = max(s.elapsed_days for s in STEPS if not s.needs_appointment)
    return {
        "elapsed_days": round(total, 2),
        "customer_minutes": round(total_customer_minutes(), 1),
        "customer_days_equivalent": round(active_days, 4),
        "share_of_elapsed_time_that_is_waiting": round(1 - active_days / total, 4),
        "longest_single_passive_step_days": longest_passive,
        "courier_share_of_elapsed": round(longest_passive / total, 4),
    }


def appointment_steps() -> tuple[Step, ...]:
    return tuple(s for s in STEPS if s.needs_appointment)


def reconciles_with_headline() -> bool:
    """The published step timings should add up to the published headline."""
    return abs(total_elapsed_days() - HEADLINE_DAYS) < 1e-9


def funnel(step_completion: dict[str, float]) -> dict:
    """Carry a cohort through the published steps at given completion rates.

    The rates are the caller's assumption -- the page publishes no drop-off
    data and none is invented here. What the model gives is the arithmetic of
    sequential completion, which is the part people get wrong: three steps at
    90% is not 90%.
    """
    remaining = 1.0
    rows = []
    for s in STEPS:
        rate = step_completion[s.name]
        before = remaining
        remaining *= rate
        rows.append({
            "step": s.name,
            "entered": round(before, 4),
            "completion_rate": rate,
            "exited": round(remaining, 4),
            "lost": round(before - remaining, 4),
        })
    worst = max(rows, key=lambda r: r["lost"])
    return {
        "rows": rows,
        "end_to_end": round(remaining, 4),
        "largest_single_loss": worst["step"],
        "largest_single_loss_fraction": worst["lost"],
    }


def uniform_funnel(rate: float) -> dict:
    """Every step at the same rate -- isolates compounding from step quality."""
    return funnel({s.name: rate for s in STEPS})
