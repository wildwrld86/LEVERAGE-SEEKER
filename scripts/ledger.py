#!/usr/bin/env python3
"""Validate an immutable JSON evidence ledger and rebuild SQLite/public feed."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sqlite3
import sys
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]
EVENTS=ROOT/"data/events"
SLUG=re.compile(r"^[a-z0-9][a-z0-9-]{1,100}$")
ID=re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{4,130}$")
SHA=re.compile(r"^[0-9a-f]{64}$")

def load_events(root=EVENTS):
    events=[]; seen=set()
    for path in sorted(Path(root).glob("*/*.json")):
        e=json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(e,dict): raise ValueError(f"{path}: event is not object")
        required=("schema_version","event_id","event_type","subject_id","recorded_at","actor","review_state","source_url","facts")
        if any(k not in e for k in required): raise ValueError(f"{path}: missing required keys")
        if e["schema_version"]!=1 or e["event_type"] not in ("observation","action","outcome"):
            raise ValueError(f"{path}: bad version or event type")
        if not isinstance(e["event_id"],str) or not ID.fullmatch(e["event_id"]) or e["event_id"] in seen or path.name!=e["event_id"]+".json":
            raise ValueError(f"{path}: invalid, duplicate or mismatched id")
        seen.add(e["event_id"])
        if not isinstance(e["subject_id"],str) or not SLUG.fullmatch(e["subject_id"]):
            raise ValueError(f"{path}: bad subject slug")
        if not isinstance(e["recorded_at"],str) or not e["recorded_at"].endswith("Z"):
            raise ValueError(f"{path}: recorded_at must end in UTC Z")
        dt=datetime.fromisoformat(e["recorded_at"][:-1]+"+00:00")
        if dt.utcoffset()!=timezone.utc.utcoffset(dt) or path.parent.name!=dt.strftime("%Y-%m-%d"):
            raise ValueError(f"{path}: timestamp/path mismatch")
        if not isinstance(e["actor"],str) or not e["actor"].strip() or len(e["actor"])>100:
            raise ValueError(f"{path}: bad actor")
        if e["review_state"] not in ("verified_public","needs_review"):
            raise ValueError(f"{path}: bad review state")
        url=urlparse(e["source_url"]) if isinstance(e["source_url"],str) else None
        if not url or url.scheme!="https" or not url.hostname or url.username or url.password:
            raise ValueError(f"{path}: source must be HTTPS with no credentials")
        facts=e["facts"]
        if not isinstance(facts,dict) or not facts or any(not isinstance(k,str) or k.startswith("_") or not isinstance(v,(str,int,float,bool)) or len(str(v))>1000 for k,v in facts.items()):
            raise ValueError(f"{path}: facts must be nonempty public scalars")
        if "source_sha256" in e and (not isinstance(e["source_sha256"],str) or not SHA.fullmatch(e["source_sha256"])):
            raise ValueError(f"{path}: bad source hash")
        if "note" in e and (not isinstance(e["note"],str) or len(e["note"])>500):
            raise ValueError(f"{path}: bad note")
        if any(k in e for k in ("api_key","token","private_notes","email","phone")):
            raise ValueError(f"{path}: forbidden private field")
        events.append(e)
    return sorted(events,key=lambda e:(e["recorded_at"],e["event_id"]))

def public_feed(events):
    groups=defaultdict(list)
    for e in events:
        if e["event_type"]=="observation" and e["review_state"]=="verified_public":
            groups[e["subject_id"]].append(e)
    opportunities=[]
    for subject,items in sorted(groups.items()):
        last=items[-1]; prev=items[-2] if len(items)>1 else None
        status="NEW" if prev is None else ("CHANGED" if prev["facts"]!=last["facts"] else "UNCHANGED")
        opportunities.append({"subject_id":subject,"recorded_at":last["recorded_at"],"source_url":last["source_url"],"facts":last["facts"],"state":status,"observation_count":len(items),"source_sha256":last.get("source_sha256")})
    return {"schema_version":1,"feed_type":"reviewed_public_observations","notice":"Published source claims are not founder approvals or current account entitlements.","opportunities":opportunities}

def build_db(events,dest):
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists():dest.unlink()
    with sqlite3.connect(dest) as conn:
        conn.execute("CREATE TABLE events (event_id TEXT PRIMARY KEY,event_type TEXT,subject_id TEXT,recorded_at TEXT,actor TEXT,review_state TEXT,source_url TEXT,facts_json TEXT,source_sha256 TEXT,note TEXT)")
        for e in events:
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?,?,?,?,?,?)",(e["event_id"],e["event_type"],e["subject_id"],e["recorded_at"],e["actor"],e["review_state"],e["source_url"],json.dumps(e["facts"],sort_keys=True),e.get("source_sha256"),e.get("note")))
        conn.execute("CREATE INDEX idx_subject_history ON events(subject_id,recorded_at)")

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="command",required=True)
    sub.add_parser("validate"); sub.add_parser("report")
    b=sub.add_parser("build"); b.add_argument("--db",default=str(ROOT/"build/leverage.sqlite"));b.add_argument("--feed",default=str(ROOT/"docs/feed.json"))
    args=ap.parse_args();events=load_events()
    if args.command=="validate": print(f"OK: {len(events)} events validated")
    if args.command=="report": print(json.dumps({"events":len(events),"feed":public_feed(events)},indent=2))
    if args.command=="build":
        build_db(events,args.db)
        Path(args.feed).parent.mkdir(parents=True,exist_ok=True)
        Path(args.feed).write_text(json.dumps(public_feed(events),indent=2,ensure_ascii=False,sort_keys=True)+"\n",encoding="utf-8")
        print(f"Built {len(events)} events, SQLite and feed")

if __name__=="__main__":
    try:main()
    except (ValueError,OSError,json.JSONDecodeError,sqlite3.Error) as err:
        print(f"ERROR: {err}",file=sys.stderr);sys.exit(1)
