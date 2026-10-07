import frappe
from frappe.tests.utils import FrappeTestCase

from labqubit.tests.utils import make_asset, make_client, make_contract


class TestAMCContract(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		make_client("_Test AMC Client")
		make_client("_Test AMC Other")

	def test_status_from_dates(self):
		self.assertEqual(make_contract("_Test AMC Client", end_offset=200).status, "Active")
		self.assertEqual(make_contract("_Test AMC Client", end_offset=10).status, "Expiring Soon")
		self.assertEqual(
			make_contract("_Test AMC Client", start_offset=-400, end_offset=-1).status, "Expired"
		)
		self.assertEqual(make_contract("_Test AMC Client", status="Draft").status, "Draft")

	def test_assets_must_belong_to_client(self):
		other = make_asset("_Test AMC Other", "Other asset")
		self.assertRaises(frappe.ValidationError, make_contract, "_Test AMC Client", [other.name])

	def test_assets_link_and_renewal(self):
		asset = make_asset("_Test AMC Client", "Core switch")
		contract = make_contract("_Test AMC Client", [asset.name])
		self.assertEqual(frappe.db.get_value("LQ Client Asset", asset.name, "amc_contract"), contract.name)
		renewal = frappe.get_doc("LQ AMC Contract", contract.create_renewal())
		self.assertEqual(renewal.status, "Draft")
		self.assertEqual(frappe.db.get_value("LQ AMC Contract", contract.name, "renewed_by"), renewal.name)
		# the current contract stays in force until the renewal is activated
		self.assertEqual(frappe.db.get_value("LQ Client Asset", asset.name, "amc_contract"), contract.name)
		self.assertRaises(
			frappe.ValidationError, frappe.get_doc("LQ AMC Contract", contract.name).create_renewal
		)

	def test_end_before_start_rejected(self):
		self.assertRaises(frappe.ValidationError, make_contract, "_Test AMC Client", (), -10, -20)
