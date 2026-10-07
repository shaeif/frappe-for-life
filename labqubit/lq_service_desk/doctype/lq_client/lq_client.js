// Copyright (c) 2026, LabQubit and contributors
// For license information, please see license.txt

frappe.ui.form.on("LQ Client", {
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("Create Portal User"), () => {
			const dialog = new frappe.ui.Dialog({
				title: __("Give portal access"),
				fields: [
					{ fieldname: "email", fieldtype: "Data", options: "Email", label: __("Email"), reqd: 1 },
					{ fieldname: "first_name", fieldtype: "Data", label: __("First Name"), reqd: 1 },
					{ fieldname: "last_name", fieldtype: "Data", label: __("Last Name") },
					{ fieldname: "primary", fieldtype: "Check", label: __("Primary contact (receives renewal reminders)") },
				],
				primary_action_label: __("Create and send invite"),
				primary_action(values) {
					frappe
						.call({
							method: "labqubit.api.portal_admin.create_portal_user",
							args: { client: frm.doc.name, ...values },
							freeze: true,
						})
						.then((r) => {
							dialog.hide();
							frappe.show_alert({ message: __("Portal access granted to {0}", [r.message]), indicator: "green" });
							frm.reload_doc();
						});
				},
			});
			dialog.show();
		});
		frm.add_custom_button(__("Tickets"), () => frappe.set_route("List", "LQ Support Ticket", { client: frm.doc.name }), __("View"));
		frm.add_custom_button(__("Contracts"), () => frappe.set_route("List", "LQ AMC Contract", { client: frm.doc.name }), __("View"));
		frm.add_custom_button(__("Assets"), () => frappe.set_route("List", "LQ Client Asset", { client: frm.doc.name }), __("View"));
	},
});
