"""Shared context for /portal pages. Every portal page is personal: never cached."""

from urllib.parse import quote

import frappe
from frappe import _

from labqubit.permissions import get_portal_client, is_portal_user

STATUS_BADGE = {
	# tickets
	"Open": "brand",
	"In Progress": "warning",
	"Waiting on Client": "warning",
	"Resolved": "success",
	"Closed": "",
	# SLA
	"On Track": "success",
	"At Risk": "warning",
	"Breached": "danger",
	"Met": "success",
	# contracts
	"Active": "success",
	"Expiring Soon": "warning",
	"Expired": "danger",
	"Draft": "",
	"Renewed": "brand",
	"Cancelled": "",
	# assets
	"In Repair": "warning",
	"Retired": "",
	# priority
	"Low": "",
	"Medium": "brand",
	"High": "warning",
	"Critical": "danger",
}


def portal_context(context, active, title):
	"""Require a signed-in portal user; returns their client name (or None for staff/unlinked)."""
	context.no_cache = 1
	context.noindex = True
	context.nav_solid = True
	context.active = active
	context.title = title
	context.badge = STATUS_BADGE

	if frappe.session.user == "Guest":
		path = frappe.local.request.path if frappe.local.request else "/portal"
		frappe.local.flags.redirect_location = "/login?redirect-to=" + quote(path)
		raise frappe.Redirect

	client = get_portal_client() if is_portal_user() else None
	context.portal_client = client
	context.is_staff = frappe.get_cached_value("User", frappe.session.user, "user_type") == "System User"
	if client:
		context.client = frappe.get_list(
			"LQ Client", filters={"name": client}, fields=["name", "client_name", "account_manager"], limit=1
		)[0]
		context.account_manager = (
			frappe.db.get_value("User", context.client.account_manager, ["full_name", "email"], as_dict=True)
			if context.client.account_manager
			else None
		)
	return client
