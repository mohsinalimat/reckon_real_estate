frappe.ui.form.on("Sales Agreement", {
    onload(frm) {
        if (frm.is_new()) return fill_agreement_defaults(frm);
    },
    booking(frm) {
        if (frm.is_new()) return fill_agreement_defaults(frm);
    },
    refresh(frm) {
        frm.set_df_property("booking", "read_only", !frm.is_new());
        if (frm.doc.docstatus === 0 && frm.doc.booking) {
            frm.add_custom_button(__("Fill Missing Agreement Details"), () => fill_agreement_defaults(frm));
        }
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Installment Plan"), () => {
            frappe.route_options = {
                sales_agreement: frm.doc.name,
                booking: frm.doc.booking,
                customer: frm.doc.customer,
                project: frm.doc.project,
                unit: frm.doc.unit,
                down_payment: frm.doc.booking_money,
            };
            frappe.new_doc("Installment Plan");
        }, __("Create"));
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Handover"), () => {
            frappe.route_options = {sales_agreement: frm.doc.name};
            frappe.new_doc("Handover");
        }, __("Create"));
    },
});

async function fill_agreement_defaults(frm) {
    const booking = frm.doc.booking || null;
    const request = (frm._agreement_defaults_request || 0) + 1;
    frm._agreement_defaults_request = request;
    const response = await frappe.call({
        method: "reckon_real_estate.agreement_defaults.get_agreement_defaults",
        args: { booking },
    });
    if (request !== frm._agreement_defaults_request || booking !== (frm.doc.booking || null)) return;
    const previous = frm._agreement_defaults || {};
    const values = response.message || {};
    const updates = {};
    const derived = ["customer", "project", "unit", "company", "contract_value", "discount",
        "net_contract_value", "booking_money", "buyer_name", "property_description"];
    const identity = ["seller_legal_name", "seller_address", "authorized_signatory", "buyer_address",
        "buyer_nid_passport", "buyer_phone", "buyer_email", "possession_date", "included_facilities", "parking_details"];
    const changedBooking = frm._agreement_defaults_booking && frm._agreement_defaults_booking !== booking;
    for (const field of new Set([...Object.keys(previous), ...Object.keys(values)])) {
        if (derived.includes(field) || (changedBooking && identity.includes(field)) || !frm.doc[field] || frm.doc[field] === previous[field]) {
            updates[field] = values[field] ?? null;
        }
    }
    frm._agreement_defaults = values;
    frm._agreement_defaults_booking = booking;
    await frm.set_value(updates);
}
