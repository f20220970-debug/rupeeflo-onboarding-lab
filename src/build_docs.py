"""Rebuild docs/index.html from the models.  python src/build_docs.py"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import advisor as a  # noqa: E402
import onboarding as o  # noqa: E402
import pricing as p  # noqa: E402

OUT = ROOT / "docs" / "index.html"
REPO = "https://github.com/f20220970-debug/rupeeflo-onboarding-lab"

PROFILES = [
    ("Converting an existing Zerodha account", a.Profile(converting_existing_zerodha_account=True)),
    ("Wants F&O", a.Profile(wants_instruments=("equity", "fno"))),
    ("Bank not PIS-enabled", a.Profile(bank_is_pis_enabled=False)),
    ("Has Indian rental income", a.Profile(has_indian_source_income=True)),
    ("Foreign earnings only", a.Profile()),
    ("Indian income + >$1M repatriation", a.Profile(has_indian_source_income=True,
                                                    annual_repatriation_need_usd=2_000_000)),
]


def main() -> int:
    w = o.waiting_share()
    uni = o.uniform_funnel(0.90)
    share = a.constraint_share([pr for _, pr in PROFILES])

    prows = "".join(
        f"<tr{' class=hi' if d.identical else ''}>"
        f"<td class='n'>{d.trade_value_inr:,.0f}</td>"
        f"<td class='n'>{d.nre_cost:,.0f}</td>"
        f"<td class='n'>{d.nro_cost:,.0f}</td>"
        f"<td class='n'>{d.ratio:.2f}&times;</td>"
        f"<td>{'identical' if d.identical else ''}</td></tr>"
        for d in p.curve())

    srows = "".join(
        f"<tr><td>{s.name}</td><td class='n'>{s.elapsed_days:g}</td>"
        f"<td class='n'>{s.customer_minutes:g} min</td>"
        f"<td>{'yes' if s.needs_appointment else '&mdash;'}</td>"
        f"<td class='why'>{s.source}</td></tr>"
        for s in o.STEPS)

    frows = "".join(
        f"<tr><td>{r['step']}</td><td class='n'>{r['entered'] * 100:.0f}%</td>"
        f"<td class='n'>{r['exited'] * 100:.1f}%</td>"
        f"<td class='n'>{r['lost'] * 100:.1f} pp</td></tr>"
        for r in uni["rows"])

    arows = ""
    for label, prof in PROFILES:
        r = a.recommend(prof)
        if r.needs_both:
            verdict, cls = "Both accounts", "warn"
        else:
            verdict = "NRE (PIS)" if r.account == a.NRE else "NRO (Non-PIS)"
            cls = "ok" if not r.determined_by_constraint else "bad"
        if r.binding_constraints:
            why = r.binding_constraints[0]
        elif r.needs_both:
            why = next(x for x in r.reasons if "repatriat" in x.lower())
        else:
            why = r.reasons[0]
        tag = "constraint" if r.determined_by_constraint else "choice"
        arows += (f"<tr><td>{label}</td>"
                  f"<td><span class='chip {cls}'>{verdict}</span></td>"
                  f"<td class='n'>{tag}</td><td class='why'>{why}</td></tr>")

    html = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Rupeeflo Onboarding Lab</title>
<style>
:root{{--bg:#fbfaf9;--panel:#fff;--ink:#17171a;--muted:#6a6a72;--line:#e7e4e0;
  --accent:#1c5d8c;--ok:#1f6f4a;--bad:#8a5a1f;--warn:#b4411f}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{
  --bg:#131318;--panel:#1c1c23;--ink:#eceaf0;--muted:#9b99a3;--line:#2b2b35;
  --accent:#7cc0ef;--ok:#6fcf97;--bad:#e0b25e;--warn:#e87f52}}}}
:root[data-theme="dark"]{{--bg:#131318;--panel:#1c1c23;--ink:#eceaf0;--muted:#9b99a3;
  --line:#2b2b35;--accent:#7cc0ef;--ok:#6fcf97;--bad:#e0b25e;--warn:#e87f52}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 ui-sans-serif,-apple-system,"Segoe UI",Inter,system-ui,sans-serif}}
.wrap{{max-width:880px;margin:0 auto;padding:48px 16px 80px}}
h1{{font-size:clamp(1.7rem,4.5vw,2.4rem);line-height:1.15;margin:0 0 8px;letter-spacing:-.025em}}
h2{{font-size:1.15rem;margin:46px 0 6px;letter-spacing:-.01em}}
.sub{{color:var(--muted);margin:0 0 6px}}
.lede{{color:var(--muted);max-width:64ch;margin:0 0 26px}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px;margin:12px 0;overflow-x:auto}}
.kpis{{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin:24px 0}}
.kpi{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px}}
.kpi .n{{font-size:1.5rem;font-weight:650;letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.kpi .l{{color:var(--muted);font-size:.82rem;margin-top:2px}}
table{{width:100%;border-collapse:collapse;font-size:.9rem;font-variant-numeric:tabular-nums}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
td.n,th.n{{text-align:right;white-space:nowrap}}
th{{color:var(--muted);font-weight:600;font-size:.76rem;text-transform:uppercase;letter-spacing:.05em}}
tbody tr:last-child td{{border-bottom:none}}
td.why{{color:var(--muted);font-size:.83rem}}
tr.hi td{{color:var(--accent);font-weight:600}}
.chip{{display:inline-block;padding:1px 9px;border-radius:999px;font-size:.74rem;
  font-weight:650;white-space:nowrap;border:1px solid currentColor}}
.chip.ok{{color:var(--ok)}} .chip.bad{{color:var(--bad)}} .chip.warn{{color:var(--warn)}}
.note{{font-size:.88rem;color:var(--muted);max-width:66ch}}
a{{color:var(--accent)}}
</style></head><body><div class="wrap">

<h1>Where the seven days go</h1>
<p class="sub">Rupeeflo's published onboarding flow and brokerage, taken apart</p>
<p class="lede">Rupeeflo publishes its whole account-opening flow, its step timings and
both brokerage schedules. That is unusual, and it means three product questions can be
answered from the outside, with arithmetic rather than opinion.</p>

<div class="kpis">
  <div class="kpi"><div class="n">&#8377;{p.indifference_ceiling():,.0f}</div><div class="l">trade size below which the account choice is cost-neutral</div></div>
  <div class="kpi"><div class="n">{p.max_ratio():.0f}&times;</div><div class="l">the largest the brokerage gap ever gets</div></div>
  <div class="kpi"><div class="n">{w['customer_minutes']:.0f} min</div><div class="l">customer effort across the 7-day process</div></div>
  <div class="kpi"><div class="n">{w['courier_share_of_elapsed'] * 100:.0f}%</div><div class="l">of elapsed time is courier transit</div></div>
</div>

<h2>1. The brokerage difference does not exist for most customers</h2>
<div class="panel">
<table><thead><tr><th class='n'>Trade value (&#8377;)</th><th class='n'>NRE (PIS)</th>
<th class='n'>NRO (Non-PIS)</th><th class='n'>Ratio</th><th></th></tr></thead>
<tbody>{prows}</tbody></table>
</div>
<p class="note">Both schedules are &ldquo;0.5% or a flat cap, whichever is lower&rdquo; &mdash;
&#8377;200 on NRE, &#8377;50 on NRO. Below <strong>&#8377;10,000</strong> a trade the
percentage binds for both and the two accounts cost <strong>exactly the same</strong>. The gap
opens between &#8377;10,000 and &#8377;40,000 and then <strong>stops growing forever</strong> at
4&times;. A customer investing &#8377;25,000 a month pays
<strong>&#8377;{p.annual_gap(12, 25_000):,.0f} a year</strong> more on NRE &mdash; against
<strong>31.2% TDS</strong> on NRO interest, which is the number that actually moves money.
A comparison table that leads with brokerage is leading with the least important row.</p>

<h2>2. The account choice is usually not a choice</h2>
<div class="panel">
<table><thead><tr><th>Customer</th><th>Outcome</th><th class='n'>Settled by</th>
<th>Why</th></tr></thead><tbody>{arows}</tbody></table>
</div>
<p class="note">Of six representative profiles,
<strong>{share['settled_by_constraint']} of {share['profiles']}</strong> are settled by a hard
constraint before preference enters: conversion is NRO-only, derivatives are NRO-only, and a
bank outside the PIS list closes the NRE route entirely. The customer already knows the answer
to all of these. <strong>{share['questions_needed']} questions resolve every branch</strong>,
including the one case a wizard must refuse to answer &mdash; Indian income plus a repatriation
need above the $1M NRO ceiling needs both accounts, and a human.</p>

<h2>3. Seven days, fifty-five minutes</h2>
<div class="panel">
<table><thead><tr><th>Step</th><th class='n'>Elapsed</th><th class='n'>Customer effort</th>
<th>Appointment?</th><th>Published source</th></tr></thead><tbody>{srows}</tbody></table>
</div>
<p class="note">The published step timings reconcile exactly with the published
<strong>7-day</strong> headline, which is worth checking before trusting either. The customer
spends <strong>{w['customer_minutes']:.0f} minutes</strong> in total;
<strong>{w['share_of_elapsed_time_that_is_waiting'] * 100:.1f}%</strong> of the elapsed time is
waiting, and <strong>{w['courier_share_of_elapsed'] * 100:.0f}%</strong> is a courier moving
paper after the customer has already finished. So the lever on &ldquo;it takes a week&rdquo; is
mostly <em>communication</em>, not speed. Exactly one step &mdash; the notary call &mdash;
needs the customer to meet another person at a set time, and that is the only step that can
fail on calendars rather than on effort.</p>

<h2>4. And three good steps still lose a quarter of the cohort</h2>
<div class="panel">
<table><thead><tr><th>Step</th><th class='n'>Entering</th><th class='n'>Surviving</th>
<th class='n'>Lost</th></tr></thead><tbody>{frows}</tbody></table>
</div>
<p class="note">Every step at a healthy 90% still ends at
<strong>{uni['end_to_end'] * 100:.1f}%</strong> end to end &mdash; sequential completion
compounds, and three steps at 90% is not 90%. At equal rates the <em>earliest</em> step costs
the most customers in absolute terms, which is an argument for moving whatever can be moved
later in the flow. <strong>These rates are an assumption, not a measurement</strong> &mdash;
no drop-off data is published, and none is invented here. What the model supplies is the
arithmetic; the rates would come from Rupeeflo's own funnel.</p>

<h2>What I would want before proposing anything</h2>
<p class="note">Real completion rates per step, and the distribution of customer trade sizes
&mdash; the first decides which step to attack, the second decides whether the brokerage row
deserves its prominence at all. Also where the notary call gets rescheduled, since that is the
only step with a coordination failure mode, and whether the courier step can report progress,
since that is where most of the week goes.</p>

<p class="note" style="margin-top:40px">
Built for a Rupeeflo PS-II application by Pavitra Seth. Every published figure is from
rupeeflo.com/product, read 22 November 2026; nothing here is tax advice. &middot;
<a href="{REPO}/blob/main/src/pricing.py">Brokerage</a> &middot;
<a href="{REPO}/blob/main/src/advisor.py">Account rules</a> &middot;
<a href="{REPO}/blob/main/src/onboarding.py">Flow</a> &middot;
<a href="{REPO}/blob/main/tests/test_findings.py">18 tests</a> &middot;
<a href="{REPO}">Repository</a>
</p>
</div></body></html>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html)
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
