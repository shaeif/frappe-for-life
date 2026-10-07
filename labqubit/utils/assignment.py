import frappe
from frappe.utils import get_url_to_form


def has_active_assignment_rule(doctype):
	"""Admins can replace the built-in round robin with a Frappe Assignment Rule."""
	return frappe.db.exists("Assignment Rule", {"document_type": doctype, "disabled": 0})


def least_loaded_user(role, doctype):
	"""Enabled user with `role` who has the fewest open assignments on `doctype`."""
	users = frappe.get_all(
		"Has Role",
		filters={"role": role, "parenttype": "User", "parent": ["not in", ["Administrator", "Guest"]]},
		pluck="parent",
		distinct=True,
	)
	users = frappe.get_all("User", filters={"name": ["in", users or [""]], "enabled": 1}, pluck="name")
	if not users:
		return None
	open_counts = dict(
		frappe.get_all(
			"ToDo",
			filters={"allocated_to": ["in", users], "reference_type": doctype, "status": "Open"},
			fields=["allocated_to", "count(name) as open"],
			group_by="allocated_to",
			as_list=True,
		)
	)
	return min(sorted(users), key=lambda u: open_counts.get(u, 0))


def assign(doc, user, description):
	"""Create an open ToDo (shows in the assignee's list and notifications, updates _assign)."""
	if not user or frappe.db.exists(
		"ToDo",
		{"reference_type": doc.doctype, "reference_name": doc.name, "allocated_to": user, "status": "Open"},
	):
		return
	frappe.get_doc(
		{
			"doctype": "ToDo",
			"allocated_to": user,
			"reference_type": doc.doctype,
			"reference_name": doc.name,
			"description": description,
			"assigned_by": "Administrator",
			"priority": "High" if doc.get("priority") in ("High", "Critical") else "Medium",
		}
	).insert(ignore_permissions=True)


def auto_assign(doc, role, description):
	if has_active_assignment_rule(doc.doctype):
		return None
	user = least_loaded_user(role, doc.doctype)
	assign(doc, user, description)
	return user


def form_url(doc):
	return get_url_to_form(doc.doctype, doc.name)
