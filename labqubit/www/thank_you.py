import frappe
from frappe import _

no_cache = 1

MESSAGES = {
	"contact": ("Thank you for reaching out", "Our team will reply within one business day."),
	"quote": ("Your quote request is in", "An engineer will review your requirements and send a proposal."),
	"consultation": ("Consultation requested", "We will confirm your consultation time by email."),
	"application": (
		"Application received",
		"Our team will review your application and contact you if there is a fit.",
	),
}


def get_context(context):
	heading, text = MESSAGES.get(frappe.form_dict.type, MESSAGES["contact"])
	context.heading = _(heading)
	context.text = _(text)
	context.title = _("Thank you")
	context.noindex = True
