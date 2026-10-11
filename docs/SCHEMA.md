# Immutable event ledger v0.1

Public events are single JSON files under `data/events/YYYY-MM-DD/<event_id>.json`. One file per event avoids several agents concurrently rewriting a SQLite binary. SQLite and `docs/feed.json` are *reproducible projections*.

Each event has `schema_version: 1`, unique `event_id`, `event_type` (`observation`, `action`, `outcome`), `subject_id` (lowercase slug), `recorded_at` (actual UTC timestamp), `actor`, `review_state` (`verified_public` or `needs_review`), `source_url` (first-party HTTPS URL), and `facts` (object of simple public scalar values). Optional `source_sha256` is a 64-character SHA-256 hex string; optional `note` describes evidence limits.

A program's `verified_public` state verifies **published source facts**, not the founder's eligibility, approval or realized benefit. The dashboard excludes unreviewed observations. A hash change alone is **not** a material opportunity change.

Event files should be appended, not overwritten. Errors require a subsequent corrective observation. A derived status `NEW`, `CHANGED` or `UNCHANGED` compares the last two *reviewed* observations of the same subject. Outcomes here must be non-sensitive; private founder history belongs outside this public repo.

```bash
python scripts/ledger.py validate
python scripts/ledger.py build --db build/leverage.sqlite --feed docs/feed.json
```
