# LEVERAGE//SEEKER — Compounding intelligence protocol v1

**North star:** Accumulate a truthful, reusable history of opportunity terms, their changes, closures, distribution signals and eventual outcomes. The asset should be useful to other independent builders even if its owner cannot actively operate it.

## Two distinct ledgers
1. `data/events/` is the pre-existing, reviewed immutable evidence engine for published opportunity facts. Do not rewrite historical records.
2. `data/daily/YYYY-MM-DD.json` is a lightweight daily **delta journal**. Only record genuinely new or materially rechecked observations. There is no requirement to publish an entry every day. If there is no meaningful delta, report that and leave the journal unchanged.

`docs/intelligence.json` is a deterministic projection of reviewed daily journal entries, **not** a source of truth. Run `python scripts/compile_daily.py build` to regenerate. It may be used by a future searchable free site; it does not confer commercial rights to third-party data.

## An observation is a dated claim, not a guaranteed opportunity
- Stable `id` across runs (e.g., `us-small-business-grant-example`); chronological append-only daily files.
- `status` is `NEW`, `CHANGED`, `CLOSED`, `BLOCKED`, `REJECTED` or `WATCH`. **CHANGED** requires a substantive difference, not merely a changed page hash.
- `verification` is `source_checked` (we verified exactly what a cited source currently *says*) or `needs_review`; source-checked **does not** establish approval, eligibility or truth of a self-reported business outcome.
- `evidence_level` is `first_party`, `firsthand_report`, or `secondary`. Prioritize official terms; use firsthand reports only to verify that *the statement was made*, not to infer true conversion rates.
- Include original HTTPS URL and UTC check time; explain the delta, real access terms, cash vs credits vs hypothetical revenue, deadlines, friction and next recheck. Use `null` when unknown.
- **REJECTED is an asset.** Document stale deadlines, contradictory terms, ineligible offers and unverifiable hype. Do not delete failures.
- Outcome levels are separate: `problem_report`, `reachable_buyer`, `explicit_purchase_intent`, `payment_committed`, `payment_confirmed`. Never upgrade an outcome without direct evidence; never publish someone else's personal/account information.

## Suggested daily procedure for a connected agent
1. Read today's and recent prior entries, `docs/feed.json`, and the current source pages.
2. Research a few high-value opportunities; identify what is genuinely different, what expired, and what was false.
3. Add **0–5** public-only entries in a new `data/daily/YYYY-MM-DD.json` on `research/intelligence-ledger`, not main. When possible regenerate `docs/intelligence.json` and run validation; commit only on this branch. If today's file exists, use a uniquely named dated follow-up only after updating the schema/tools (do **not** silently overwrite).
4. Propose a PR when review is needed. **Never auto-merge, deploy, spend money, contact prospects, apply to programs or handle private customer records.**
5. If GitHub writing isn't available during an automation run, provide a copy-ready record and say **NOT PERSISTED**. A chat response is not a database write.
6. Keep human-facing delivery short: meaningful deltas, what changed, persistence status, reliability, next recheck, optional 15-minute task.

## What makes the data compound?
- Immutable *time-series* allows new vs changed vs closed and detects repeated false positives.
- Source and source-check timestamps enable evidence audits and freshness measurement.
- Rejection reasons make future filters better.
- An explicit `next_check` allows expiring-program monitoring without daily repetition.
- Real outcomes, **only when supported**, allow eventual usefulness calibration. Until then, outcome effectiveness is **UNKNOWN**.

## Future product, not yet launched
- **Free:** honest, dated, source-linked updates; searchable vetted feed; history of closed or changed programs.
- **Paid hypothesis:** personalized eligibility/watchlists, urgent material-change notifications, saved comparisons, action kits, API/export, and evidence-backed decision support.
- Paid features must save users measurable time or money. Don't paywall raw facts, claim users are eligible, or treat credits or prize pools as cash.
- Paid customer accounts, preference data, application records and private outcome attribution must remain outside public Git and require appropriate access controls.

## Priority weighting (simple, not magic)
Rank by **accessible value, eligibility certainty, time to useful action, relevance to independent builders, and ability to reuse the finding**. Down-rank signup/payment friction, short credit expiry, vague eligibility, unsupported claims, and deadlines that have already passed. Record prediction-versus-outcome separately when the outcome actually becomes known.

User's current anchor: SECONDS MATTER — customer-owned missed-call follow-up and callback accountability. Do not force a pivot without clearly superior buyer evidence.
