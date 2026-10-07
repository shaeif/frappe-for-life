import frappe
from frappe import _

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	if not portal_context(context, "assets", _("Assets")):
		return
	context.assets = frappe.get_list(
		"LQ Client Asset",
		fields=[
			"name",
			"asset_name",
			"asset_type",
			"vendor",
			"model",
			"serial_number",
			"site_location",
			"warranty_expiry",
			"status",
			"amc_contract",
		],
		order_by="asset_name asc",
		limit=2000,
	)
	context.types = sorted({a.asset_type for a in context.assets})
	context.today = frappe.utils.getdate()
