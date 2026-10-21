import io
import json
from pathlib import Path
import sys
import unittest
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import scan_sources
from scan_sources import DEFAULT_MAX_BYTES,HARD_MAX_BYTES,fingerprint,max_bytes_for

class FakeResponse(io.BytesIO):
    def __init__(self,body,ctype="text/html; charset=utf-8"):
        super().__init__(body);self.headers={"content-type":ctype}
    def __enter__(self):return self
    def __exit__(self,*a):self.close()

def page(text,pad=0):
    return ("<html><head><title>T</title><script>"+"x"*pad+"</script></head><body><p>"+text+"</p></body></html>").encode()

BODY="Program terms: free to join, credits subject to eligibility and expiry. "*3

class ScanSourceTests(unittest.TestCase):
    def test_default_limit_rejects_oversize_html(self):
        with mock.patch.object(scan_sources,"urlopen",return_value=FakeResponse(page(BODY,DEFAULT_MAX_BYTES))):
            with self.assertRaises(ValueError):fingerprint("https://example.org/p")
    def test_override_accepts_large_html_and_hashes_visible_text_only(self):
        with mock.patch.object(scan_sources,"urlopen",return_value=FakeResponse(page(BODY,DEFAULT_MAX_BYTES))):
            big,_=fingerprint("https://example.org/p",2*DEFAULT_MAX_BYTES)
        with mock.patch.object(scan_sources,"urlopen",return_value=FakeResponse(page(BODY,10))):
            small,_=fingerprint("https://example.org/p")
        self.assertEqual(big,small)
    def test_max_bytes_bounds(self):
        self.assertEqual(max_bytes_for({"source_id":"a"}),DEFAULT_MAX_BYTES)
        self.assertEqual(max_bytes_for({"source_id":"a","max_bytes":3*1024*1024}),3*1024*1024)
        for bad in (HARD_MAX_BYTES+1,DEFAULT_MAX_BYTES-1,"3000000",True,2.5e6):
            with self.assertRaises(ValueError):max_bytes_for({"source_id":"a","max_bytes":bad})
    def test_repo_watchlist_is_valid(self):
        root=Path(__file__).resolve().parents[1]
        sources=json.loads((root/"data/sources.json").read_text())
        seen=json.loads((root/"data/monitor/seen.json").read_text())
        ids=[s["source_id"] for s in sources]
        self.assertEqual(len(ids),len(set(ids)))
        for s in sources:
            self.assertTrue(s["url"].startswith("https://"))
            max_bytes_for(s)
        self.assertTrue(set(seen)<=set(ids))
if __name__=="__main__":unittest.main()
