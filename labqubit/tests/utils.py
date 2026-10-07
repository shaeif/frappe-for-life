import frappe
from frappe.utils import add_days, today


def make_client(name):
	if not frappe.db.exists("LQ Client", name):
		frappe.get_doc({"doctype": "LQ Client", "client_name": name}).insert(ignore_permissions=True)
	return frappe.get_doc("LQ Client", name)


def make_portal_user(client, email):
	if not frappe.db.exists("User", email):
		frappe.get_doc(
			{
				"doctype": "User",
				"email": email,
				"first_name": "Test",
				"user_type": "Website User",
				"send_welcome_email": 0,
			}
		).insert(ignore_permissions=True)
	client = frappe.get_doc("LQ Client", client)
	if email not in [r.user for r in client.portal_users]:
		client.append("portal_users", {"user": email})
		client.save(ignore_permissions=True)
	return email


def make_asset(client, name, serial=None):
	return frappe.get_doc(
		{
			"doctype": "LQ Client Asset",
			"asset_name": name,
			"client": client,
			"asset_type": "Firewall",
			"serial_number": serial,
		}
	).insert(ignore_permissions=True)


def make_contract(client, assets=(), start_offset=-100, end_offset=265, status="Active"):
	return frappe.get_doc(
		{
			"doctype": "LQ AMC Contract",
			"contract_title": f"{client} AMC",
			"client": client,
			"coverage_level": "Standard",
			"status": status,
			"start_date": add_days(today(), start_offset),
			"end_date": add_days(today(), end_offset),
			"covered_assets": [{"asset": a} for a in assets],
		}
	).insert(ignore_permissions=True)


def make_ticket(client, priority="Medium", **kwargs):
	return frappe.get_doc(
		{
			"doctype": "LQ Support Ticket",
			"subject": "Test issue",
			"client": client,
			"priority": priority,
			"description": "x",
			**kwargs,
		}
	).insert(ignore_permissions=True)
