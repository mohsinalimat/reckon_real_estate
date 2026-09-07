"""Editable sample wording and master-data mapping for new sales agreements.

Bangladesh context reference: Real Estate Development and Management Act, 2010,
https://bdlaws.minlaw.gov.bd/act-1055.html . These are sample commercial terms,
not a certification of title, approvals or legal compliance.
"""

from html import escape

import frappe


SAMPLE_TERMS = {
    "payment_instructions": "Payments shall follow the agreed price and attached installment schedule, through the Seller's designated banking channel, quoting the booking or agreement number. Obtain an official receipt for every payment. Booking money stated in this agreement is not evidence of receipt. Record included and excluded taxes, registration costs, utility deposits and other charges in the signed commercial schedule; no unspecified charge is agreed by this sample wording.",
    "payment_default_terms": "If a payment is missed, the Seller shall notify the Buyer in writing and seek resolution. Any late charge, cure period or cancellation process must comply with applicable Bangladesh law and the signed agreement. This sample does not set a penalty rate or waive either party's statutory rights.",
    "cancellation_refund_terms": "A cancellation request shall be made in writing. The parties shall reconcile receipts, lawful deductions and the refundable balance, and document the applicable refund deadline and payment method. Mandatory rights and deadlines under Bangladesh law prevail over inconsistent terms.",
    "handover_conditions": "Arrange a joint inspection and record any defects, meter readings, keys and documents in the Handover record. Confirm financial clearance and customer acceptance. Confirm the delivery date and the Seller's obligations for delay in the executed agreement; a project forecast alone is not proof of an agreed delivery date.",
    "utility_maintenance_terms": "Record the agreed electricity, water, sewerage and other utility arrangements, connection charges and deposits in the commercial schedule. Do not assume a gas connection is included. State the maintenance start date, rate, billing frequency and common-area management arrangements in writing.",
    "defect_liability_terms": "The Buyer shall report defects in writing with reasonable access for inspection and rectification. Record the applicable coverage, response arrangements and warranty periods in the handover documents. Nothing in this sample limits mandatory developer obligations under Bangladesh law.",
    "registration_document_terms": "Verify the title chain, land schedule, Mouza, Khatian, Dag, developer authority and applicable project approvals before execution. Complete the transfer deed and registration through the applicable Bangladesh process. Record the allocation of stamp duty, registration fees, taxes and related costs in the signed schedule, subject to law.",
    "dispute_resolution_terms": "Serve written notices at the party addresses recorded in this agreement and retain evidence of delivery. Seek an amicable settlement first, then use the dispute-resolution process applicable under Bangladesh law. Do not treat this sample as a waiver of statutory remedies.",
    "annexure_documents": "Attach the agreed Property Booking, installment schedule, unit and floor plan, specifications and inclusions, land-share schedule, relevant title and approval references, and any signed special commercial terms. List the actual annexures and their dates before signing; this list does not certify that documents have been supplied.",
    "terms": "This agreement concerns the identified unit and only the rights and facilities expressly included in the signed documents. Use the property consistently with its approved purpose and applicable building and management rules. Record variations in writing with both parties' agreement. Mandatory Bangladesh law prevails. Review and complete this sample for the specific project before execution.",
    "registration_cost_borne_by": "As Agreed in Special Terms",
}


def read_source(doctype, name):
    doc = frappe.get_doc(doctype, name)
    doc.check_permission("read")
    return doc


def linked_record(doctype, party_type, party_name, preferred=None):
    """Use a selected party record or a deterministically chosen linked record."""
    links = frappe.get_all("Dynamic Link", filters={
        "parenttype": doctype, "link_doctype": party_type, "link_name": party_name,
    }, pluck="parent")
    if preferred and preferred in links:
        return read_source(doctype, preferred)
    if not links:
        return None
    primary = "is_primary_address" if doctype == "Address" else "is_primary_contact"
    names = frappe.get_list(doctype, filters={"name": ["in", links]},
                           order_by=f"{primary} desc, modified desc, name asc", pluck="name", limit_page_length=1)
    return read_source(doctype, names[0]) if names else None


def address_text(doc):
    return ", ".join(str(doc.get(key)) for key in
                     ("address_line1", "address_line2", "city", "state", "pincode", "country")
                     if doc and doc.get(key))


