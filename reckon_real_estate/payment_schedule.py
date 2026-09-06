"""Adapt operational installments to ERPNext's one-row-per-due-date schedule."""

from datetime import date, datetime


def consolidate_due_dates(schedule):
    """Combine amounts without changing contractual dates or source rows."""
    grouped = {}
    for due_date, amount, description in schedule:
        if isinstance(due_date, datetime):
            due_date = due_date.date()
        elif not isinstance(due_date, date):
            due_date = date.fromisoformat(due_date)
        if due_date not in grouped:
            grouped[due_date] = [0, []]
        grouped[due_date][0] += amount
        if description:
            grouped[due_date][1].append(description)
    return [
        (due_date, amount, "; ".join(descriptions))
        for due_date, (amount, descriptions) in sorted(grouped.items())
    ]
