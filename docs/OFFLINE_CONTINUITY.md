# GB-012 — Offline Continuity Capsule

**Why:** Project NOMAD demonstrates the value of usable offline knowledge. LEVERAGE//SEEKER already has a cloud-first, source-linked public ledger. Instead of buying a mini PC or installing a large self-hosted stack, package a small offline **read-only** fallback.

This is **not** a fork or installation of Project NOMAD, not local AI, and not an Internet-independent source verification engine.

## Generate

From the repository root with Python 3.11+ (standard library only):

```sh
python -m unittest discover -s tests -v
python scripts/build_capsule.py
```

Output: `build/leverage-seeker-continuity.zip` (ignored by Git).

Alternatively, once the proposed workflow is available, find the latest successful **Build offline continuity capsule** GitHub Actions run and download its `leverage-seeker-continuity` artifact.

## Use

1. Extract `leverage-seeker-continuity.zip` to any disk or USB storage.
2. Open `index.html` in a modern browser. It renders directly under `file://`, without JavaScript, network requests, local server or GPU.
3. Read the exported `ledger.json` and `intelligence.json` if you want machine-readable data.
4. Optional integrity check from the extracted directory: `sha256sum -c manifest.sha256`.

This ZIP contains only **derived, reviewed public** projections from `data/events/` and source-checked entries from `data/daily/`, plus a static HTML reader and SHA-256 manifest. It does **not** bundle the full event history, candidate records, raw source pages, the SQLite database, applications or credentials. Public-source facts are a trust boundary, but reviewers must still check for accidental personal or licensed material in any source-approved fields.

## Boundaries

- A snapshot is **historical**: offline data does not refresh and URLs can expire.
- Grant/credit terms in the feed are not proof of eligibility, award, current availability, payment or value realized.
- Integrity hashes detect file corruption; they do **not** authenticate the publisher or establish that published claims are true.
- Build and distribution are free only within applicable GitHub quota/service terms. Do not buy hardware, subscribe or deploy infrastructure for this experiment.
- The online GitHub repository remains the source of truth. Do not edit offline outputs and expect them to synchronize.
- No change to `main`, merge, production deployment, scheduled upload or external outreach without owner review.

## Acceptance checks

- CI tests all existing ledger and daily scripts plus offline packaging tests.
- The artifact contains exactly `index.html`, `ledger.json`, `intelligence.json`, `README.txt`, and `manifest.sha256`.
- Unreviewed opportunity material is not exported.
- HTML escapes source-supplied text; the page has no script or remote asset dependency.
- The ZIP passes `unzip -t` and `sha256sum -c`.

## Follow-on decision

If a real user finds this useful, add a light export/download UI to the existing free feed. **Only then** test whether specialized offline knowledge packs solve a recurring paid problem. Keep hardware-heavy NOMAD deployment as a separate, evidence-dependent option.

Upstream reference: https://github.com/Crosstalk-Solutions/project-nomad
