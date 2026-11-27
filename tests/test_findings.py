"""Tests that fail if the findings stop holding.

Each asserts a claim the write-up makes, including the ones derived from
Rupeeflo's published figures. If a published number is updated and the code
is pointed at the new one, the test that encodes the old conclusion breaks --
which is the point.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import advisor as a  # noqa: E402
import onboarding as o  # noqa: E402
import pricing as p  # noqa: E402


# --- pricing: the shape of the published brokerage -----------------------------

def test_the_two_accounts_cost_exactly_the_same_below_ten_thousand():
    """The headline finding on pricing.

    Both caps are above 0.5% of a Rs 10,000 trade, so the percentage binds for
    both and the account choice is cost-neutral. Most retail NRI trades sit
    here.
    """
    assert p.indifference_ceiling() == 10_000
    for v in (1_000, 5_000, 9_999, 10_000):
        assert p.compare(v).identical is True


def test_the_gap_opens_between_ten_and_forty_thousand_then_stops():
    assert p.cap_binds_above("nro_non_pis") == 10_000
    assert p.cap_binds_above("nre_pis") == 40_000
    assert p.compare(25_000).ratio == 2.5
    assert p.compare(40_000).ratio == 4.0
    # Beyond the point both caps bind, the ratio is frozen.
    assert p.compare(100_000).ratio == 4.0
    assert p.compare(5_000_000).ratio == 4.0
    assert p.max_ratio() == 4.0


def test_the_cost_difference_is_small_for_a_typical_investor():
    """Why brokerage does not belong at the top of the flow.

    A monthly investor putting Rs 25,000 to work pays Rs 900 a year more on
    the NRE route -- against 31.2% TDS on NRO interest, which is the figure
    that actually moves money.
    """
    assert p.annual_gap(trades_per_year=12, trade_value_inr=25_000) == 900.0
    assert p.annual_gap(trades_per_year=12, trade_value_inr=5_000) == 0.0


def test_an_active_trader_is_the_only_one_for_whom_it_is_material():
    assert p.annual_gap(trades_per_year=200, trade_value_inr=500_000) == 30_000.0


# --- onboarding: where the seven days go ---------------------------------------

def test_the_published_steps_reconcile_with_the_published_headline():
    """A check worth running on any published funnel: do the parts sum?"""
    assert o.reconciles_with_headline() is True
    assert o.total_elapsed_days() == o.HEADLINE_DAYS == 7


def test_the_customer_spends_under_an_hour_across_seven_days():
    w = o.waiting_share()
    assert w["customer_minutes"] == 55.0
    assert w["share_of_elapsed_time_that_is_waiting"] > 0.99


def test_the_courier_is_most_of_the_wait_and_needs_nothing_from_the_customer():
    """So the lever on 'it takes 7 days' is communication, not speed."""
    w = o.waiting_share()
    assert w["courier_share_of_elapsed"] == pytest.approx(0.7143, abs=0.001)
    courier = [s for s in o.STEPS if s.name == "Courier to Zerodha"][0]
    assert courier.needs_appointment is False


def test_exactly_one_step_requires_scheduling_with_another_person():
    """The only step that can fail on calendars rather than on effort."""
    appts = o.appointment_steps()
    assert len(appts) == 1
    assert appts[0].name == "Notary video call"


def test_three_steps_at_ninety_percent_is_not_ninety_percent():
    """Sequential completion compounds, which is the arithmetic people skip."""
    f = o.uniform_funnel(0.90)
    assert f["end_to_end"] == 0.729
    assert 1 - f["end_to_end"] > 0.27


def test_at_equal_rates_the_earliest_step_costs_the_most_customers():
    f = o.uniform_funnel(0.90)
    assert f["largest_single_loss"] == "Upload documents"
    assert f["rows"][0]["lost"] > f["rows"][-1]["lost"]


def test_six_documents_are_required_before_anything_else_happens():
    assert len(o.DOCUMENTS) == 6
    assert o.STEPS[0].name == "Upload documents"


# --- the account choice is mostly not a choice ---------------------------------

def test_converting_an_existing_account_forces_nro():
    """The page supports only NRO-linked conversion, so preference is irrelevant."""
    r = a.recommend(a.Profile(converting_existing_zerodha_account=True))
    assert r.account == a.NRO
    assert r.determined_by_constraint is True


def test_derivatives_force_nro():
    r = a.recommend(a.Profile(wants_instruments=("equity", "fno")))
    assert r.account == a.NRO
    assert r.determined_by_constraint is True
    assert "FNO" in r.binding_constraints[0]


def test_a_non_pis_bank_closes_the_nre_route():
    r = a.recommend(a.Profile(bank_is_pis_enabled=False))
    assert r.account == a.NRO
    assert r.determined_by_constraint is True


def test_foreign_earnings_only_recommends_nre_on_the_published_reasons():
    r = a.recommend(a.Profile())
    assert r.account == a.NRE
    assert r.determined_by_constraint is False
    assert any("tax-free" in x for x in r.reasons)


def test_a_large_repatriation_need_with_indian_income_needs_both_accounts():
    """The one case a single-answer wizard must not pretend to resolve."""
    r = a.recommend(a.Profile(has_indian_source_income=True,
                              annual_repatriation_need_usd=2_000_000))
    assert r.needs_both is True
    assert r.account is None


def test_half_of_the_representative_profiles_never_get_a_choice():
    profiles = [
        a.Profile(converting_existing_zerodha_account=True),
        a.Profile(wants_instruments=("equity", "fno")),
        a.Profile(bank_is_pis_enabled=False),
        a.Profile(has_indian_source_income=True),
        a.Profile(),
        a.Profile(has_indian_source_income=True,
                  annual_repatriation_need_usd=2_000_000),
    ]
    v = a.constraint_share(profiles)
    assert v["settled_by_constraint"] == 3
    assert v["share"] == 0.5
    assert v["questions_needed"] == 4


def test_four_questions_cover_every_branch():
    """If the wizard needs more questions than this, the claim is overstated."""
    assert len(a.QUESTIONS) == 4
