# Frappe's login logic (redirects for signed-in users, settings); LabQubit template.
import frappe
from frappe import _
from frappe.www.login import get_context as frappe_login_context

no_cache = 1


def get_context(context):
	frappe_login_context(context)
	context.title = _("Sign in")
	context.noindex = True
	context.nav_solid = True
	context.redirect_to = frappe.form_dict.get("redirect-to") or ""
