"""Data shared by all LabQubit website pages (settings, navigation) and detail-page context.

Navigation and settings are cached in Redis and rebuilt when website content changes
(see `clear_website_cache`, wired to doc_events in hooks.py).
"""

import frappe
from frappe import _
from frappe.utils import get_url, getdate, today

from labqubit.utils.jinja import is_arabic, t

CACHE_KEY = "labqubit:website"

# Service categories, in display order, with their icon
SERVICE_CATEGORIES = {
	"Network Infrastructure": "network",
	"Cybersecurity": "shield-check",
	"Data Center": "server",
	"Structured Cabling": "cable",
	"Managed Services": "headset",
	"Cloud & Consulting": "cloud",
}

CARD_FIELDS = ["name", "title", "title_ar", "route", "icon", "short_description", "short_description_ar"]
PARTNER_FIELDS = ["name", "partner_name", "partnership_level", "logo", "logo_dark", "website"]
CASE_FIELDS = [
	"name",
	"title",
	"title_ar",
	"route",
	"summary",
	"summary_ar",
	"client_label",
	"industry",
	"cover_image",
]

# Fields never sent to templates
PRIVATE_SETTINGS = {"turnstile_secret_key"}


def update_website_context(context):
	"""Hook: runs for every website page render."""
	data = frappe.cache.get_value(CACHE_KEY, generator=_build_shared_data)
	lang = "ar" if is_arabic() else "en"
	path = "/" + (context.get("path") or "").strip("/")
	if path == "/index":
		path = "/"
	url = get_url(path)
	context.lq = frappe._dict(
		settings=frappe._dict(data["settings"]),
		nav=data["nav"],
		lang=lang,
		rtl=lang == "ar",
		year=getdate().year,
		path=path,
		url=url,
		canonical=f"{url}?_lang=ar" if lang == "ar" else url,
		organization_schema=organization_schema(data["settings"]),
	)


def organization_schema(settings):
	schema = {
		"@context": "https://schema.org",
		"@type": "Organization",
		"name": settings.get("company_name") or "LabQubit",
		"url": get_url("/"),
	}
	if settings.get("logo"):
		schema["logo"] = get_url(settings["logo"])
	if settings.get("email"):
		schema["email"] = settings["email"]
	if settings.get("phone"):
		schema["telephone"] = settings["phone"]
	if settings.get("address"):
		schema["address"] = settings["address"]
	same_as = [
		settings.get(k) for k in ("linkedin_url", "x_url", "instagram_url", "youtube_url", "facebook_url")
	]
	if any(same_as):
		schema["sameAs"] = [u for u in same_as if u]
	return schema


def clear_website_cache(doc=None, method=None):
	"""doc_events hook: rebuild navigation and drop rendered pages after content changes."""
	from frappe.website.utils import clear_cache

	frappe.cache.delete_value(CACHE_KEY)
	clear_cache()


def _build_shared_data():
	settings = frappe.get_cached_doc("LQ Settings").as_dict(no_default_fields=True)
	for key in PRIVATE_SETTINGS:
		settings.pop(key, None)

	services = frappe.get_all(
		"LQ Service",
		filters={"published": 1},
		fields=[*CARD_FIELDS, "category", "featured"],
		order_by="display_order asc, title asc",
	)
	groups = []
	for category, category_icon in SERVICE_CATEGORIES.items():
		items = [s for s in services if s.category == category]
		if items:
			groups.append(
				{
					"category": category,
					"icon": category_icon,
					"anchor": frappe.scrub(category).replace("_", "-"),
					"services": items,
				}
			)

	return {
		"settings": settings,
		"nav": {
			"service_groups": groups,
			"solutions": published("LQ Solution", fields=[*CARD_FIELDS, "tagline", "tagline_ar"]),
			"industries": published("LQ Industry"),
		},
	}


def published(doctype, filters=None, fields=None, limit=None, order_by="display_order asc, title asc"):
	return frappe.get_all(
		doctype,
		filters={"published": 1, **(filters or {})},
		fields=fields or CARD_FIELDS,
		order_by=order_by,
		limit=limit,
	)


def published_by_names(doctype, names, fields=None):
	"""Published records for the given names, in the given order."""
	names = [n for n in names if n]
	if not names:
		return []
	rows = {r.name: r for r in published(doctype, filters={"name": ["in", names]}, fields=fields)}
	return [rows[n] for n in names if n in rows]


def case_study_cards(filters=None, limit=None):
	return published(
		"LQ Case Study",
		filters=filters,
		fields=CASE_FIELDS,
		order_by="published_on desc, creation desc",
		limit=limit,
	)


def linked_case_studies(child_doctype, fieldname, value, limit=3):
	"""Published case studies that reference `value` through a multi-select child table."""
	parents = frappe.get_all(
		child_doctype, filters={fieldname: value, "parenttype": "LQ Case Study"}, pluck="parent"
	)
	if not parents:
		return []
	return case_study_cards({"name": ["in", parents]}, limit)


# ---------------------------------------------------------------- detail pages


def build_generator_context(doc, context):
	context.doc = doc
	context.title = t(doc, "meta_title") or t(doc, "title")
	context.page_title = t(doc, "title")
	context.description = t(doc, "meta_description") or t(doc, "short_description") or t(doc, "summary")
	context.og_image = doc.get("meta_image") or doc.get("hero_image") or doc.get("cover_image")
	builder = DETAIL_BUILDERS.get(doc.doctype)
	if builder:
		builder(doc, context)
	context.schema = detail_schema(doc, context)


