#!/usr/bin/env python3
"""Build a self-contained, public-only offline snapshot from reviewed sources.

Requires only the Python standard library; never fetches URLs or reads private data.
"""
import argparse
import hashlib
from html import escape
import json
import os
from pathlib import Path
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from compile_daily import load_runs, make_feed
from ledger import load_events, public_feed

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "build" / "leverage-seeker-continuity.zip"


def _json_bytes(data):
    return (json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")


def _cards(ledger_feed, intelligence_feed):
    cards = []
    for item in ledger_feed["opportunities"]:
        title = escape(str(item.get("facts", {}).get("program", item["subject_id"])))
        state = escape(str(item["state"]))
        timestamp = escape(str(item["recorded_at"]))
        source = escape(str(item["source_url"]), quote=True)
        facts = "".join(
            f"<dt>{escape(str(key).replace('_', ' '))}</dt>"
            f"<dd>{escape(str(value))}</dd>"
            for key, value in sorted(item["facts"].items())
        )
        cards.append(
            f'<article><h3>{title}</h3><p class="meta">Ledger: {state} · checked {timestamp}</p>'
            f'<dl>{facts}</dl><p><a href="{source}" rel="noopener noreferrer">Official source (online only)</a></p></article>'
        )
    for item in intelligence_feed["opportunities"]:
        title = escape(str(item["title"]))
        state = escape(str(item["status"]))
        timestamp = escape(str(item["checked_at"]))
        source = escape(str(item["source_url"]), quote=True)
        claim = escape(str(item["claim"]))
        why_now = escape(str(item["why_now"]))
        cards.append(
            f'<article><h3>{title}</h3><p class="meta">Research: {state} · checked {timestamp}</p>'
            f'<p>{claim}</p><p><strong>Why it matters:</strong> {why_now}</p>'
            f'<p><a href="{source}" rel="noopener noreferrer">Source (online only)</a></p></article>'
        )
    return "\n".join(cards) or "<p>No reviewed public opportunities in this snapshot.</p>"


def render_html(ledger_feed, intelligence_feed):
    count = len(ledger_feed["opportunities"]) + len(intelligence_feed["opportunities"])
    cards = _cards(ledger_feed, intelligence_feed)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LEVERAGE//SEEKER — Offline Continuity Capsule</title>
<style>
:root {{color-scheme:dark}} body {{font:16px/1.55 system-ui,sans-serif;max-width:880px;margin:auto;padding:24px;background:#0d121b;color:#eef3fa}}
header {{border-bottom:1px solid #3c4b5f;margin-bottom:24px}} h1 {{font-size:1.65rem}} a {{color:#8ddcff;overflow-wrap:anywhere}}
article {{border:1px solid #405069;border-radius:12px;padding:18px;margin:16px 0;background:#182335}}
.meta {{font-size:.9rem;color:#c0d0e1}} dl {{display:grid;grid-template-columns:minmax(130px,1fr) 2fr;gap:8px 14px;overflow-wrap:anywhere}}
dt {{font-weight:650}} dd {{margin:0}} .notice {{background:#273244;padding:12px;border-radius:8px}}
</style></head><body>
<header><h1>LEVERAGE//SEEKER // CONTINUITY CAPSULE</h1><p>Offline, read-only public evidence snapshot · {count} reviewed records</p></header>
<p class="notice"><strong>Historical snapshot, not live offers.</strong> Published-source checks do not prove personal eligibility, acceptance, current availability, cash awards, or realized results. No automatic updates occur offline.</p>
<main>{cards}</main>
<footer><p>Local files: <code>ledger.json</code>, <code>intelligence.json</code>, <code>manifest.sha256</code>, <code>README.txt</code>. External source links require a connection.</p></footer>
</body></html>
'''


def build_capsule(output=DEFAULT_OUTPUT, events_dir=None, daily_dir=None):
    # The existing source validators enforce a reviewed-public export boundary.
    ledger = public_feed(load_events(events_dir) if events_dir is not None else load_events())
    intelligence = make_feed(load_runs(daily_dir) if daily_dir is not None else load_runs())
    files = {
        "index.html": render_html(ledger, intelligence).encode("utf-8"),
        "ledger.json": _json_bytes(ledger),
        "intelligence.json": _json_bytes(intelligence),
        "README.txt": (
            "LEVERAGE//SEEKER CONTINUITY CAPSULE\n"
            "==================================\n"
            "Unzip, then open index.html directly in any modern browser (file://).\n"
            "No server, JavaScript, Docker, Ollama, internet, subscription or GPU is required to read.\n\n"
            "This contains ONLY reviewed public projections from the repository's\n"
            "event ledger and source-checked daily research. It does not contain\n"
            "private accounts, raw scraped pages, tokens or the SQLite database.\n"
            "All records are historical; recheck official source URLs when back online.\n"
            "The manifest checks accidental changes, not authorship or authenticity.\n"
            "Check with: sha256sum -c manifest.sha256 (from the extracted directory).\n"
            "Source: https://github.com/wildwrld86/LEVERAGE-SEEKER\n"
        ).encode("utf-8"),
    }
    files["manifest.sha256"] = "".join(
        f"{hashlib.sha256(content).hexdigest()}  {name}\n"
        for name, content in sorted(files.items())
    ).encode("ascii")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".capsule-", suffix=".zip", dir=output.parent, delete=False) as temp:
            temp_path = Path(temp.name)
        with ZipFile(temp_path, "w") as archive:
            for name, content in sorted(files.items()):
                entry = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                entry.compress_type = ZIP_DEFLATED
                entry.external_attr = 0o644 << 16
                archive.writestr(entry, content)
        os.replace(temp_path, output)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(f"Built offline capsule: {build_capsule(args.output)}")


if __name__ == "__main__":
    main()
