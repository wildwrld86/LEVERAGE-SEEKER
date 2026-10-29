#!/usr/bin/env python3
"""Verify public daily opportunity deltas and derive a small distributable feed.

Standard library only. History is file-based; the JSON feed is rebuildable.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DAILY = ROOT / "data" / "daily"
FEED = ROOT / "docs" / "intelligence.json"
ALLOWED_STATUS = {"NEW", "CHANGED", "CLOSED", "BLOCKED", "REJECTED", "WATCH"}
ALLOWED_VERIFICATION = {"source_checked", "needs_review"}
ALLOWED_LEVELS = {"first_party", "firsthand_report", "secondary"}
ALLOWED_VALUES = {"cash", "credit", "discount", "cost_saving", "proposed_revenue", "none", "unknown"}
ALLOWED_SIGNALS = {"none", "problem_report", "reachable_buyer", "explicit_purchase_intent", "payment_committed", "payment_confirmed"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{2,100}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DISALLOWED_FIELDS = {"email", "phone", "api_key", "token", "contact_info", "private_notes", "account_id", "customer_name"}

def check_date(value, nullable=False):
    if nullable and value is None:
        return
    if not isinstance(value, str) or not DATE.fullmatch(value):
        raise ValueError(f"Expected ISO date, got {value!r}")
    date.fromisoformat(value)

def check_text(value, name, limit=1200):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{name} must be nonempty text, <= {limit} characters")

def load_runs(folder=DAILY):
    records = []
    for path in sorted(Path(folder).glob("????-??-??.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(doc, dict) or doc.get("schema_version") != 1:
            raise ValueError(f"{path}: invalid document version")
        check_date(doc.get("date"))
        if path.stem != doc["date"]:
            raise ValueError(f"{path}: mismatched filename/date")
        items = doc.get("observations")
        if not isinstance(items, list) or len(items) > 5:
            raise ValueError(f"{path}: observations must be a list of <= 5 entries")
        ids = set()
        for o in items:
            if not isinstance(o, dict):
                raise ValueError(f"{path}: observation must be an object")
            must = ("id","title","status","source_url","checked_at","claim","why_now","verification","evidence_level","confidence")
            if any(k not in o for k in must) or DISALLOWED_FIELDS.intersection(o):
                raise ValueError(f"{path}: missing required key or disallowed private field")
            if not isinstance(o["id"], str) or not SLUG.fullmatch(o["id"]) or o["id"] in ids:
                raise ValueError(f"{path}: invalid or duplicate ID")
            ids.add(o["id"])
            for key in ("title", "claim", "why_now"):
                check_text(o[key], key)
            if o["status"] not in ALLOWED_STATUS or o["verification"] not in ALLOWED_VERIFICATION:
                raise ValueError(f"{path}: invalid status or verification")
            if o["evidence_level"] not in ALLOWED_LEVELS or o["confidence"] not in ("high","medium","low"):
                raise ValueError(f"{path}: invalid evidence level or confidence")
            url = urlparse(o["source_url"]) if isinstance(o["source_url"],str) else None
            if not url or url.scheme != "https" or not url.hostname or url.username or url.password:
                raise ValueError(f"{path}: HTTPS source URL required")
            timestamp = o["checked_at"]
            if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
                raise ValueError(f"{path}: checked_at must be a UTC Z timestamp")
            datetime.fromisoformat(timestamp[:-1] + "+00:00")
            if o.get("value_type","unknown") not in ALLOWED_VALUES:
                raise ValueError(f"{path}: invalid value type")
            if o.get("buyer_signal","none") not in ALLOWED_SIGNALS:
                raise ValueError(f"{path}: invalid buyer signal")
            for key in ("deadline", "next_check"):
                if key in o:
                    check_date(o[key], nullable=True)
            if "score" in o and (o["score"] is not None and (type(o["score"]) is not int or not (1<=o["score"]<=5))):
                raise ValueError(f"{path}: score must be 1..5 or null")
            if "stackability" in o and (not isinstance(o["stackability"],list) or any(not isinstance(s,str) or len(s)>140 for s in o["stackability"])):
                raise ValueError(f"{path}: invalid stackability")
            for key in ("value","eligibility","friction"):
                if key in o and o[key] is not None:
                    check_text(o[key],key)
            records.append({"date":doc["date"],**o})
    return records

def make_feed(records):
    # Only verified *source checks* enter the distributable feed.
    checked = [r for r in records if r["verification"] == "source_checked"]
    groups = defaultdict(list)
    for r in checked:
        groups[r["id"]].append(r)
    latest = []
    for ident, history in sorted(groups.items()):
        current = history[-1].copy()
        current["first_seen"] = history[0]["date"]
        current["observations_count"] = len(history)
        latest.append(current)
    latest.sort(key=lambda o: (o["date"],o["id"]), reverse=True)
    counts = Counter(r["status"] for r in checked)
    stats = {
        "checked_observations": len(checked),
        "tracked_opportunities": len(groups),
        "changed_observations": counts["CHANGED"],
        "closed_observations": counts["CLOSED"],
        "rejected_observations": counts["REJECTED"],
        "unreviewed_observations": len(records)-len(checked),
    }
    return {
        "schema_version": 1,
        "description": "Source-checked public opportunity statements; NOT proof of approval, individual eligibility, settled revenue, or current service availability.",
        "stats": stats,
        "opportunities": latest
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate","build","report"))
    parser.add_argument("--folder", default=str(DAILY))
    parser.add_argument("--feed", default=str(FEED))
    args = parser.parse_args()
    records = load_runs(args.folder)
    feed = make_feed(records)
    if args.command == "validate":
        print(f"OK: {len(records)} observations validated, {feed['stats']['tracked_opportunities']} source-checked subjects")
    elif args.command == "report":
        print(json.dumps(feed["stats"], indent=2, sort_keys=True))
    else:
        target = Path(args.feed)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(feed, ensure_ascii=False, indent=2, sort_keys=True)+"\n",encoding="utf-8")
        print(f"Compiled {len(records)} observations to {target}")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}",file=sys.stderr)
        sys.exit(1)
