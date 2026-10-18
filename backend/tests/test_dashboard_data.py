"""Verify every dashboard cell against the repository's supplied CSV."""
import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def test_dashboard_is_lossless_csv_projection():
    with (ROOT/'data/supplier_risk_dataset.csv').open() as f:
        reader=csv.DictReader(f); columns=reader.fieldnames; rows=list(reader)
    payload=json.loads((ROOT/'public/suppliers.json').read_text())
    assert payload['columns']==columns
    assert len(payload['rows'])==len(rows)==10000
    assert len({r['supplierID'] for r in rows})==len(rows)
    for original,display in zip(rows,payload['rows']):
        for key,value in zip(columns,display):
            if isinstance(value,(float,int)):
                assert Decimal(original[key])==Decimal(str(value)),(original['supplierID'],key)
            else:assert original[key]==value,(original['supplierID'],key)
        for key in columns:
            if key.endswith('_Level') and key[:-6] in original:
                score=float(original[key[:-6]])
                assert 0<=score<=100
                assert original[key]==('Low' if score<25 else 'Medium' if score<50 else 'High' if score<75 else 'Critical')
    assert (ROOT/'data/risk_criteria_description.md').read_bytes()==(ROOT/'public/risk_criteria_description.md').read_bytes()
