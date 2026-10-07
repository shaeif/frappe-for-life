"""Client portal actions. Logged-in portal users only (no allow_guest).

Portal users have read-only DocType permissions; every write goes through these methods,
which check the ticket belongs to the user's client and set internal fields server-side.
"""

import secrets

import frappe
from frappe import _
from werkzeug.utils import secure_filename

from labqubit.permissions import get_portal_client, is_portal_user
from labqubit.utils.forms import FormErrors, FormReader
from labqubit.utils.ratelimit import per_user

PRIORITIES = ("Low", "Medium", "High", "Critical")
CATEGORIES = ("Incident", "Service Request", "Change Request", "Question")

MAX_FILES = 5
MAX_FILE_BYTES = 10 * 1024 * 1024
ALLOWED_FILES = {
	"png": (b"\x89PNG",),
	"jpg": (b"\xff\xd8\xff",),
	"jpeg": (b"\xff\xd8\xff",),
	"webp": (b"RIFF",),
	"pdf": (b"%PDF-",),
	"txt": None,  # text files: no signature, but must decode as UTF-8
	"log": None,
	"csv": None,
}


def require_portal_client():
	if frappe.session.user == "Guest":
		frappe.throw(_("Please sign in."), frappe.AuthenticationError)
	client = get_portal_client() if is_portal_user() else None
	if not client:
		frappe.throw(_("Your account is not linked to a client."), frappe.PermissionError)
	return client


def get_client_ticket(name):
	client = require_portal_client()
	ticket_client = frappe.db.get_value("LQ Support Ticket", name, "client")
	if ticket_client != client:
		# same response whether it doesn't exist or belongs to someone else
		frappe.throw(_("Ticket not found."), frappe.DoesNotExistError)
	return frappe.get_doc("LQ Support Ticket", name)


@frappe.whitelist(methods=["POST"])
@per_user(limit=30, seconds=60 * 60)
def create_ticket():
	client = require_portal_client()
	form = FormReader()
	form.text("subject", 140, required=True, label=_("Subject"))
	form.text("description", 10000, required=True, label=_("Description"))
	form.choice("priority", PRIORITIES, required=True, label=_("Priority"))
	form.choice("category", CATEGORIES)
	form.link("asset", "LQ Client Asset", {"client": client})
	try:
		form.raise_if_errors()
		files = read_uploads()
	except FormErrors as e:
		frappe.local.response.http_status_code = 422
		return {"ok": False, "errors": e.errors}

	ticket = frappe.get_doc(
		{
			"doctype": "LQ Support Ticket",
			"client": client,
			"subject": form.values["subject"],
			"description": form.values["description"],
			"priority": form.values["priority"],
			"category": form.values["category"] or "Incident",
			"asset": form.values["asset"] or None,
			"status": "Open",
			"raised_by": frappe.session.user,
		}
	).insert(ignore_permissions=True)
	attach_files(ticket, files)
	return {
		"ok": True,
		"message": _("Ticket {0} created.").format(ticket.name),
		"redirect": f"/portal/tickets/{ticket.name}",
	}


@frappe.whitelist(methods=["POST"])
@per_user(limit=60, seconds=60 * 60)
def add_reply():
	data = frappe.form_dict
	ticket = get_client_ticket(data.get("ticket"))
	form = FormReader()
	form.text("message", 10000, required=True, label=_("Message"))
	try:
		form.raise_if_errors()
		files = read_uploads()
	except FormErrors as e:
		frappe.local.response.http_status_code = 422
		return {"ok": False, "errors": e.errors}

	if ticket.status == "Closed":
		frappe.local.response.http_status_code = 422
		return {"ok": False, "errors": {"message": _("This ticket is closed. Please open a new ticket.")}}

	message = form.values["message"]
	if files:
		message += "\n\n" + _("Attached: {0}").format(", ".join(name for name, _content in files))
	ticket.append("replies", {"message": message, "posted_by": frappe.session.user})
	# a client reply on a ticket waiting for them puts it back in the queue
	if ticket.status in ("Waiting on Client", "Resolved"):
		ticket.status = "In Progress" if ticket.first_responded_on else "Open"
	ticket.save(ignore_permissions=True)
	attach_files(ticket, files)
	return {"ok": True, "message": _("Reply sent."), "redirect": f"/portal/tickets/{ticket.name}"}


@frappe.whitelist(methods=["POST"])
@per_user(limit=60, seconds=60 * 60)
def set_ticket_status(ticket, action):
	ticket = get_client_ticket(ticket)
	if action == "resolve" and ticket.status in ("Open", "In Progress", "Waiting on Client"):
		ticket.status = "Resolved"
	elif action == "reopen" and ticket.status == "Resolved":
		ticket.status = "In Progress" if ticket.first_responded_on else "Open"
	else:
		frappe.throw(_("This action is not available for the ticket's current status."))
	ticket.save(ignore_permissions=True)
	return {"ok": True, "redirect": f"/portal/tickets/{ticket.name}"}


def read_uploads():
	"""Validate uploaded files (type by extension and signature, size, count)."""
	uploads = frappe.request.files.getlist("files") if frappe.request else []
	uploads = [u for u in uploads if u and u.filename]
	if len(uploads) > MAX_FILES:
		raise FormErrors({"files": _("Attach up to {0} files.").format(MAX_FILES)})
	files = []
	for upload in uploads:
		name = secure_filename(upload.filename) or "file"
		extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
		if extension not in ALLOWED_FILES:
			raise FormErrors({"files": _("{0}: file type not allowed.").format(name)})
		content = upload.stream.read(MAX_FILE_BYTES + 1)
		if len(content) > MAX_FILE_BYTES:
			raise FormErrors({"files": _("{0} is larger than 10 MB.").format(name)})
		signatures = ALLOWED_FILES[extension]
		if signatures and not content.startswith(signatures):
			raise FormErrors({"files": _("{0} doesn't match its file type.").format(name)})
		if signatures is None:
			try:
				content.decode("utf-8")
			except UnicodeDecodeError:
				raise FormErrors({"files": _("{0} must be a plain text file.").format(name)})
		files.append((name, content))
	return files


def attach_files(ticket, files):
	for name, content in files:
		frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"{secrets.token_hex(4)}-{name}",
				"content": content,
				"is_private": 1,
				"attached_to_doctype": ticket.doctype,
				"attached_to_name": ticket.name,
			}
		).insert(ignore_permissions=True)
