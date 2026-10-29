import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / "scripts"))
from compile_daily import load_runs, make_feed

def record(value, status="NEW", verification="source_checked"):
    return {
        "id":"test-opportunity",
        "title":"Synthetic test program",
        "status":status,
        "source_url":"https://example.org/",
        "checked_at":"2026-10-28T12:00:00Z",
        "claim":f"Published value: {value}",
        "why_now":"Testing a material change",
        "verification":verification,
        "evidence_level":"first_party",
        "confidence":"high",
        "value_type":"credit"
    }

class DailyTests(unittest.TestCase):
    def save(self, folder, day, observations):
        Path(folder,day+".json").write_text(json.dumps({"schema_version":1,"date":day,"observations":observations}))
    def test_latest_and_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.save(tmp,"2026-10-27",[record(100)])
            self.save(tmp,"2026-10-28",[record(200,"CHANGED")])
            feed=make_feed(load_runs(tmp))
            self.assertEqual(feed["stats"]["tracked_opportunities"],1)
            self.assertEqual(feed["stats"]["changed_observations"],1)
            self.assertEqual(feed["opportunities"][0]["observations_count"],2)
    def test_unreviewed_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.save(tmp,"2026-10-28",[record(100,verification="needs_review")])
            feed=make_feed(load_runs(tmp))
            self.assertEqual(feed["stats"]["tracked_opportunities"],0)
            self.assertEqual(feed["stats"]["unreviewed_observations"],1)
    def test_no_private_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            o=record(100);o["email"]="customer@example.org"
            self.save(tmp,"2026-10-28",[o])
            with self.assertRaises(ValueError):load_runs(tmp)
    def test_reject_non_https(self):
        with tempfile.TemporaryDirectory() as tmp:
            o=record(100);o["source_url"]="http://example.org"
            self.save(tmp,"2026-10-28",[o])
            with self.assertRaises(ValueError):load_runs(tmp)
if __name__=="__main__":unittest.main()
