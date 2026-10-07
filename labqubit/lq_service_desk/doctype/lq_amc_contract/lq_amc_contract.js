// Copyright (c) 2026, LabQubit and contributors
// For license information, please see license.txt

frappe.ui.form.on("LQ AMC Contract", {
	refresh(frm) {
		if (!frm.is_new() && !frm.doc.renewed_by && ["Active", "Expiring Soon", "Expired"].includes(frm.doc.status)) {
			frm.add_custom_button(__("Create Renewal"), () => {
				frm.call("create_renewal").then((r) => {
					if (r.message) frappe.set_route("Form", "LQ AMC Contract", r.message);
				});
			});
		}
		if (frm.doc.status === "Draft" && !frm.is_new()) {
			frm.add_custom_button(__("Activate"), () => {
				frm.set_value("status", "Active");
				frm.save();
			});
		}
	},
	client(frm) {
		frm.set_query("asset", "covered_assets", () => ({ filters: { client: frm.doc.client } }));
	},
	onload(frm) {
		frm.set_query("asset", "covered_assets", () => ({ filters: { client: frm.doc.client } }));
	},
});
