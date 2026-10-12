# Public data
`events/` is immutable reviewed public fact history. `candidates/` contains **unverified** source fingerprints. `monitor/seen.json` tracks scan baselines only. The SQLite output is generated in untracked `build/`; it is never shared as a writable database. No founder account details or personal outcome data in this repo.

`sources.json` entries may set an optional `max_bytes` (default 1 MB, hard cap 4 MB) for official pages whose HTML is large but whose visible-text fingerprint is stable. Only add a source after repeated fetches give the same fingerprint.
