# Rupeeflo onboarding lab

Built for a **Rupeeflo PS-II (Bengaluru, Product Intern)** application.

Rupeeflo publishes its whole account-opening flow, its step timings and both brokerage schedules. That is unusual, and it means three product questions can be answered from outside the company with arithmetic rather than opinion. Every figure here is from [rupeeflo.com/product](https://www.rupeeflo.com/product), read 22 November 2026. Nothing here is tax advice.

🌐 **[Live results](https://f20220970-debug.github.io/rupeeflo-onboarding-lab/)** · [Brokerage](src/pricing.py) · [Account rules](src/advisor.py) · [Flow](src/onboarding.py) · [18 tests](tests/test_findings.py)

---

## 1. The brokerage difference does not exist for most customers

Both schedules are "0.5% or a flat cap, whichever is lower" — ₹200 on NRE (PIS), ₹50 on NRO (Non-PIS).

| Trade value | NRE (PIS) | NRO (Non-PIS) | Ratio |
| ---: | ---: | ---: | ---: |
| ₹5,000 | ₹25 | ₹25 | **identical** |
| ₹10,000 | ₹50 | ₹50 | **identical** |
| ₹25,000 | ₹125 | ₹50 | 2.5× |
| ₹40,000 | ₹200 | ₹50 | 4.0× |
| ₹5,00,000 | ₹200 | ₹50 | 4.0× |

Below **₹10,000** a trade the percentage binds for both and the accounts cost **exactly the same**. The gap opens between ₹10,000 and ₹40,000, then **stops growing forever** at 4×.

A customer investing ₹25,000 a month pays **₹900 a year** more on NRE — against **31.2% TDS** on NRO interest, which is the number that actually moves money. A comparison table that leads with brokerage is leading with its least important row.

## 2. The account choice is usually not a choice

The product page presents NRE and NRO as two columns, which frames it as a preference. Read the rows carefully and most of it isn't:

- **Converting an existing Zerodha account** → NRO only; the page supports only NRO-linked conversion
- **F&O, intraday or BTST** → NRO only; not available on the NRE (PIS) route
- **Bank outside the PIS list** → NRE route closed entirely

Of six representative profiles, **three are settled by a hard constraint before preference enters**, and the customer already knows the answer to every one. **Four questions resolve every branch** — including the one case a wizard must refuse to answer: Indian income *plus* a repatriation need above the $1M NRO ceiling needs both accounts, and a human.

## 3. Seven days, fifty-five minutes

| Step | Elapsed | Customer effort | Appointment? |
| --- | ---: | ---: | --- |
| Upload documents | 1 day | ~20 min | — |
| Notary video call | 1 day | 30 min | **yes** |
| Courier to Zerodha | 5 days | ~5 min | — |

The published step timings **reconcile exactly** with the published 7-day headline, which is worth checking before trusting either.

The customer spends **55 minutes** in total. **99.5%** of elapsed time is waiting, and **71%** is a courier moving paper after the customer has already finished. The lever on "it takes a week" is therefore mostly **communication, not speed**.

Exactly one step — the notary call — requires meeting another person at a set time. It is the only step that can fail on calendars rather than on effort, and it is the one worth instrumenting first.

## 4. Three good steps still lose a quarter of the cohort

Every step at a healthy 90% still ends at **72.9%** end to end. Sequential completion compounds, and at equal rates the *earliest* step costs the most customers in absolute terms — an argument for moving whatever can be moved later in the flow.

**These rates are an assumption, not a measurement.** No drop-off data is published and none is invented here; the model supplies the arithmetic, and the rates would come from Rupeeflo's own funnel.

## Run it

```bash
pip install pytest
python -m pytest -q        # 18 tests
python src/build_docs.py   # rebuilds the live page from the models
```

The tests encode the conclusions, not the plumbing. If a published figure changes and the code is pointed at the new one, the test carrying the old conclusion breaks — which is the point of writing them this way.

## What I would want before proposing anything

Real completion rates per step, and the distribution of customer trade sizes. The first decides which step to attack; the second decides whether the brokerage row deserves its prominence at all. Also: where the notary call gets rescheduled, and whether the courier step can report progress, since that is where most of the week goes.

---

Built by Pavitra Seth.
