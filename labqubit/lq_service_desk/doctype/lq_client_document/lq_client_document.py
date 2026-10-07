# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

from labqubit.utils.files import make_attachments_private


class LQClientDocument(Document):
	def validate(self):
		for link_doctype, fieldname in (("LQ AMC Contract", "amc_contract"), ("LQ Support Ticket", "ticket")):
			value = self.get(fieldname)
			if value and frappe.db.get_value(link_doctype, value, "client") != self.client:
				frappe.throw(_("{0} {1} does not belong to {2}.").format(_(link_doctype), value, self.client))

	def on_update(self):
		make_attachments_private(self, "file")
