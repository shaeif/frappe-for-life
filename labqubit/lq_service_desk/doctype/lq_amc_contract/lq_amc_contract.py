# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, cint, date_diff, getdate, today

from labqubit.utils.files import make_attachments_private

# Statuses set by people; Active / Expiring Soon / Expired are derived from the dates
MANUAL_STATUSES = ("Draft", "Renewed", "Cancelled")


class LQAMCContract(Document):
	def validate(self):
		if getdate(self.end_date) <= getdate(self.start_date):
			frappe.throw(_("End date must be after the start date."))
		self.validate_assets()
		if not self.sla_policy:
			self.sla_policy = frappe.db.get_value("LQ Client", self.client, "default_sla_policy") or (
				self.coverage_level if frappe.db.exists("LQ SLA Policy", self.coverage_level) else None
			)
		self.status = get_contract_status(self)

	def on_update(self):
		make_attachments_private(self, "contract_document")
		self.sync_asset_links()

	def on_trash(self):
		frappe.db.set_value("LQ Client Asset", {"amc_contract": self.name}, "amc_contract", None)

	def validate_assets(self):
		seen = set()
		for row in self.covered_assets:
			if row.asset in seen:
				frappe.throw(_("Row {0}: asset {1} is listed twice.").format(row.idx, row.asset))
			seen.add(row.asset)
			if frappe.db.get_value("LQ Client Asset", row.asset, "client") != self.client:
				frappe.throw(
					_("Row {0}: asset {1} does not belong to {2}.").format(row.idx, row.asset, self.client)
				)

	def sync_asset_links(self):
		"""Point each covered asset at this contract while it is in force; unlink removed assets."""
		covered = {row.asset for row in self.covered_assets}
		for asset in frappe.get_all("LQ Client Asset", filters={"amc_contract": self.name}, pluck="name"):
			if asset not in covered:
				frappe.db.set_value("LQ Client Asset", asset, "amc_contract", None)
		if self.status in ("Active", "Expiring Soon"):
			for asset in covered:
				frappe.db.set_value("LQ Client Asset", asset, "amc_contract", self.name)

	@frappe.whitelist()
	def create_renewal(self):
		"""Create the next-term contract as a Draft. This one stays in force until its end date;
		covered assets move to the renewal when it is activated."""
		self.check_permission("write")
		frappe.has_permission("LQ AMC Contract", "create", throw=True)
		if self.renewed_by:
			frappe.throw(_("This contract was already renewed by {0}.").format(self.renewed_by))

		term_days = date_diff(self.end_date, self.start_date)
		new_start = add_days(self.end_date, 1)
		renewal = frappe.copy_doc(self)
		renewal.update(
			{
				"status": "Draft",
				"start_date": new_start,
				"end_date": add_days(new_start, term_days),
				"renewed_by": None,
				"renewal_notified_on": None,
				"contract_document": None,
			}
		)
		renewal.insert()

		self.db_set("renewed_by", renewal.name)
		return renewal.name


def get_contract_status(doc, on_date=None):
	if doc.status in MANUAL_STATUSES:
		return doc.status

	on_date = getdate(on_date or today())
	end_date = getdate(doc.end_date)
	if on_date > end_date:
		return "Expired"
	if date_diff(end_date, on_date) <= cint(doc.renewal_reminder_days):
		return "Expiring Soon"
	return "Active"
