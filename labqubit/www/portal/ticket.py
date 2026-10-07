import frappe
from frappe import _

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	client = portal_context(context, "tickets", _("Ticket"))
	if not client:
		return
	name = frappe.form_dict.name
	tickets = frappe.get_list("LQ Support Ticket", filters={"name": name}, pluck="name")
	if not tickets:
		raise frappe.PageDoesNotExistError
	ticket = frappe.get_doc("LQ Support Ticket", tickets[0])
	ticket.check_permission("read")
	context.ticket = ticket
	context.title = f"{ticket.name} · {ticket.subject}"
	context.asset = (
		frappe.db.get_value("LQ Client Asset", ticket.asset, ["asset_name", "serial_number"], as_dict=True)
		if ticket.asset
		else None
	)
	context.attachments = frappe.get_all(
		"File",
		filters={"attached_to_doctype": ticket.doctype, "attached_to_name": ticket.name},
		fields=["file_name", "file_url", "file_size", "creation"],
		order_by="creation asc",
	)
