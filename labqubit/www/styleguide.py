import frappe
from frappe import _

no_cache = 1


def get_context(context):
	if "System Manager" not in frappe.get_roles():
		raise frappe.PermissionError(_("The style guide is available to System Managers only."))
	context.title = _("Style guide")
	context.noindex = True
	context.sample_feature = {
		"icon": "shield-check",
		"title": "Next-Generation Firewalls",
		"short_description": "Design, migration and hardening with threat prevention.",
	}
	context.sample_case = {
		"title": "Secure SD-WAN for 40 branches",
		"route": "styleguide",
		"summary": "Sample summary text for the case study card.",
		"industry": "Enterprise",
		"client_label": "Retail group",
	}
	context.sample_quotes = [
		{
			"quote": "Sample testimonial text to preview the slider component.",
			"author_name": "Sample Name",
			"author_title": "IT Director",
			"company": "Sample Co.",
		},
		{
			"quote": "Another sample quote, slightly longer, to check how cards align when text wraps over lines.",
			"author_name": "Sample Name",
			"author_title": "CISO",
			"company": "Sample Co.",
		},
		{
			"quote": "A third sample quote.",
			"author_name": "Sample Name",
			"author_title": "Head of IT",
			"company": "Sample Co.",
		},
	]
	context.sample_partners = [
		{"partner_name": n} for n in ("Vendor One", "Vendor Two", "Vendor Three", "Vendor Four")
	]
	context.sample_stats = [
		{"value": 250, "suffix": "+", "label": "Projects delivered"},
		{"value": 99.98, "suffix": "%", "decimals": 2, "label": "Network uptime"},
		{"value": 12, "suffix": "+", "label": "Years of experience"},
	]
