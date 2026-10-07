import frappe
from frappe import _

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	client = portal_context(context, "dashboard", _("Client portal"))
	if not client:
		return
	open_statuses = ["Open", "In Progress", "Waiting on Client"]
	context.counts = {
		"tickets": frappe.db.count("LQ Support Ticket", {"client": client, "status": ["in", open_statuses]}),
		"contracts": frappe.db.count(
			"LQ AMC Contract", {"client": client, "status": ["in", ["Active", "Expiring Soon"]]}
		),
		"assets": frappe.db.count("LQ Client Asset", {"client": client, "status": ["!=", "Retired"]}),
		"documents": frappe.db.count("LQ Client Document", {"client": client, "visible_to_client": 1}),
	}
	context.expiring = frappe.get_list(
		"LQ AMC Contract",
		filters={"status": "Expiring Soon"},
		fields=["name", "contract_title", "end_date"],
		order_by="end_date asc",
	)
	context.recent_tickets = frappe.get_list(
		"LQ Support Ticket",
		fields=["name", "subject", "status", "priority", "modified", "sla_status"],
		order_by="modified desc",
		limit=5,
	)
	context.recent_documents = frappe.get_list(
		"LQ Client Document",
		fields=["name", "title", "document_type", "document_date", "file"],
		order_by="document_date desc",
		limit=4,
	)
