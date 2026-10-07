import frappe
from frappe import _

no_cache = 1


def get_context(context):
	context.title = _("Set password")
	context.noindex = True
	context.nav_solid = True
	context.key = frappe.form_dict.get("key") or ""
	context.signed_in = frappe.session.user != "Guest"
