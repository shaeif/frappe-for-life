"""Branded transactional emails. Emails are queued (Email Queue) and sent by the scheduler
through the default outgoing Email Account.

Sending never blocks the business action: a lead, ticket or application is saved even if
email is not configured yet or the mail server is down.
"""

import frappe
from frappe.utils import escape_html


def send(recipients, subject, heading, intro="", rows=None, button=None, doc=None, footer="", reply_to=None):
	recipients = sorted({r.strip().lower() for r in (recipients or []) if r and "@" in r})
	if not recipients:
		return
	settings = frappe.get_cached_doc("LQ Settings")
	try:
		_sendmail(recipients, subject, heading, intro, rows, button, doc, footer, reply_to, settings)
	except frappe.OutgoingEmailError:
		frappe.clear_last_message()
		frappe.logger("labqubit").warning("Email not sent (no outgoing Email Account): %s", subject)
	except Exception:
		frappe.clear_last_message()
		frappe.log_error(title=f"LabQubit email failed: {subject}"[:140])


def _sendmail(recipients, subject, heading, intro, rows, button, doc, footer, reply_to, settings):
	frappe.sendmail(
		recipients=recipients,
		subject=subject,
		template="lq_notification",
		args={
			"heading": heading,
			"intro": intro,
			"rows": [
				(label, escape_html(str(value))) for label, value in (rows or []) if value not in (None, "")
			],
			"button": button,
			"footer": footer,
			"company": settings.company_name or "LabQubit",
			"site_url": frappe.utils.get_url(),
		},
		reference_doctype=doc.doctype if doc else None,
		reference_name=doc.name if doc else None,
		reply_to=reply_to,
		now=frappe.flags.in_test,
	)
