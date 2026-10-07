import frappe
from frappe import _

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	if not portal_context(context, "tickets", _("Support tickets")):
		return
	context.tickets = frappe.get_list(
		"LQ Support Ticket",
		fields=["name", "subject", "status", "priority", "sla_status", "opened_on", "modified", "asset"],
		order_by="modified desc",
		limit=500,
	)
