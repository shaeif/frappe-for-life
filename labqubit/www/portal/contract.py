import frappe
from frappe import _
from frappe.utils import date_diff, getdate, today

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	if not portal_context(context, "contracts", _("Contract")):
		return
	names = frappe.get_list(
		"LQ AMC Contract", filters={"name": frappe.form_dict.name, "status": ["!=", "Draft"]}, pluck="name"
	)
	if not names:
		raise frappe.PageDoesNotExistError
	contract = frappe.get_doc("LQ AMC Contract", names[0])
	contract.check_permission("read")
	context.contract = contract
	context.title = contract.contract_title
	context.days_left = date_diff(contract.end_date, today())
	total = date_diff(contract.end_date, contract.start_date) or 1
	context.progress = max(0, min(100, round(date_diff(today(), contract.start_date) * 100 / total)))
	context.assets = frappe.get_list(
		"LQ Client Asset",
		filters={"name": ["in", [r.asset for r in contract.covered_assets] or [""]]},
		fields=["name", "asset_name", "asset_type", "model", "serial_number", "site_location", "status"],
		order_by="asset_name asc",
	)
	context.targets = (
		frappe.get_cached_doc("LQ SLA Policy", contract.sla_policy).targets if contract.sla_policy else []
	)
	context.ended = getdate(contract.end_date) < getdate(today())
