from datetime import date, datetime
import json
from pathlib import Path

from reckon_real_estate.payment_schedule import consolidate_due_dates


def test_down_payment_and_first_installment_share_date():
    rows = [
        ("2026-09-30", 1500000, "Booking / Down Payment"),
        (date(2026, 9, 30), 850000, "Installment 1"),
        ("2026-10-30", 850000, "Installment 2"),
    ]
    result = consolidate_due_dates(rows)
    assert result == [
        (date(2026, 9, 30), 2350000, "Booking / Down Payment; Installment 1"),
        (date(2026, 10, 30), 850000, "Installment 2"),
    ]
    assert sum(r[1] for r in result) == sum(r[1] for r in rows)
    assert len(rows) == 3  # Operational allocations remain separate.


def test_custom_duplicate_dates_are_sorted_and_missing_descriptions_supported():
    assert consolidate_due_dates([
        ("2026-11-30", 50, None),
        (datetime(2026, 9, 30), 25, "First"),
        ("2026-11-30", 25, "Last"),
    ]) == [
        (date(2026, 9, 30), 25, "First"),
        (date(2026, 11, 30), 75, "Last"),
    ]


def test_distinct_dates_and_empty_schedule():
    rows = [(date(2026, 9, 30), 40, "First"), (date(2026, 10, 30), 60, "Second")]
    assert consolidate_due_dates(rows) == rows
    assert consolidate_due_dates([]) == []


def test_unit_item_is_required():
    path = Path(__file__).resolve().parents[1] / "reckon_real_estate/doctype/real_estate_unit/real_estate_unit.json"
    fields = {f["fieldname"]: f for f in json.loads(path.read_text())["fields"]}
    assert fields["erpnext_item"]["reqd"] == 1
