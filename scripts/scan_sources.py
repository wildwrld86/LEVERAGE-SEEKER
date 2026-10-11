#!/usr/bin/env python3
"""Scan curated first-party websites. Changes create UNVERIFIED fingerprints."""
from datetime import datetime,timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parents[1]

class Content(HTMLParser):
    def __init__(self):super().__init__();self.skip=0;self.tokens=[];self.title=[];self.in_title=False
    def handle_starttag(self,tag,attrs):
        if tag in ("script","style","svg","noscript"):self.skip+=1
        if tag=="title":self.in_title=True
    def handle_endtag(self,tag):
        if tag in ("script","style","svg","noscript"):self.skip=max(0,self.skip-1)
        if tag=="title":self.in_title=False
    def handle_data(self,data):
        if self.in_title:self.title.append(data)
        if not self.skip:self.tokens.append(data)

def fingerprint(url):
    if urlparse(url).scheme!="https":raise ValueError("Only HTTPS sources")
    req=Request(url,headers={"Accept":"text/html","User-Agent":"LEVERAGE-SEEKER-evidence-monitor/0.1 (https://github.com/wildwrld86/LEVERAGE-SEEKER)"})
    with urlopen(req,timeout=18) as res:
        if "html" not in res.headers.get("content-type","").lower():raise ValueError("Not HTML")
        doc=res.read(1024*1024+1)
        if len(doc)>1024*1024:raise ValueError("HTML exceeds 1 MB")
    parser=Content();parser.feed(doc.decode("utf-8",errors="replace"))
    visible=re.sub(r"\s+"," "," ".join(parser.tokens)).strip()
    if len(visible)<120:raise ValueError("Too little visible text")
    return sha256(visible.encode()).hexdigest()," ".join(parser.title)[:140].strip()

def run():
    now=datetime.now(timezone.utc)
    state_path=ROOT/"data/monitor/seen.json";state=json.loads(state_path.read_text())
    sources=json.loads((ROOT/"data/sources.json").read_text())
    created=[];errors=[]
    for source in sources:
        sid=source["source_id"];url=source["url"]
        if not re.fullmatch(r"[a-z0-9][a-z0-9-]+",sid):raise ValueError("Bad source id")
        try:hash_value,title=fingerprint(url)
        except Exception as err:
            errors.append(f"{sid}: {type(err).__name__}: {err}");continue
        if state.get(sid)==hash_value:continue
        record={"candidate_type":"unverified_source_fingerprint","source_id":sid,"subject_id":source["subject_id"],"source_url":url,"observed_at":now.isoformat(timespec="seconds").replace("+00:00","Z"),"previous_sha256":state.get(sid),"source_sha256":hash_value,"page_title":title,"review_state":"NEEDS_REVIEW","notice":"Hash change does not prove material change; manual source verification required."}
        path=ROOT/"data/candidates"/now.strftime("%Y-%m-%d")/(sid+"-"+hash_value[:16]+".json")
        path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(record,indent=2,sort_keys=True)+"\n")
        created.append(str(path.relative_to(ROOT)));state[sid]=hash_value
    if created:state_path.write_text(json.dumps(state,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"candidate_files":created,"errors":errors},indent=2))
    return 1 if sources and len(errors)==len(sources) else 0

if __name__=="__main__":
    try:sys.exit(run())
    except (ValueError,OSError,json.JSONDecodeError) as e:print(str(e),file=sys.stderr);sys.exit(1)
