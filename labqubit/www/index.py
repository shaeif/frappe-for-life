import frappe
from frappe import _

from labqubit.utils.jinja import t
from labqubit.website.context import CARD_FIELDS, PARTNER_FIELDS, case_study_cards, published

sitemap = 1


def get_context(context):
	settings = frappe.get_cached_doc("LQ Settings")
	context.title = settings.company_name or "LabQubit"
	context.description = t(settings, "default_meta_description") or t(settings, "hero_subtitle")

	context.home_hero = {
		"eyebrow": t(settings, "hero_eyebrow") or _("Networks · Security · Cloud · Web"),
		"title": t(settings, "hero_title") or _("Resilient solutions for resilient businesses"),
		"subtitle": t(settings, "hero_subtitle")
		or _(
			"LabQubit designs, builds and runs networks, security, cloud infrastructure and web applications for "
			"enterprises, government, oil & gas and hospitality, backed by experienced, qualified engineers and "
			"measurable SLAs."
		),
	}

	context.description = context.description or context.home_hero["subtitle"]

	services = published("LQ Service", filters={"featured": 1}, limit=9) or published("LQ Service", limit=9)
	context.services = services
	context.solutions = published(
		"LQ Solution", filters={"featured": 1}, fields=[*CARD_FIELDS, "tagline", "tagline_ar"], limit=3
	) or published("LQ Solution", fields=[*CARD_FIELDS, "tagline", "tagline_ar"], limit=3)
	context.industries = published("LQ Industry", limit=4)
	context.case_studies = case_study_cards({"featured": 1}, limit=3) or case_study_cards(limit=3)
	context.partners = published(
		"LQ Partner", fields=PARTNER_FIELDS, order_by="display_order asc, partner_name asc"
	)
	context.testimonials = published(
		"LQ Testimonial",
		fields=["quote", "quote_ar", "author_name", "author_title", "company", "photo"],
		order_by="display_order asc, creation desc",
	)
	context.certifications = published(
		"LQ Certification", fields=["title", "issuer", "logo"], order_by="display_order asc, title asc"
	)
	context.stats = [
		{"value": settings.stat_projects, "suffix": "+", "label": _("Projects delivered")},
		{"value": settings.stat_clients, "suffix": "+", "label": _("Clients served")},
		{"value": settings.stat_uptime, "suffix": "%", "decimals": 2, "label": _("Network uptime")},
		{"value": settings.stat_years, "suffix": "+", "label": _("Years of experience")},
	]
