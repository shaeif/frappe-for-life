# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, validate_email_address

CLOSED_STATUSES = ("Won", "Lost")


class LQLead(Document):
	def validate(self):
		self.email = (self.email or "").strip().lower()
		validate_email_address(self.email, throw=True)
		self.set_closed_on()

	def set_closed_on(self):
		if self.status in CLOSED_STATUSES:
			self.closed_on = self.closed_on or today()
		else:
			self.closed_on = None
