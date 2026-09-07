import frappe
from frappe.model.document import Document
from reckon_real_estate.agreement_defaults import defaults_for_booking, fill_empty_fields

from reckon_real_estate.construction_workflow import (
    block_if_submitted,
    require_submitted,
    set_cancelled_status,
    set_draft_status,
    set_submitted_status,
)


class SalesAgreement(Document):
    def validate(self):
        set_draft_status(self, "agreement_no", "document_status")
        previous = self.get_doc_before_save()
        if previous and previous.booking != self.booking:
            frappe.throw("Create a new Sales Agreement to use a different Property Booking.")
        booking = frappe.get_doc("Property Booking", self.booking)
        self.customer, self.project, self.unit = booking.customer, booking.project, booking.unit
        self.company = frappe.db.get_value("Real Estate Project", booking.project, "company")
        self.contract_value, self.discount = booking.contract_value, booking.discount
        self.net_contract_value, self.booking_money = booking.net_contract_value, booking.booking_money
        self.buyer_name = frappe.db.get_value("Customer", self.customer, "customer_name") or self.customer
        if self.is_new():
            defaults = defaults_for_booking(self.booking)
            fill_empty_fields(self, defaults)
            self.property_description = defaults["property_description"]
        duplicate = frappe.db.exists("Sales Agreement", {
            "booking": self.booking, "name": ["!=", self.name], "docstatus": ["!=", 2]
        })
        if duplicate:
            frappe.throw(f"Active Sales Agreement already exists for this Booking: {duplicate}")
        if self.docstatus == 1:
            require_submitted("Property Booking", self.booking)

    def on_submit(self):
        self.db_set("status", "Active")
        set_submitted_status(self, "document_status")

    def on_cancel(self):
        block_if_submitted("Installment Plan", {"sales_agreement": self.name}, "Submitted Installment Plan exists")
        self.db_set("status", "Cancelled")
        set_cancelled_status(self, "document_status")
