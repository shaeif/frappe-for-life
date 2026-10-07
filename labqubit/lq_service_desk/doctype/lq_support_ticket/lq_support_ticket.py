# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LQSupportTicket(Document):
	def validate(self):
		self.validate_links_belong_to_client()

	def validate_links_belong_to_client(self):
		if self.asset:
			asset_client, asset_contract = frappe.db.get_value(
				"LQ Client Asset", self.asset, ["client", "amc_contract"]
			)
			if asset_client != self.client:
				frappe.throw(_("Asset {0} does not belong to {1}.").format(self.asset, self.client))
			self.amc_contract = self.amc_contract or asset_contract

		if (
			self.amc_contract
			and frappe.db.get_value("LQ AMC Contract", self.amc_contract, "client") != self.client
		):
			frappe.throw(_("AMC contract {0} does not belong to {1}.").format(self.amc_contract, self.client))
