import frappe
from frappe import _

from labqubit.website.portal import portal_context

no_cache = 1


def get_context(context):
	if not portal_context(context, "documents", _("Documents")):
		return
	context.documents = frappe.get_list(
		"LQ Client Document",
		fields=[
			"name",
			"title",
			"document_type",
			"document_date",
			"reference_no",
			"amount",
			"currency",
			"file",
		],
		order_by="document_date desc, creation desc",
		limit=1000,
	)
	context.types = sorted({d.document_type for d in context.documents})
