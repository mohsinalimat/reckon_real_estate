frappe.ui.form.on("Property Booking", {
    setup(frm) {
        frm.set_query("project", () => ({filters: {status: "Active", docstatus: 1}}));
        frm.set_query("unit", () => ({filters: {
            project: frm.doc.project || "",
            status: "Available",
            docstatus: 1,
        }}));
    },
    async project(frm) {
        frm.set_df_property("unit", "read_only", !frm.doc.project || frm.doc.docstatus !== 0);
        if (frm.doc.docstatus !== 0 || !frm.doc.unit) return;
        const project = frm.doc.project;
        const unit = frm.doc.unit;
        if (!project) return frm.set_value("unit", null);
        // Keep a valid unit passed by Unit > Create > Property Booking.
        const {message} = await frappe.db.get_value("Real Estate Unit", unit, ["project", "status", "docstatus"]);
        if (frm.doc.project !== project || frm.doc.unit !== unit) return;
        if (!message || message.project !== project || message.status !== "Available" || message.docstatus !== 1) {
            await frm.set_value("unit", null);
        }
    },
    refresh(frm) {
        frm.set_df_property("unit", "read_only", !frm.doc.project || frm.doc.docstatus !== 0);
        if (frm.doc.docstatus === 1) frm.add_custom_button(__("Sales Agreement"), () => {
            frappe.route_options = {
                booking: frm.doc.name,
            };
            frappe.new_doc("Sales Agreement");
        }, __("Create"));
    },
});
