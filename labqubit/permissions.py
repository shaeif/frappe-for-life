"""Row-level security for client portal users.

A portal user is a Website User with the "LQ Client" role, linked to exactly one LQ Client
through LQ Client.portal_users. For those users every query and every single-document read
on client data is restricted to their own client. Staff (System Users) are unaffected.

Applied through hooks, so it covers the portal pages, the REST API (/api/resource),
reports, and private file downloads (File checks the attached document's permission).
"""

import frappe

CLIENT_ROLE = "LQ Client"

# doctype -> field holding the client
CLIENT_FIELD = {
	"LQ Client": "name",
	"LQ AMC Contract": "client",
	"LQ Client Asset": "client",
	"LQ Support Ticket": "client",
	"LQ Client Document": "client",
}


def is_portal_user(user=None):
	user = user or frappe.session.user
	if user in ("Administrator", "Guest"):
		return False
	return frappe.get_cached_value(
		"User", user, "user_type"
	) == "Website User" and CLIENT_ROLE in frappe.get_roles(user)


def get_portal_client(user=None):
	"""The LQ Client this portal user belongs to, or None."""
	user = user or frappe.session.user
	if user == "Guest":
		return None
	return frappe.db.get_value("LQ Client User", {"user": user, "parenttype": "LQ Client"}, "parent")


def _query_condition(doctype, user):
	if not is_portal_user(user):
		return ""
	client = get_portal_client(user)
	if not client:
		return "1=0"
	condition = f"`tab{doctype}`.`{CLIENT_FIELD[doctype]}` = {frappe.db.escape(client)}"
	if doctype == "LQ Client Document":
		condition += f" and `tab{doctype}`.`visible_to_client` = 1"
	return condition


def _has_permission(doc, ptype, user):
	if not is_portal_user(user):
		return True
	if ptype not in ("read", "print"):
		return False  # portal users change data only through labqubit.api.portal
	client = get_portal_client(user)
	if not client or doc.get(CLIENT_FIELD[doc.doctype]) != client:
		return False
	if doc.doctype == "LQ Client Document" and not doc.get("visible_to_client"):
		return False
	return True


# Frappe calls these with (user) and (doc, ptype, user); one pair per doctype


def client_query(user=None):
	return _query_condition("LQ Client", user or frappe.session.user)


def contract_query(user=None):
	return _query_condition("LQ AMC Contract", user or frappe.session.user)


def asset_query(user=None):
	return _query_condition("LQ Client Asset", user or frappe.session.user)


def ticket_query(user=None):
	return _query_condition("LQ Support Ticket", user or frappe.session.user)


def document_query(user=None):
	return _query_condition("LQ Client Document", user or frappe.session.user)


def has_client_permission(doc, ptype=None, user=None):
	return _has_permission(doc, ptype or "read", user or frappe.session.user)
