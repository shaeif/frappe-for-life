import frappe
from frappe import _

from labqubit.website.context import PARTNER_FIELDS, published

sitemap = 1


def get_context(context):
	settings = frappe.get_cached_doc("LQ Settings")
	context.title = _("About")
	context.description = _(
		"LabQubit is an IT solutions provider specializing in networks, cybersecurity, data centers, managed services and web development."
	)
	context.partners = published("LQ Partner", fields=PARTNER_FIELDS, order_by="display_order asc")
	context.certifications = published(
		"LQ Certification", fields=["title", "issuer", "logo"], order_by="display_order asc"
	)
	context.stats = [
		{"value": settings.stat_projects, "suffix": "+", "label": _("Projects delivered")},
		{"value": settings.stat_clients, "suffix": "+", "label": _("Clients served")},
		{"value": settings.stat_uptime, "suffix": "%", "decimals": 2, "label": _("Network uptime")},
		{"value": settings.stat_years, "suffix": "+", "label": _("Years of experience")},
	]
