# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html, today, validate_email_address

from labqubit.utils import notify
from labqubit.utils.assignment import auto_assign, form_url

CLOSED_STATUSES = ("Won", "Lost")


class LQLead(Document):
	def validate(self):
		self.email = (self.email or "").strip().lower()
		validate_email_address(self.email, throw=True)
		self.set_closed_on()

	def after_insert(self):
		owner = auto_assign(
			self, "LQ Sales User", _("New {0} from {1}").format(_(self.lead_type), self.full_name)
		)
		if owner and not self.lead_owner:
			self.db_set("lead_owner", owner, update_modified=False)
		self.notify_team()
		self.acknowledge_visitor()

	def set_closed_on(self):
		if self.status in CLOSED_STATUSES:
			self.closed_on = self.closed_on or today()
		else:
			self.closed_on = None

	def notify_team(self):
		settings = frappe.get_cached_doc("LQ Settings")
		recipients = [
			self.lead_owner and frappe.db.get_value("User", self.lead_owner, "email"),
			settings.lead_notification_email,
		]
		services = ", ".join(r.service for r in self.services_of_interest)
		notify.send(
			recipients,
			subject=_("New {0}: {1} ({2})").format(
				_(self.lead_type), self.full_name, self.company or self.email
			),
			heading=_("New {0}").format(_(self.lead_type)),
			intro=_("A new enquiry arrived from the website."),
			rows=[
				(_("Name"), self.full_name),
				(_("Email"), self.email),
				(_("Phone"), self.phone),
				(_("Company"), self.company),
				(_("Job title"), self.job_title),
				(_("Country"), self.country),
				(_("Industry"), self.industry),
				(_("Services"), services),
				(_("Budget"), self.budget_range),
				(_("Timeline"), self.timeline),
				(_("Sites"), self.site_count),
				(_("Preferred date"), self.preferred_date and frappe.format(self.preferred_date, "Date")),
				(_("Preferred time"), self.preferred_time),
				(_("Meeting"), self.meeting_mode),
				(_("Message"), self.message),
				(_("Assigned to"), self.lead_owner),
			],
			button={"label": _("Open lead"), "url": form_url(self)},
			doc=self,
			reply_to=self.email,
		)

	def acknowledge_visitor(self):
		if not frappe.get_cached_doc("LQ Settings").send_lead_acknowledgement:
			return
		subjects = {
			"Contact": _("We received your message"),
			"Quote Request": _("We received your quote request"),
			"Consultation": _("Your consultation request"),
		}
		intros = {
			"Contact": _(
				"Thank you for contacting LabQubit. A member of our team will reply within one business day."
			),
			"Quote Request": _(
				"Thank you for your interest. An engineer is reviewing your requirements and will send you a tailored proposal."
			),
			"Consultation": _(
				"Thank you for booking a consultation. We will confirm the date and time by email shortly."
			),
		}
		notify.send(
			[self.email],
			subject=subjects[self.lead_type],
			heading=_("Hello {0},").format(escape_html(self.full_name.split(" ")[0])),
			intro=intros[self.lead_type],
			rows=[
				(_("Reference"), self.name),
				(_("Preferred date"), self.preferred_date and frappe.format(self.preferred_date, "Date")),
			],
			footer=_("If you need to add anything, simply reply to this email."),
			doc=self,
		)
