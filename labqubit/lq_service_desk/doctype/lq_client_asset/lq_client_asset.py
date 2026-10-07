# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class LQClientAsset(Document):
	def validate(self):
		if self.serial_number:
			self.serial_number = self.serial_number.strip()
			duplicate = frappe.db.exists(
				"LQ Client Asset",
				{"client": self.client, "serial_number": self.serial_number, "name": ["!=", self.name]},
			)
			if duplicate:
				frappe.throw(
					_("Serial number {0} is already registered as {1}.").format(self.serial_number, duplicate)
				)

		if (
			self.installed_on
			and self.warranty_expiry
			and getdate(self.warranty_expiry) < getdate(self.installed_on)
		):
			frappe.throw(_("Warranty expiry cannot be before the installation date."))
