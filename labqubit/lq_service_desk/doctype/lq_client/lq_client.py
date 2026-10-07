# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

CLIENT_ROLE = "LQ Client"


class LQClient(Document):
	def validate(self):
		self.validate_portal_users()

	def on_update(self):
		for row in self.portal_users:
			ensure_client_role(row.user)

	def validate_portal_users(self):
		seen = set()
		for row in self.portal_users:
			if row.user in seen:
				frappe.throw(_("Row {0}: {1} is listed twice.").format(row.idx, row.user))
			seen.add(row.user)

			# One portal user belongs to exactly one client: keeps data isolation simple and safe
			other_client = frappe.db.get_value(
				"LQ Client User",
				{"user": row.user, "parenttype": "LQ Client", "parent": ["!=", self.name]},
				"parent",
			)
			if other_client:
				frappe.throw(
					_(
						"{0} already has portal access for {1}. A portal user can belong to one client only."
					).format(row.user, other_client)
				)


def ensure_client_role(user):
	if CLIENT_ROLE not in frappe.get_roles(user):
		frappe.get_doc("User", user).add_roles(CLIENT_ROLE)
