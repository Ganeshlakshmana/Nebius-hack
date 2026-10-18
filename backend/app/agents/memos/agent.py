from __future__ import annotations

import html
from datetime import datetime, timezone
from app.services.data_tools import DataTools


class MemoAgent:
    def __init__(self, tools: DataTools):
        self.tools = tools

    def build_html(self, ids: list[str], chosen: str | None = None, note: str = "") -> str:
        rows = self.tools.get_suppliers(ids)
        table_rows = "".join(f"<tr><td>{html.escape(str(r['supplierID']))}</td><td>{html.escape(str(r['Supplier Name']))}</td>"
            f"<td>{float(r['Total_Risk_Index']):.1f}</td><td>{html.escape(str(r['Sourcing Risk Level']))}</td>"
            f"<td>{float(r['Purchase Order Volume (EUR)']):,.2f}</td></tr>" for r in rows)
        return f"""<!doctype html><html><head><meta charset='utf-8'><title>Supplier shortlist memo</title>
<style>body{{font:15px Arial,sans-serif;margin:40px;color:#172033}}h1{{color:#123b5d}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #cbd5e1;padding:9px;text-align:left}}th{{background:#e8f1f7}}</style></head>
<body><h1>Supplier shortlist decision memo</h1><p>Generated {datetime.now(timezone.utc).isoformat()}</p>
<p><b>Selected supplier:</b> {html.escape(chosen or 'Not specified')}</p><p>{html.escape(note)}</p>
<p>Historic TRI and PO values below are from the immutable source dataset. Operations feed data is simulated and is not included in official TRI.</p>
<table><thead><tr><th>ID</th><th>Supplier</th><th>Total Risk Index</th><th>Sourcing risk</th><th>PO volume (EUR)</th></tr></thead><tbody>{table_rows}</tbody></table>
<p>Methodology: TRI values are reproduced from the source dataset. All operational signals, if added, must be labelled as simulated feed.</p></body></html>"""
