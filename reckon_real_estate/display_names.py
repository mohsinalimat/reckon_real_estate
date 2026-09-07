"""Human-readable labels while preserving all document identifiers and links."""

from functools import wraps

import frappe


MASTER_TITLES = {
    "Real Estate Project": "project_name", "Real Estate Building": "building_name",
    "Real Estate Floor": "floor_name", "Real Estate Unit": "unit_no",
    "Contractor": "contractor_name", "Land Owner": "owner_name",
    "Land Parcel": "parcel_name", "Service Request": "subject",
}
TRANSACTION_TITLES = {
    "Property Booking": ("customer", "unit", "project", "booking_date"),
    "Sales Agreement": ("customer", "unit", "project", "agreement_date"),
    "Installment Plan": ("customer", "unit", "project", "plan_start_date"),
    "Collection Entry": ("customer", "unit", "project", "collection_date"),
    "BOQ": ("project", "effective_date"),
    "Project Budget": ("project", "from_date", "to_date"),
    "Contractor Work Order": ("contractor", "project", "start_date"),
    "Measurement Sheet": ("contractor", "project", "measurement_date"),
    "Running Bill": ("contractor", "project", "bill_date"),
    "JV Agreement": ("land_owner", "land_parcel", "project"),
    "JV Allocation": ("land_owner", "unit", "project", "allocation_type"),
    "Handover": ("customer", "unit", "project", "handover_date"),
    "Warranty": ("customer", "unit", "warranty_type"),
    "Maintenance": ("customer", "unit", "project", "start_date"),
    "Snag": ("description", "unit", "project"),
    "Sales Commission": ("sales_person", "customer", "project"),
    "Sales Target": ("sales_person", "project", "company", "from_date"),
}
NATIVE_TITLES = {
    "Customer": "customer_name", "Supplier": "supplier_name", "Item": "item_name",
    "Company": "company_name", "Project": "project_name", "Cost Center": "cost_center_name",
    "Warehouse": "warehouse_name", "Account": "account_name", "Contact": "full_name",
    "User": "full_name", "Sales Person": "sales_person_name",
}


def make_record_title(doc, lookup=None):
    lookup = lookup or frappe.db.get_value
    parts = []
    for fieldname in TRANSACTION_TITLES.get(doc.doctype, ()):
        value = doc.get(fieldname)
        if not value:
            continue
        field = doc.meta.get_field(fieldname)
        if field and field.fieldtype == "Link":
            title_field = MASTER_TITLES.get(field.options) or NATIVE_TITLES.get(field.options)
            if title_field:
                value = lookup(field.options, value, title_field) or value
        value = " ".join(str(value).split())
        if value and value not in parts:
            parts.append(value[:80])
    return " — ".join(parts)[:140] or doc.doctype


def set_record_title(doc, method=None):
    if doc.doctype in TRANSACTION_TITLES:
        doc.record_title = make_record_title(doc)


def refresh_referencing_titles(doc, method=None):
    """Keep labels current when a master name changes; do not resave transactions."""
    title_field = MASTER_TITLES.get(doc.doctype) or NATIVE_TITLES.get(doc.doctype)
    if not title_field:
        return
    previous = doc.get_doc_before_save()
    if previous and previous.get(title_field) == doc.get(title_field):
        return
    for doctype, fields in TRANSACTION_TITLES.items():
        if not frappe.db.exists("DocType", doctype):
            continue
        meta = frappe.get_meta(doctype)
        if not meta.has_field("record_title"):
            continue
        for fieldname in fields:
            field = meta.get_field(fieldname)
            if field and field.fieldtype == "Link" and field.options == doc.doctype:
                for name in frappe.get_all(doctype, filters={fieldname: doc.name}, pluck="name"):
                    target = frappe.get_doc(doctype, name)
                    frappe.db.set_value(doctype, name, "record_title", make_record_title(target), update_modified=False)
        frappe.clear_cache(doctype=doctype)


def setup_display_names():
    """Migration backfill changes display fields only, including submitted records."""
    from frappe.custom.doctype.property_setter.property_setter import make_property_setter

    for doctype, title in NATIVE_TITLES.items():
        meta = frappe.get_meta(doctype)
        if meta.has_field(title):
            # Shared native masters use the same name display wherever linked.
            if not meta.title_field:
                make_property_setter(doctype, None, "title_field", title, "Data")
            if not meta.show_title_field_in_link:
                make_property_setter(doctype, None, "show_title_field_in_link", 1, "Check")
    for doctype in TRANSACTION_TITLES:
        start = 0
        while True:
            names = frappe.get_all(doctype, pluck="name", order_by="name", limit_start=start, limit_page_length=200)
            if not names:
                break
            for name in names:
                doc = frappe.get_doc(doctype, name)
                title = make_record_title(doc)
                if doc.get("record_title") != title:
                    frappe.db.set_value(doctype, name, "record_title", title, update_modified=False)
            start += len(names)
    frappe.clear_cache()


def with_link_names(execute):
    """Add permission-aware name columns to reports, retaining clickable ID columns."""
    @wraps(execute)
    def wrapped(*args, **kwargs):
        result = list(execute(*args, **kwargs))
        columns, rows = result[:2]
        requests = {}
        display_columns = {}
        for column in columns:
            if column.get("fieldtype") not in ("Link", "Dynamic Link"):
                continue
            fieldname = column["fieldname"]
            dynamic = column.get("fieldtype") == "Dynamic Link"
            doctypes = {row.get(column["options"]) for row in rows} if dynamic else {column.get("options")}
            for doctype in doctypes:
                title = MASTER_TITLES.get(doctype) or NATIVE_TITLES.get(doctype)
                if doctype in TRANSACTION_TITLES:
                    title = "record_title"
                if not title:
                    continue
                display_columns[fieldname] = column
                requests.setdefault((doctype, title), set()).update(
                    row.get(fieldname) for row in rows if row.get(fieldname)
                    and (not dynamic or row.get(column["options"]) == doctype)
                )
        titles = {}
        for (doctype, title), names in requests.items():
            # Use get_list, not get_all, so report labels do not reveal restricted masters.
            if not frappe.has_permission(doctype, "read"):
                continue
            names = sorted(names)
            for start in range(0, len(names), 200):
                for row in frappe.get_list(doctype, filters={"name": ["in", names[start:start+200]]},
                                           fields=["name", title], limit_page_length=200):
                    titles[doctype, row.name] = row.get(title)
        output = []
        for column in columns:
            fieldname = column["fieldname"]
            if fieldname in display_columns:
                display_field = fieldname + "_display_name"
                output.append({"label": column["label"] + " Name", "fieldname": display_field,
                               "fieldtype": "Data", "width": 210})
                for row in rows:
                    doctype = row.get(column["options"]) if column["fieldtype"] == "Dynamic Link" else column["options"]
                    row[display_field] = titles.get((doctype, row.get(fieldname))) or row.get(fieldname)
                column = {**column, "label": column["label"] + " ID"}
            output.append(column)
        result[0] = output
        return tuple(result)
    return wrapped
