"""Guest form endpoints: validation, field allowlist and bot handling."""

import time

import frappe
from frappe.tests.utils import FrappeTestCase

from labqubit.api.leads import submit_enquiry


def call(**data):
	frappe.local.form_dict = frappe._dict(data)
	frappe.local.response = frappe._dict()
	return submit_enquiry()


VALID = {
	"lead_type": "Quote Request",
	"full_name": "Test Visitor",
	"email": "Visitor@Example.com",
	"phone": "+971 50 000 0000",
	"company": "Example LLC",
	"consent": "1",
	"budget_range": "Not sure",
}


class TestLeadsAPI(FrappeTestCase):
	def setUp(self):
		frappe.set_user("Guest")

	def tearDown(self):
		frappe.set_user("Administrator")

	def latest(self, email):
		return frappe.get_all(
			"LQ Lead", filters={"email": email}, fields=["*"], order_by="creation desc", limit=1
		)

	def test_valid_submission_creates_lead(self):
		result = call(**VALID, ts=str((time.time() - 10) * 1000))
		self.assertTrue(result["ok"])
		lead = self.latest("visitor@example.com")[0]
		self.assertEqual(lead.lead_type, "Quote Request")
		self.assertEqual(lead.status, "New")

	def test_internal_fields_cannot_be_set(self):
		call(
			**{
				**VALID,
				"email": "allowlist@example.com",
				"status": "Won",
				"lead_owner": "Administrator",
				"source": "Referral",
			}
		)
		lead = self.latest("allowlist@example.com")[0]
		self.assertEqual(lead.status, "New")
		self.assertEqual(lead.source, "Website")
		self.assertNotEqual(lead.lead_owner, "Administrator")

	def test_validation_errors(self):
		result = call(lead_type="Quote Request", email="not-an-email")
		self.assertFalse(result["ok"])
		for field in ("full_name", "email", "phone", "company", "consent"):
			self.assertIn(field, result["errors"])
		self.assertEqual(frappe.local.response.http_status_code, 422)

	def test_unknown_choice_rejected(self):
		result = call(**{**VALID, "budget_range": "A billion"})
		self.assertIn("budget_range", result["errors"])

	def test_honeypot_creates_nothing(self):
		result = call(**{**VALID, "email": "bot@example.com", "website": "http://spam.example"})
		self.assertTrue(result["ok"])
		self.assertFalse(self.latest("bot@example.com"))

	def test_too_fast_creates_nothing(self):
		result = call(**{**VALID, "email": "fast@example.com", "ts": str(time.time() * 1000)})
		self.assertTrue(result["ok"])
		self.assertFalse(self.latest("fast@example.com"))

	def test_unknown_lead_type(self):
		self.assertFalse(call(**{**VALID, "lead_type": "Admin"})["ok"])