def _service(doc, context):
	context.section = {"label": _("Services"), "url": "/services"}
	context.partners = published_by_names("LQ Partner", [r.partner for r in doc.partners], PARTNER_FIELDS)
	context.industries = published_by_names("LQ Industry", [r.industry for r in doc.industries])
	context.related = published(
		"LQ Service", filters={"category": doc.category, "name": ["!=", doc.name]}, limit=3
	)
	context.case_studies = linked_case_studies("LQ Service Link", "service", doc.name)


def _solution(doc, context):
	context.section = {"label": _("Solutions"), "url": "/solutions"}
	context.services = published_by_names("LQ Service", [r.service for r in doc.services])
	context.industries = published_by_names("LQ Industry", [r.industry for r in doc.industries])
	context.partners = published_by_names("LQ Partner", [r.partner for r in doc.partners], PARTNER_FIELDS)
	context.case_studies = linked_case_studies("LQ Solution Link", "solution", doc.name)


def _industry(doc, context):
	context.section = {"label": _("Industries"), "url": "/industries"}
	context.services = published_by_names("LQ Service", [r.service for r in doc.services])
	solution_names = frappe.get_all(
		"LQ Industry Link", filters={"industry": doc.name, "parenttype": "LQ Solution"}, pluck="parent"
	)
	context.solutions = published_by_names("LQ Solution", solution_names)
	context.case_studies = case_study_cards({"industry": doc.name}, limit=3)


def _case_study(doc, context):
	context.section = {"label": _("Case Studies"), "url": "/case-studies"}
	context.description = t(doc, "meta_description") or t(doc, "summary")
	context.industry = (
		frappe.db.get_value("LQ Industry", {"name": doc.industry, "published": 1}, CARD_FIELDS, as_dict=True)
		if doc.industry
		else None
	)
	context.services = published_by_names("LQ Service", [r.service for r in doc.services])
	context.solutions = published_by_names("LQ Solution", [r.solution for r in doc.solutions])
	context.testimonial = (
		frappe.db.get_value(
			"LQ Testimonial",
			{"name": doc.testimonial, "published": 1},
			["quote", "quote_ar", "author_name", "author_title", "company", "photo"],
			as_dict=True,
		)
		if doc.testimonial
		else None
	)
	context.more = case_study_cards({"name": ["!=", doc.name]}, limit=2)


def _job_opening(doc, context):
	context.section = {"label": _("Careers"), "url": "/careers"}
	context.description = t(doc, "meta_description") or t(doc, "summary")
	context.is_open = is_job_open(doc)
	context.other_openings = open_jobs(exclude=doc.name, limit=3)


def is_job_open(job):
	return job.status == "Open" and (not job.closes_on or getdate(job.closes_on) >= getdate(today()))


def open_jobs(exclude=None, limit=None):
	filters = {"status": "Open"}
	if exclude:
		filters["name"] = ["!=", exclude]
	jobs = published(
		"LQ Job Opening",
		filters=filters,
		fields=[
			"name",
			"title",
			"title_ar",
			"route",
			"location",
			"employment_type",
			"department",
			"closes_on",
			"status",
			"summary",
			"summary_ar",
		],
		order_by="creation desc",
		limit=limit,
	)
	return [j for j in jobs if is_job_open(j)]


DETAIL_BUILDERS = {
	"LQ Service": _service,
	"LQ Solution": _solution,
	"LQ Industry": _industry,
	"LQ Case Study": _case_study,
	"LQ Job Opening": _job_opening,
}


# ---------------------------------------------------------------- structured data (schema.org)

EMPLOYMENT_TYPES = {
	"Full-time": "FULL_TIME",
	"Part-time": "PART_TIME",
	"Contract": "CONTRACTOR",
	"Internship": "INTERN",
}


def detail_schema(doc, context):
	url = get_url("/" + doc.route)
	company = frappe.get_cached_doc("LQ Settings").company_name or "LabQubit"
	org = {"@type": "Organization", "name": company, "url": get_url("/")}
	image = context.og_image and get_url(context.og_image)
	section = context.get("section") or {}

	crumbs = [{"name": _("Home"), "item": get_url("/")}]
	if section:
		crumbs.append({"name": section["label"], "item": get_url(section["url"])})
	crumbs.append({"name": t(doc, "title"), "item": url})
	schema = [
		{
			"@context": "https://schema.org",
			"@type": "BreadcrumbList",
			"itemListElement": [{"@type": "ListItem", "position": i + 1, **c} for i, c in enumerate(crumbs)],
		}
	]

	main = None
	if doc.doctype in ("LQ Service", "LQ Solution"):
		main = {
			"@type": "Service",
			"name": t(doc, "title"),
			"description": context.description,
			"provider": org,
			"url": url,
			**({"serviceType": doc.category} if doc.get("category") else {}),
		}
	elif doc.doctype == "LQ Case Study":
		context.og_type = "article"
		main = {
			"@type": "Article",
			"headline": t(doc, "title"),
			"description": context.description,
			"datePublished": str(doc.published_on or doc.creation.date()),
			"dateModified": str(doc.modified.date()),
			"author": org,
			"publisher": org,
			"mainEntityOfPage": url,
		}
	elif doc.doctype == "LQ Job Opening" and context.is_open:
		main = {
			"@type": "JobPosting",
			"title": t(doc, "title"),
			"description": (t(doc, "description") or "") + (t(doc, "requirements") or "")
			or context.description,
			"datePosted": str(doc.creation.date()),
			"hiringOrganization": {**org, "sameAs": get_url("/")},
			"employmentType": EMPLOYMENT_TYPES.get(doc.employment_type, "FULL_TIME"),
			"jobLocation": {
				"@type": "Place",
				"address": {"@type": "PostalAddress", "addressLocality": doc.location or ""},
			},
			"url": url,
			**({"validThrough": str(doc.closes_on)} if doc.closes_on else {}),
		}
	if main:
		if image:
			main["image"] = image
		schema.append({"@context": "https://schema.org", **main})
	return schema
