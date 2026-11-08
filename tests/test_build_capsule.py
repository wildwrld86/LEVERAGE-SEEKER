"""Public-only offline export safety and portability checks."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_capsule import build_capsule, render_html


class CapsuleTests(unittest.TestCase):
    def put_event(self, root, event_id, date, approved, text):
        record = {
            "schema_version": 1, "event_id": event_id, "event_type": "observation",
            "subject_id": "synthetic-program", "recorded_at": date + "T12:00:00Z",
            "actor": "test", "review_state": "verified_public" if approved else "needs_review",
            "source_url": "https://example.org/", "facts": {"program": text},
        }
        target = Path(root, date, event_id + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(record), encoding="utf-8")

    def put_daily(self, root, checked, text):
        doc = {"schema_version": 1, "date": "2026-10-31", "observations": [{
            "id": "test-delta", "title": text, "status": "WATCH",
            "source_url": "https://example.org/", "checked_at": "2026-10-31T12:00:00Z",
            "claim": "Test claim", "why_now": "Test reason",
            "verification": "source_checked" if checked else "needs_review",
            "evidence_level": "first_party", "confidence": "high"}]}
        Path(root, "2026-10-31.json").write_text(json.dumps(doc), encoding="utf-8")

    def test_offline_static_and_unreviewed_exclusion(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            events, daily = root / "events", root / "daily"
            daily.mkdir()
            self.put_event(events, "public-0001", "2026-10-29", True, 'Public <OK>')
            self.put_event(events, "secret-0002", "2026-10-30", False, "NEVER_EXPORT_UNREVIEWED")
            self.put_daily(daily, False, "NEVER_EXPORT_DAILY")
            output = build_capsule(root / "output.zip", events, daily)
            with ZipFile(output) as archive:
                names = set(archive.namelist())
                self.assertEqual(names, {"index.html", "ledger.json", "intelligence.json", "README.txt", "manifest.sha256"})
                index = archive.read("index.html").decode("utf-8")
                combined = b"".join(archive.read(name) for name in names)
                self.assertNotIn(b"NEVER_EXPORT_UNREVIEWED", combined)
                self.assertNotIn(b"NEVER_EXPORT_DAILY", combined)
                self.assertIn("Public &lt;OK&gt;", index)
                self.assertNotIn("<script", index.lower())
                self.assertNotIn("fetch(", index)
                self.assertNotIn("<link", index.lower())
                self.assertIn("file://", archive.read("README.txt").decode("utf-8"))
                manifest = archive.read("manifest.sha256").decode("ascii")
                for name in names - {"manifest.sha256"}:
                    self.assertIn(hashlib.sha256(archive.read(name)).hexdigest() + "  " + name, manifest)

    def test_escapes_untrusted_record_html(self):
        ledger = {"opportunities": [{"subject_id": "x", "state": "NEW", "recorded_at": "2026-10-31T12:00:00Z",
            "source_url": 'https://example.org/?q="<', "facts": {"program": '<img src=x onerror=alert(1)>'}}]}
        research = {"opportunities": []}
        html = render_html(ledger, research)
        self.assertNotIn("<img", html)
        self.assertIn("&lt;img", html)
        self.assertIn("&quot;&lt;", html)

    def test_rejects_invalid_source_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            events, daily = root / "events", root / "daily"
            daily.mkdir()
            self.put_event(events, "good-0001", "2026-10-29", True, "Public")
            self.put_daily(daily, True, "Test title")
            file = daily / "2026-10-31.json"
            doc = json.loads(file.read_text())
            doc["observations"][0]["email"] = "private@example.org"
            file.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                build_capsule(root / "output.zip", events, daily)
            self.assertFalse((root / "output.zip").exists())


if __name__ == "__main__":
    unittest.main()
