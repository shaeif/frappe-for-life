"""Validation helpers for public (guest) form endpoints.

Every guest endpoint follows the same rules:
- read only an explicit allowlist of fields (never `**kwargs` straight into a document)
- trim and length-limit every value, validate choices against fixed options
- silently accept-and-drop obvious bots (honeypot / too-fast submit) so they get no signal
- optionally verify Cloudflare Turnstile
"""

import re
import time

import frappe
import requests
from frappe import _
from frappe.utils import getdate, today, validate_email_address
from frappe.utils.password import get_decrypted_password

PHONE = re.compile(r"^[0-9+()\-.\s]{6,40}$")
MIN_SECONDS_ON_PAGE = 3


class FormErrors(Exception):
	def __init__(self, errors: dict):
		self.errors = errors


class FormReader:
	"""Collects cleaned values and per-field errors from frappe.form_dict."""

	def __init__(self, data=None):
		self.data = data if data is not None else frappe.form_dict
		self.errors = {}
		self.values = {}

	def text(self, field, max_length=140, required=False, label=None):
		value = self.data.get(field)
		value = "" if value is None else str(value).strip()
		if len(value) > max_length:
			self.errors[field] = _("Please keep this under {0} characters.").format(max_length)
		elif required and not value:
			self.errors[field] = _("{0} is required.").format(label or _("This field"))
		self.values[field] = value
		return value

	def email(self, field="email", required=True):
		value = self.text(field, 140, required, _("Email")).lower()
		if value and not validate_email_address(value):
			self.errors[field] = _("Enter a valid email address.")
		self.values[field] = value
		return value

	def phone(self, field="phone", required=False):
		value = self.text(field, 40, required, _("Phone"))
		if value and not PHONE.match(value):
			self.errors[field] = _("Enter a valid phone number.")
		return value

	def choice(self, field, options, required=False, label=None):
		value = self.text(field, 140, required, label)
		if value and value not in options:
			self.errors[field] = _("Choose one of the listed options.")
			self.values[field] = ""
		return self.values[field]

	def int(self, field, minimum=0, maximum=100000):
		raw = self.text(field, 10)
		if not raw:
			self.values[field] = None
			return None
		try:
			value = int(raw)
			if not minimum <= value <= maximum:
				raise ValueError
		except ValueError:
			self.errors[field] = _("Enter a number between {0} and {1}.").format(minimum, maximum)
			value = None
		self.values[field] = value
		return value

	def future_date(self, field, max_days=365, required=False):
		raw = self.text(field, 10, required, _("Date"))
		if not raw:
			self.values[field] = None
			return None
		try:
			value = getdate(raw)
		except Exception:
			self.errors[field] = _("Enter a valid date.")
			self.values[field] = None
			return None
		if value < getdate(today()) or (value - getdate(today())).days > max_days:
			self.errors[field] = _("Choose a date between today and the next {0} days.").format(max_days)
		self.values[field] = value
		return value

	def link(self, field, doctype, filters=None):
		value = self.text(field, 140)
		if value and not frappe.db.exists(doctype, {"name": value, **(filters or {})}):
			self.errors[field] = _("Choose one of the listed options.")
			self.values[field] = ""
		return self.values[field]

	def links(self, field, doctype, filters=None, limit=20):
		"""Multi-select values sent as a list or as repeated/comma-separated form values."""
		raw = self.data.get(field) or []
		if isinstance(raw, str):
			raw = [v for v in raw.split(",")]
		names = [str(v).strip() for v in raw if str(v).strip()][:limit]
		valid = set(
			frappe.get_all(doctype, filters={"name": ["in", names or [""]], **(filters or {})}, pluck="name")
		)
		self.values[field] = [n for n in names if n in valid]
		return self.values[field]

	def checked(self, field, required=False, message=None):
		value = str(self.data.get(field) or "").lower() in ("1", "true", "on", "yes")
		if required and not value:
			self.errors[field] = message or _("Please confirm to continue.")
		self.values[field] = 1 if value else 0
		return value

	def raise_if_errors(self):
		if self.errors:
			raise FormErrors(self.errors)


def looks_like_bot(data=None) -> bool:
	"""Honeypot field filled in, or the form was submitted implausibly fast."""
	data = data if data is not None else frappe.form_dict
	if (data.get("website") or "").strip():
		return True
	started = data.get("ts")
	try:
		if started and time.time() - float(started) / 1000 < MIN_SECONDS_ON_PAGE:
			return True
	except (TypeError, ValueError):
		return True
	return False


def verify_turnstile(data=None):
	"""Verify Cloudflare Turnstile when it is enabled in LQ Settings."""
	settings = frappe.get_cached_doc("LQ Settings")
	if not settings.enable_turnstile:
		return
	data = data if data is not None else frappe.form_dict
	token = data.get("cf-turnstile-response")
	secret = get_decrypted_password(
		"LQ Settings", "LQ Settings", "turnstile_secret_key", raise_exception=False
	)
	if not token or not secret:
		raise FormErrors({"captcha": _("Please complete the verification.")})
	try:
		response = requests.post(
			"https://challenges.cloudflare.com/turnstile/v0/siteverify",
			data={"secret": secret, "response": token, "remoteip": getattr(frappe.local, "request_ip", None)},
			timeout=8,
		).json()
	except Exception:
		frappe.log_error("Turnstile verification failed")
		raise FormErrors({"captcha": _("Verification is temporarily unavailable. Please try again.")})
	if not response.get("success"):
		raise FormErrors({"captcha": _("Verification failed. Please try again.")})


def tracking_values(data=None) -> dict:
	"""Attribution fields. The page URL is reduced to a same-site path."""
	data = data if data is not None else frappe.form_dict
	page = str(data.get("page_url") or "")[:500]
	page = "/" + page.split("://", 1)[-1].split("/", 1)[-1] if page else ""
	return {
		"page_url": page[:140],
		"utm_source": str(data.get("utm_source") or "")[:140],
		"utm_medium": str(data.get("utm_medium") or "")[:140],
		"utm_campaign": str(data.get("utm_campaign") or "")[:140],
		"ip_address": getattr(frappe.local, "request_ip", None),
		"language": (frappe.local.lang or "en")[:10],
	}


def respond(ok: bool, message: str = "", errors: dict | None = None, redirect: str | None = None):
	"""JSON for fetch() callers; a redirect or message page for plain HTML form posts."""
	request = getattr(frappe.local, "request", None)
	wants_html = (
		bool(request)
		and "text/html" in (request.headers.get("Accept") or "")
		and not request.headers.get("X-Requested-With")
	)
	if not ok:
		frappe.local.response.http_status_code = 422
	if wants_html:
		if ok and redirect:
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = redirect
			return
		frappe.respond_as_web_page(
			_("Thank you") if ok else _("Please check the form"),
			message if ok else "<br>".join(frappe.utils.escape_html(v) for v in (errors or {}).values()),
			indicator_color="green" if ok else "red",
			http_status_code=200 if ok else 422,
		)
		return
	return {"ok": ok, "message": message, "errors": errors or {}}
