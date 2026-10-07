"""Staff tools for managing client portal access."""

import frappe
from frappe import _
from frappe.utils import validate_email_address


@frappe.whitelist(methods=["POST"])
def create_portal_user(client: str, email: str, first_name: str, last_name: str = "", primary: int = 0):
	"""Create (or reuse) a Website User and give them portal access to `client`.

	Requires write permission on the LQ Client. New users receive Frappe's welcome email
	with a link to set their password.
	"""
	client_doc = frappe.get_doc("LQ Client", client)
	client_doc.check_permission("write")

	email = (email or "").strip().lower()
	if not validate_email_address(email):
		frappe.throw(_("Enter a valid email address."))

	if frappe.db.exists("User", email):
		user = frappe.get_doc("User", email)
		if user.user_type == "System User":
			frappe.throw(_("{0} is a staff account. Use a separate email for portal access.").format(email))
	else:
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": first_name.strip(),
				"last_name": (last_name or "").strip(),
				"user_type": "Website User",
				"send_welcome_email": 0,
			}
		).insert(ignore_permissions=True)
		# Send the invite separately so a mail server problem never blocks granting access
		try:
			user.send_welcome_mail_to_user()
		except Exception:
			frappe.clear_last_message()
			frappe.log_error(title=f"Portal invite email failed for {email}")
			frappe.msgprint(
				_(
					"Access was granted, but the invitation email could not be sent. Check the outgoing email account, then use Reset Password on the user."
				),
				indicator="orange",
			)

	if email not in [row.user for row in client_doc.portal_users]:
		client_doc.append("portal_users", {"user": email, "is_primary": int(primary)})
		client_doc.save()
	return email
