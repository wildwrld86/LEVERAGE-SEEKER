import json
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from ledger import load_events,public_feed,build_db
class LedgerTests(unittest.TestCase):
    def make(self,name,date,value,review="verified_public"):
        return {"schema_version":1,"event_id":name,"event_type":"observation","subject_id":"synthetic-program","recorded_at":date+"T10:00:00Z","actor":"test","review_state":review,"source_url":"https://example.org/program","facts":{"nominal_value":value}}
    def save(self,root,event):
        path=Path(root)/event["recorded_at"][:10]/(event["event_id"]+".json");path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(event))
    def test_changed_and_unverified_exclusion(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/"events"
            self.save(root,self.make("synthetic-0001","2026-10-01",100))
            self.save(root,self.make("synthetic-0002","2026-10-02",200))
            self.save(root,self.make("synthetic-0003","2026-10-03",300,"needs_review"))
            events=load_events(root);feed=public_feed(events)
            self.assertEqual(feed["opportunities"][0]["state"],"CHANGED")
            self.assertEqual(feed["opportunities"][0]["facts"]["nominal_value"],200)
            db=Path(temp)/"build.sqlite";build_db(events,db)
            with sqlite3.connect(db) as con:self.assertEqual(con.execute("SELECT COUNT(*) FROM events").fetchone()[0],3)
    def test_reject_mismatched_filename(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"2026-10-01"/"bad.json";path.parent.mkdir(parents=True)
            path.write_text(json.dumps(self.make("synthetic-0001","2026-10-01",100)))
            with self.assertRaises(ValueError):load_events(temp)
if __name__=="__main__":unittest.main()
