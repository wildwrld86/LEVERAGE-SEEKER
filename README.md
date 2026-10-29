# LEVERAGE//SEEKER

**Evidence-aware opportunity intelligence for independent builders.** Discover → verify → compare → decide → act → record outcomes → learn.

This public repo is the shared, reviewable collaboration and evidence layer for LEVERAGE//SEEKER and **Creeper (Grok Bot)**. It is an initial working foundation, not a proven autonomous opportunity engine. Sensitive applicant information and proprietary business intelligence belong in a separate private store.

## Run (Python 3.11+, standard library only)
```bash
python -m unittest discover -s tests -v
python scripts/ledger.py validate
python scripts/ledger.py build --db build/leverage.sqlite --feed docs/feed.json
python scripts/ledger.py report
```

## Repository map
- `data/events/YYYY-MM-DD/<event_id>.json`: immutable verified public observations, one file per event. **Source of truth.**
- `data/candidates/`: **unverified** automated page-fingerprint changes for review; never treat a changed hash as a changed grant.
- `data/monitor/seen.json`: last reviewed monitored fingerprints.
- `data/sources.json`: the watchlist of curated first-party URLs.
- `docs/feed.json`: reproducible, reviewed-only public JSON feed.
- `docs/index.html`: mobile-friendly static viewer. To publish: GitHub Settings → Pages → Deploy from branch → main → /docs.
- `build/leverage.sqlite`: derived SQLite database, **local/untracked**, rebuilt from public events.
- `handoffs/CREEPER-001.md`: Creeper's first assignment.
- `AGENTS.md`, `TEAM.md`: coordination, trust boundaries and claims.
- `.github/workflows/`: tests plus review-only daily source scan.

The **private** [Grokbot Desk](https://github.com/wildwrld86/grokbot-desk) is our agent mailbox and GB task registry; project code and public facts live here. The daily scan proposes a PR, **not** a source verification, live application, auto-merge or deployment. GitHub Actions must be enabled and allowed to create pull requests.

**Security:** never publish secrets, email identities, applications, balances, personal eligibility or private outcomes. See [Security](docs/SECURITY.md). The starter record reports an advertised AMD program benefit; it does **not** establish award or account approval.

**Licensing decision pending:** public GitHub visibility is not a license to reuse. No open-source license has yet been granted by the owner.

## Compounding intelligence / future product

The owner has authorized a quiet, low-maintenance research-first direction. The durable goal is a source-linked time series that becomes useful to other independent builders, not a daily stream of transient lists.

- [Compounding intelligence protocol](docs/COMPOUNDING_PROTOCOL.md)
- [Daily delta JSON format](data/daily/README.md)
- [Generated public intelligence JSON](docs/intelligence.json)
- [Future free/paid product direction](docs/PRODUCT_DIRECTION.md)

This is a **scaffold**, not proof that scheduled tasks already commit to GitHub or that a paid offering exists. A dedicated `research/intelligence-ledger` branch can accumulate reviewable, append-only research without changing the public main feed.
