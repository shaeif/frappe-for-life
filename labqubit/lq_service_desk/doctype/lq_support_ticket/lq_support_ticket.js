// Copyright (c) 2026, LabQubit and contributors
// For license information, please see license.txt

frappe.ui.form.on("LQ Support Ticket", {
	setup(frm) {
		const by_client = () => ({ filters: { client: frm.doc.client } });
		["asset", "amc_contract", "ticket"].forEach((field) => {
			if (frm.fields_dict[field]) frm.set_query(field, by_client);
		});
	},
});
