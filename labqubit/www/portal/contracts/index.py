import frappe
from frappe import _

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	if not portal_context(context, "contracts", _("AMC contracts")):
		return
	context.contracts = frappe.get_list(
		"LQ AMC Contract",
		filters={"status": ["!=", "Draft"]},
		fields=["name", "contract_title", "coverage_level", "start_date", "end_date", "status"],
		order_by="end_date desc",
	)
