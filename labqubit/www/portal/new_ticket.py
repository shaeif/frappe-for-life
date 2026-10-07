import frappe
from frappe import _

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	if not portal_context(context, "tickets", _("New ticket")):
		return
	context.assets = [
		(a.name, f"{a.asset_name}" + (f" · {a.serial_number}" if a.serial_number else ""))
		for a in frappe.get_list(
			"LQ Client Asset",
			filters={"status": ["!=", "Retired"]},
			fields=["name", "asset_name", "serial_number"],
			order_by="asset_name asc",
		)
	]
	context.preselect_asset = frappe.form_dict.asset
