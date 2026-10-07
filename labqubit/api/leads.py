"""Public form endpoints: contact, quote request, consultation booking, job application.

Security notes (guest-accessible methods):
- POST only, rate limited per IP, explicit field allowlist, server-side validation
- honeypot + minimum time-on-page (checked after validation, so people always see
  field errors; bots get a fake success); optional Cloudflare Turnstile
- documents are inserted with ignore_permissions *after* validation; nothing from the
  request can set status, owner, assignment or other internal fields
- responses never include document names, so records can't be enumerated
"""

import secrets

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit

from labqubit.utils.forms import (
	FormErrors,
	FormReader,
	looks_like_bot,
	respond,
	tracking_values,
	verify_turnstile,
)

LEAD_TYPES = ("Contact", "Quote Request", "Consultation")
BUDGETS = ("Under 10,000", "10,000 - 50,000", "50,000 - 250,000", "250,000+", "Not sure")
TIMELINES = ("ASAP", "1-3 months", "3-6 months", "6+ months", "Not sure")
TIMES = ("Morning (9-12)", "Afternoon (12-4)", "Evening (4-6)")
MEETING_MODES = ("Online", "On-site", "Phone")

THANK_YOU = {
	"Contact": "/thank-you?type=contact",
	"Quote Request": "/thank-you?type=quote",
	"Consultation": "/thank-you?type=consultation",
}

RESUME_TYPES = {
	# extension: magic-byte prefixes
	"pdf": (b"%PDF-",),
	"docx": (b"PK\x03\x04",),
	"doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
}
MAX_RESUME_BYTES = 5 * 1024 * 1024


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=8, seconds=60 * 60)
def submit_enquiry():
	"""Create an LQ Lead from the Contact, Request a Quote or Book a Consultation forms."""
	data = frappe.form_dict
	lead_type = data.get("lead_type")
	if lead_type not in LEAD_TYPES:
		return respond(False, errors={"lead_type": _("Unknown form.")})

	form = FormReader(data)
	form.text("full_name", 140, required=True, label=_("Full name"))
	form.email("email")
	form.phone("phone", required=lead_type != "Contact")
	form.text("company", 140, required=lead_type != "Contact", label=_("Company"))
	form.text("job_title", 140)
	form.link("country", "Country")
	form.link("industry", "LQ Industry", {"published": 1})
	form.links("services_of_interest", "LQ Service", {"published": 1})
	form.text("message", 5000, required=lead_type == "Contact", label=_("Message"))
	form.checked("consent", required=True, message=_("Please agree to be contacted about your request."))

	if lead_type == "Quote Request":
		form.choice("budget_range", BUDGETS)
		form.choice("timeline", TIMELINES)
		form.int("site_count", 0, 10000)
	elif lead_type == "Consultation":
		form.future_date("preferred_date", required=True)
		form.choice("preferred_time", TIMES)
		form.choice("meeting_mode", MEETING_MODES, required=True, label=_("Meeting mode"))

	try:
		form.raise_if_errors()
	except FormErrors as e:
		return respond(False, errors=e.errors)

	if looks_like_bot(data):
		# Valid-looking but bot-like: pretend success and save nothing
		return respond(True, _("Thank you. We will be in touch shortly."), redirect=THANK_YOU[lead_type])

	try:
		verify_turnstile(data)
	except FormErrors as e:
		return respond(False, errors=e.errors)

	values = dict(form.values)
	services = values.pop("services_of_interest", [])
	lead = frappe.get_doc(
		{
			"doctype": "LQ Lead",
			"lead_type": lead_type,
			"source": "Website",
			**values,
			**tracking_values(data),
			"services_of_interest": [{"service": s} for s in services],
		}
	)
	lead.insert(ignore_permissions=True)

	messages = {
		"Contact": _("Thank you for reaching out. Our team will reply within one business day."),
		"Quote Request": _("Thank you. An engineer will review your requirements and send a proposal."),
		"Consultation": _("Thank you. We will confirm your consultation time by email."),
	}
	return respond(True, messages[lead_type], redirect=THANK_YOU[lead_type])


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60 * 60)
def submit_application():
	"""Create an LQ Job Application with a private CV upload (multipart/form-data)."""
	data = frappe.form_dict
	form = FormReader(data)
	job = form.text("job_opening", 140, required=True)
	if job and not _job_accepts_applications(job):
		form.errors["job_opening"] = _("This position is no longer accepting applications.")
	form.text("applicant_name", 140, required=True, label=_("Full name"))
	form.email("email")
	form.phone("phone", required=True)
	form.text("linkedin_url", 300)
	form.text("current_location", 140)
	form.text("notice_period", 140)
	form.text("cover_letter", 5000)
	form.checked("consent", required=True, message=_("Please agree to the processing of your application."))
	if form.values.get("linkedin_url") and not form.values["linkedin_url"].startswith("https://"):
		form.errors["linkedin_url"] = _("Enter a full link starting with https://")

	upload = frappe.request.files.get("resume") if frappe.request else None
	resume_name, resume_content = None, None
	try:
		resume_name, resume_content = _read_resume(upload)
	except FormErrors as e:
		form.errors.update(e.errors)

	try:
		form.raise_if_errors()
	except FormErrors as e:
		return respond(False, errors=e.errors)

	if looks_like_bot(data):
		return respond(True, _("Thank you for applying."), redirect="/thank-you?type=application")

	try:
		verify_turnstile(data)
	except FormErrors as e:
		return respond(False, errors=e.errors)

	try:
		# Frappe also scans PDFs and rejects ones that contain JavaScript
		resume = frappe.get_doc(
			{"doctype": "File", "file_name": resume_name, "content": resume_content, "is_private": 1}
		).insert(ignore_permissions=True)
	except Exception:
		frappe.clear_last_message()
		return respond(
			False,
			errors={
				"resume": _("We couldn't read this file. Please upload a standard PDF or Word document.")
			},
		)

	application = frappe.get_doc(
		{
			"doctype": "LQ Job Application",
			**form.values,
			"status": "New",
			"resume": resume.file_url,
			"ip_address": getattr(frappe.local, "request_ip", None),
		}
	).insert(ignore_permissions=True)

	resume.db_set(
		{
			"attached_to_doctype": application.doctype,
			"attached_to_name": application.name,
			"attached_to_field": "resume",
		}
	)
	return respond(
		True,
		_("Thank you for applying. Our team will review your application and contact you if there is a fit."),
		redirect="/thank-you?type=application",
	)


def _job_accepts_applications(job):
	from labqubit.website.context import is_job_open

	doc = frappe.db.get_value(
		"LQ Job Opening", {"name": job, "published": 1}, ["status", "closes_on"], as_dict=True
	)
	return bool(doc) and is_job_open(doc)


def _read_resume(upload):
	"""Validate extension, size and file signature; return a safe random file name and bytes."""
	if not upload or not upload.filename:
		raise FormErrors({"resume": _("Please attach your CV.")})

	extension = upload.filename.rsplit(".", 1)[-1].lower() if "." in upload.filename else ""
	if extension not in RESUME_TYPES:
		raise FormErrors({"resume": _("Upload a PDF or Word document.")})

	content = upload.stream.read(MAX_RESUME_BYTES + 1)
	if len(content) > MAX_RESUME_BYTES:
		raise FormErrors({"resume": _("The file is larger than 5 MB.")})
	if not content.startswith(RESUME_TYPES[extension]):
		raise FormErrors(
			{"resume": _("The file doesn't look like a valid {0} document.").format(extension.upper())}
		)

	# Never trust the client's file name
	return f"cv-{secrets.token_hex(8)}.{extension}", content
