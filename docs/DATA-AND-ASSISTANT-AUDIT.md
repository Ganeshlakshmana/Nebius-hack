# Data and assistant audit — 18 October 2026

## Verified

The dashboard JSON matches the repository challenge CSV in every cell: 10,000 unique supplier IDs and all 46 columns. Public and data copies of the criteria document are identical. All supplied numeric risk levels agree with the dashboard boundaries (25, 50, 75). Regression coverage: `backend/tests/test_dashboard_data.py`.

Independent portfolio totals:
- Mean Total Risk Index: 50.1528 (displayed 50.2)
- Low: 318; Medium: 4,485; High: 4,813; Critical: 384
- Recorded purchase order value: EUR 20,414,231,780.20

Delivery rating is a percentage according to the criteria document. It is not a risk score. Original TRI values are preserved; its category weights and observation date were not supplied. This audit compares repository artifacts, not a newly downloaded organizer copy.

## Corrected

- Removed fixed High badge and hardcoded 10,000 denominators from portfolio calculations.
- Removed automatic synthetic component assignments from supplied supplier profiles.
- Replaced stale service connection claims with capability descriptions, explicitly not live health checks.
- Supplier ID clarification replies now retrieve records without relying on model planning. A model reply asking again for an explicitly supplied ID on a data request is repaired into a record lookup.
- Conversational replies no longer claim completed tool work. ID-only requests show the actual record lookup.

## Limits

This is a model supervisor with bounded specialist tool/service calls, not independent autonomous agents for each turn. Research can invoke external search; arithmetic and dataset lookups are deterministic. No evidence establishes component qualification or maps anonymous suppliers to real companies. Commercial inputs are synthetic scenarios. The train is a conceptual illustration. No production order feed is connected.

The repeated-clarification case was checked through the running frontend `/api/chat` endpoint. Browser visual inspection was not performed in this audit. These changes do not establish that every possible conversation or external research claim is correct.
