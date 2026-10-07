# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from labqubit.utils.files import make_attachments_private


class LQJobApplication(Document):
	def on_update(self):
		make_attachments_private(self, "resume")