def property_summary(project, unit, building=None, floor=None, item=None, parcel=None):
    rows = [
        ("Project", project.get("project_name") or project.name),
        ("Project Address", project.get("address") or project.get("location")),
        ("Building", building.get("building_name") if building else unit.get("building")),
        ("Floor", floor.get("floor_name") if floor else unit.get("floor")),
        ("Flat / Unit", unit.get("unit_no") or unit.name),
        ("Type", unit.get("unit_type")), ("Category", unit.get("unit_category")),
        ("Area in Sq Ft", unit.get("area_sqft")), ("Facing", unit.get("facing")),
        ("Bedrooms", unit.get("bedrooms")), ("Bathrooms", unit.get("bathrooms")),
        ("Product", item.get("item_name") if item else unit.get("erpnext_item")),
        ("Land Parcel", unit.get("land_parcel")),
        ("Proportionate Land Area", unit.get("proportionate_land_area") or None),
        ("Land Area Unit", parcel.get("area_uom") if parcel else None),
        ("Land Share Percent", unit.get("land_share_percent") or None),
        ("Mouza", parcel.get("mouza") if parcel else None),
        ("Khatian", parcel.get("khatian_no") if parcel else None),
        ("Dag", parcel.get("dag_no") if parcel else None),
    ]
    return "<table><tbody>" + "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>"
        for label, value in rows if value is not None and value != ""
    ) + "</tbody></table>"


def defaults_for_booking(booking_name):
    booking = read_source("Property Booking", booking_name)
    project = read_source("Real Estate Project", booking.project)
    unit = read_source("Real Estate Unit", booking.unit)
    company = read_source("Company", project.company)
    customer = read_source("Customer", booking.customer)
    buyer_address = linked_record("Address", "Customer", customer.name, customer.get("customer_primary_address"))
    seller_address = linked_record("Address", "Company", company.name)
    contact = linked_record("Contact", "Customer", customer.name, customer.get("customer_primary_contact"))
    building = read_source("Real Estate Building", unit.building) if unit.get("building") else None
    floor = read_source("Real Estate Floor", unit.floor) if unit.get("floor") else None
    item = read_source("Item", unit.erpnext_item) if unit.get("erpnext_item") else None
    parcel = read_source("Land Parcel", unit.land_parcel) if unit.get("land_parcel") else None
    values = dict(SAMPLE_TERMS)
    values.update({
        "customer": booking.customer, "project": booking.project, "unit": booking.unit,
        "company": project.company, "contract_value": booking.contract_value,
        "discount": booking.discount, "net_contract_value": booking.net_contract_value,
        "booking_money": booking.booking_money,
        "buyer_name": customer.get("customer_name") or customer.name,
        "seller_legal_name": company.get("company_name") or company.name,
        "seller_address": address_text(seller_address), "buyer_address": address_text(buyer_address),
        "buyer_phone": customer.get("mobile_no") or (contact.get("mobile_no") or contact.get("phone") if contact else None),
        "buyer_email": customer.get("email_id") or (contact.get("email_id") if contact else None),
        # Site-specific identity fields are used only when present. Tax ID is not an NID.
        "buyer_nid_passport": customer.get("custom_nid_passport") or customer.get("custom_national_id") or customer.get("national_id") or customer.get("passport_number"),
        "authorized_signatory": company.get("custom_authorized_signatory") or company.get("authorized_signatory"),
        "possession_date": project.get("expected_completion_date"),
        "included_facilities": unit.get("description") or (item.get("description") if item else None),
        "parking_details": unit.get("parking_details"),
        "property_description": property_summary(project, unit, building, floor, item, parcel),
    })
    return values


def fill_empty_fields(doc, values):
    """Never replace negotiated wording or an already captured master-data value."""
    for field, value in values.items():
        if not doc.get(field) and value is not None:
            doc.set(field, value)


@frappe.whitelist()
def get_agreement_defaults(booking=None):
    if not frappe.has_permission("Sales Agreement", "create"):
        frappe.throw("Not permitted to prepare Sales Agreements.", frappe.PermissionError)
    return defaults_for_booking(booking) if booking else dict(SAMPLE_TERMS)
