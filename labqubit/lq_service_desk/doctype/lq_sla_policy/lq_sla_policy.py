# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

PRIORITIES = ("Low", "Medium", "High", "Critical")


class LQSLAPolicy(Document):
	def validate(self):
		priorities = [row.priority for row in self.targets]
		missing = [p for p in PRIORITIES if p not in priorities]
		if missing or len(priorities) != len(set(priorities)):
			frappe.throw(_("Add exactly one target for each priority: {0}.").format(", ".join(PRIORITIES)))
		for row in self.targets:
			if row.response_hours <= 0 or row.resolution_hours < row.response_hours:
				frappe.throw(
					_(
						"Row {0}: resolution time must be at least the response time, and both above zero."
					).format(row.idx)
				)

	def on_update(self):
		if self.is_default:
			frappe.db.set_value(
				"LQ SLA Policy", {"name": ["!=", self.name], "is_default": 1}, "is_default", 0
			)

	def get_target(self, priority):
		return next(row for row in self.targets if row.priority == priority)
