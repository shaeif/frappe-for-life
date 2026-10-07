# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html, get_fullname, now_datetime

from labqubit.service_desk import sla
from labqubit.utils import notify
from labqubit.utils.assignment import auto_assign, form_url

CLIENT_NOTIFY_STATUSES = ("In Progress", "Waiting on Client", "Resolved", "Closed")


def is_staff(user=None):
	user = user or frappe.session.user
	return user == "Administrator" or frappe.db.get_value("User", user, "user_type") == "System User"


class LQSupportTicket(Document):
	def before_insert(self):
		self.opened_on = self.opened_on or now_datetime()
		self.raised_by = self.raised_by or (frappe.session.user if frappe.session.user != "Guest" else None)
		if not self.contact_email and self.raised_by:
			self.contact_email = frappe.db.get_value("User", self.raised_by, "email")

	def validate(self):
		self.validate_links_belong_to_client()
		self.stamp_new_replies()
		if self.is_new() or (self.has_value_changed("priority") and not self.first_responded_on):
			sla.set_targets(self)
		self.track_status_change()
		self.sla_status = sla.status_at(self) or self.sla_status

	def after_insert(self):
		auto_assign(
			self,
			"LQ Support Agent",
			_("{0} ticket from {1}: {2}").format(_(self.priority), self.client, self.subject),
		)
		self.notify_assignees(
			_("New ticket {0}: {1}").format(self.name, self.subject), _("A new support ticket was raised.")
		)
		self.notify_client(
			_("Ticket {0} received: {1}").format(self.name, self.subject),
			_("We received your support request and will respond by {0}.").format(
				frappe.format(self.response_due_by, "Datetime")
				if self.response_due_by
				else _("the agreed time")
			),
		)

	def on_update(self):
		if self.flags.in_insert:
			return
		if self.has_value_changed("status") and self.status in CLIENT_NOTIFY_STATUSES:
			self.notify_client(
				_("Ticket {0} is now {1}").format(self.name, _(self.status)),
				_('The status of your ticket "{0}" changed to {1}.').format(
					escape_html(self.subject), _(self.status)
				),
			)
		for reply in self.flags.new_replies or []:
			if reply.is_staff:
				self.notify_client(
					_("New reply on ticket {0}").format(self.name),
					escape_html(reply.message),
					from_name=reply.author_name,
				)
			else:
				self.notify_assignees(
					_("Client replied on {0}: {1}").format(self.name, self.subject),
					escape_html(reply.message),
				)

	# ---------------------------------------------------------------- rules

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

	def stamp_new_replies(self):
		"""Fill author and time on replies added since the last save; staff replies count as a response."""
		self.flags.new_replies = []
		for reply in self.replies:
			if reply.posted_on:
				continue
			reply.posted_on = now_datetime()
			reply.posted_by = reply.posted_by or frappe.session.user
			reply.author_name = get_fullname(reply.posted_by)
			reply.is_staff = 1 if is_staff(reply.posted_by) else 0
			self.flags.new_replies.append(reply)
			if reply.is_staff and not self.first_responded_on:
				self.first_responded_on = reply.posted_on

	def track_status_change(self):
		if self.is_new():
			return
		if (
			self.has_value_changed("status")
			and is_staff()
			and not self.first_responded_on
			and self.status != "Open"
		):
			self.first_responded_on = now_datetime()
		if self.status in sla.DONE_STATUSES and not self.resolved_on:
			self.resolved_on = now_datetime()
		elif self.status in sla.OPEN_STATUSES and self.resolved_on:
			# reopened
			self.resolved_on = None

	# ---------------------------------------------------------------- email

	def assignee_emails(self):
		users = frappe.get_all(
			"ToDo",
			filters={"reference_type": self.doctype, "reference_name": self.name, "status": "Open"},
			pluck="allocated_to",
		)
		return [frappe.db.get_value("User", u, "email") for u in users]

	def notify_assignees(self, subject, intro):
		notify.send(
			self.assignee_emails(),
			subject=subject,
			heading=subject,
			intro=intro,
			rows=self.summary_rows(),
			button={"label": _("Open ticket"), "url": form_url(self)},
			doc=self,
		)

	def notify_client(self, subject, intro, from_name=None):
		notify.send(
			[self.contact_email],
			subject=subject,
			heading=subject,
			intro=intro,
			rows=self.summary_rows(),
			button={
				"label": _("View in client portal"),
				"url": frappe.utils.get_url(f"/portal/tickets/{self.name}"),
			},
			footer=_("Reply from the client portal so your message is added to the ticket.")
			+ (f" — {escape_html(from_name)}" if from_name else ""),
			doc=self,
		)

	def summary_rows(self):
		return [
			(_("Ticket"), self.name),
			(_("Subject"), self.subject),
			(_("Client"), self.client),
			(_("Priority"), _(self.priority)),
			(_("Status"), _(self.status)),
			(_("Response due"), self.response_due_by and frappe.format(self.response_due_by, "Datetime")),
		]
