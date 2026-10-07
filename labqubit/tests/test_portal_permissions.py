"""Portal users must only ever see their own client's data."""

import frappe
from frappe.tests.utils import FrappeTestCase

from labqubit.permissions import get_portal_client
from labqubit.tests.utils import make_asset, make_client, make_portal_user, make_ticket


class TestPortalPermissions(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		make_client("_Test Client One")
		make_client("_Test Client Two")
		cls.user_one = make_portal_user("_Test Client One", "portal.one@example.com")
		cls.user_two = make_portal_user("_Test Client Two", "portal.two@example.com")
		cls.ticket_one = make_ticket("_Test Client One", resolution_notes="internal only")
		cls.ticket_two = make_ticket("_Test Client Two")
		cls.asset_two = make_asset("_Test Client Two", "Other client's firewall")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_portal_users_have_no_desk_access(self):
		# regression: Frappe auto-creates roles with desk access while syncing DocTypes
		self.assertEqual(frappe.db.get_value("Role", "LQ Client", "desk_access"), 0)
		self.assertEqual(frappe.db.get_value("User", self.user_one, "user_type"), "Website User")
		self.assertNotIn("Desk User", frappe.get_roles(self.user_one))

	def test_saving_client_grants_portal_role(self):
		self.assertIn("LQ Client", frappe.get_roles(self.user_one))
		self.assertEqual(get_portal_client(self.user_one), "_Test Client One")

	def test_user_cannot_belong_to_two_clients(self):
		client = frappe.get_doc("LQ Client", "_Test Client Two")
		client.append("portal_users", {"user": self.user_one})
		self.assertRaises(frappe.ValidationError, client.save)

	def test_list_queries_are_scoped(self):
		frappe.set_user(self.user_one)
		clients = set(frappe.get_list("LQ Support Ticket", pluck="client"))
		self.assertEqual(clients, {"_Test Client One"})
		self.assertEqual(frappe.get_list("LQ Client", pluck="name"), ["_Test Client One"])
		self.assertFalse(frappe.get_list("LQ Client Asset", filters={"name": self.asset_two.name}))

	def test_single_document_access(self):
		frappe.set_user(self.user_one)
		self.assertTrue(frappe.has_permission("LQ Support Ticket", "read", self.ticket_one.name))
		self.assertFalse(frappe.has_permission("LQ Support Ticket", "read", self.ticket_two.name))
		self.assertFalse(frappe.has_permission("LQ Support Ticket", "write", self.ticket_one.name))

	def test_internal_fields_hidden(self):
		frappe.set_user(self.user_one)
		doc = frappe.get_doc("LQ Support Ticket", self.ticket_one.name)
		doc.apply_fieldlevel_read_permissions()
		self.assertFalse(doc.get("resolution_notes"))

	def test_portal_api_rejects_other_clients_ticket(self):
		from labqubit.api.portal import get_client_ticket

		frappe.set_user(self.user_one)
		self.assertRaises(frappe.DoesNotExistError, get_client_ticket, self.ticket_two.name)
		self.assertEqual(get_client_ticket(self.ticket_one.name).name, self.ticket_one.name)

	def test_staff_unrestricted(self):
		from labqubit.permissions import ticket_query

		self.assertEqual(ticket_query("Administrator"), "")
