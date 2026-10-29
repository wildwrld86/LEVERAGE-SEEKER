# Daily delta journal — public, append-only

One file per date: `YYYY-MM-DD.json` (UTC dates recommended). No entries required when nothing consequential changes. Do not copy the same unchanged opportunity into every date.

Use this shape (illustrative **template only**, not a factual opportunity):

```json
{
  "schema_version": 1,
  "date": "YYYY-MM-DD",
  "observations": [
    {
      "id": "stable-provider-program-id",
      "title": "Descriptive program or buyer-problem title",
      "status": "NEW",
      "source_url": "https://example.com/official-page",
      "checked_at": "2026-10-29T12:00:00Z",
      "claim": "Exactly what the source supports",
      "why_now": "Material reason to record this on this date",
      "verification": "needs_review",
      "evidence_level": "first_party",
      "confidence": "low",
      "value_type": "credit",
      "value": "Unknown until official terms reviewed",
      "eligibility": "Unverified",
      "friction": "Unverified",
      "deadline": null,
      "next_check": null,
      "buyer_signal": "none",
      "stackability": [],
      "score": null
    }
  ]
}
```

The example URL, claim and timestamp above are **placeholders**, not research evidence. Remove placeholders before committing actual daily files.

Allowed status: `NEW`, `CHANGED`, `CLOSED`, `BLOCKED`, `REJECTED`, `WATCH`.
Allowed verification: `source_checked`, `needs_review`.
Allowed evidence_level: `first_party`, `firsthand_report`, `secondary`.
Allowed value_type: `cash`, `credit`, `discount`, `cost_saving`, `proposed_revenue`, `none`, `unknown`.
Allowed buyer_signal: `none`, `problem_report`, `reachable_buyer`, `explicit_purchase_intent`, `payment_committed`, `payment_confirmed`. Never use the latter two for public individuals or the founder's private payment data without direct verified and publishable evidence.
Score: nullable integer from 1 (low) to 5 (high). Do not create fake precision.

**Privacy:** Do not publish phone numbers, personal identities, customer records, prospect contact data, API keys, individual grant applications, private financial results or messages. Do not mirror entire pages or copyrighted material.

Validate and rebuild with:

```bash
python scripts/compile_daily.py validate
python scripts/compile_daily.py build
```

A daily automated research job may not have GitHub write permissions. Persistence is **only confirmed by an actual GitHub commit**, not by an automation message or a plan.
