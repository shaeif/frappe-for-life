# Copyright (c) 2026, LabQubit and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import escape_html

from labqubit.utils import notify
from labqubit.utils.assignment import form_url
from labqubit.utils.files import make_attachments_private


class LQJobApplication(Document):
	def on_update(self):
		make_attachments_private(self, "resume")

	def after_insert(self):
		hr_email = frappe.get_cached_doc("LQ Settings").careers_notification_email
		notify.send(
			[hr_email],
			subject=_("New application: {0} for {1}").format(self.applicant_name, self.job_opening),
			heading=_("New job application"),
			rows=[
				(_("Role"), self.job_opening),
				(_("Name"), self.applicant_name),
				(_("Email"), self.email),
				(_("Phone"), self.phone),
				(_("Location"), self.current_location),
				(_("Notice period"), self.notice_period),
				(_("LinkedIn"), self.linkedin_url),
			],
			button={"label": _("Review application"), "url": form_url(self)},
			doc=self,
			reply_to=self.email,
		)
		notify.send(
			[self.email],
			subject=_("We received your application"),
			heading=_("Thank you, {0}").format(escape_html(self.applicant_name.split(" ")[0])),
			intro=_(
				"We received your application for {0}. Our team reviews every application and will contact you if there is a fit."
			).format(escape_html(self.job_opening)),
			doc=self,
		)
