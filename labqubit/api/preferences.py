import frappe
from frappe import _

SUPPORTED_LANGUAGES = ("en", "ar")


@frappe.whitelist(methods=["POST"])
def set_language(lang: str):
	"""Store the website language for the logged-in user (guests use the cookie only)."""
	if lang not in SUPPORTED_LANGUAGES:
		frappe.throw(_("Unsupported language"), frappe.ValidationError)
	frappe.local.cookie_manager.set_cookie("preferred_language", lang)
	if frappe.session.user != "Guest":
		frappe.db.set_value("User", frappe.session.user, "language", lang)
