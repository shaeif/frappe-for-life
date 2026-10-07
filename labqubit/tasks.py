"""Scheduled jobs (see scheduler_events in hooks.py)."""

import frappe
from frappe import _
from frappe.utils import cint, today

from labqubit.lq_service_desk.doctype.lq_amc_contract.lq_amc_contract import get_contract_status
from labqubit.service_desk import sla
from labqubit.utils import notify
from labqubit.utils.assignment import form_url


def update_ticket_sla():
	"""Every 15 minutes: refresh SLA status of open tickets and alert once on breach."""
	at_risk = cint(frappe.get_cached_doc("LQ Settings").sla_at_risk_percent) or 75
	tickets = frappe.get_all(
		"LQ Support Ticket",
		filters={"status": ["in", sla.OPEN_STATUSES], "response_due_by": ["is", "set"]},
		fields=[
			"name",
			"opened_on",
			"response_due_by",
			"resolution_due_by",
			"first_responded_on",
			"resolved_on",
			"sla_status",
			"breach_notified",
		],
	)
	for t in tickets:
		status = sla.status_at(t, at_risk_percent=at_risk)
		if status != t.sla_status:
			frappe.db.set_value("LQ Support Ticket", t.name, "sla_status", status, update_modified=False)
		if status == "Breached" and not t.breach_notified:
			frappe.db.set_value("LQ Support Ticket", t.name, "breach_notified", 1, update_modified=False)
			_notify_breach(frappe.get_doc("LQ Support Ticket", t.name))
	frappe.db.commit()


def _notify_breach(ticket):
	settings = frappe.get_cached_doc("LQ Settings")
	notify.send(
		[*ticket.assignee_emails(), settings.support_notification_email],
		subject=_("SLA breached: {0} ({1})").format(ticket.name, ticket.client),
		heading=_("SLA breached"),
		intro=_("This ticket has passed its SLA target."),
		rows=[
			*ticket.summary_rows(),
			(_("Resolution due"), frappe.format(ticket.resolution_due_by, "Datetime")),
		],
		button={"label": _("Open ticket"), "url": form_url(ticket)},
		doc=ticket,
	)


def update_amc_contracts():
	"""Daily: move contracts through Active → Expiring Soon → Expired and send renewal reminders."""
	for name in frappe.get_all(
		"LQ AMC Contract", filters={"status": ["in", ["Active", "Expiring Soon", "Expired"]]}, pluck="name"
	):
		contract = frappe.get_doc("LQ AMC Contract", name)
		if get_contract_status(contract) != contract.status:
			contract.save(ignore_permissions=True)  # validate() derives the status, on_update syncs assets

	due = frappe.get_all(
		"LQ AMC Contract",
		filters={
			"status": "Expiring Soon",
			"renewal_notified_on": ["is", "not set"],
			"renewed_by": ["is", "not set"],
		},
		pluck="name",
	)
	for name in due:
		_send_renewal_reminder(frappe.get_doc("LQ AMC Contract", name))
		frappe.db.set_value("LQ AMC Contract", name, "renewal_notified_on", today(), update_modified=False)
	frappe.db.commit()


def _send_renewal_reminder(contract):
	client = frappe.get_doc("LQ Client", contract.client)
	staff = [
		client.account_manager and frappe.db.get_value("User", client.account_manager, "email"),
		frappe.get_cached_doc("LQ Settings").support_notification_email,
	]
	rows = [
		(_("Contract"), f"{contract.name} · {contract.contract_title}"),
		(_("Client"), contract.client),
		(_("Coverage"), _(contract.coverage_level)),
		(_("Ends on"), frappe.format(contract.end_date, "Date")),
		(_("Covered assets"), len(contract.covered_assets)),
	]
	notify.send(
		staff,
		subject=_("AMC renewal due: {0} ends {1}").format(
			contract.client, frappe.format(contract.end_date, "Date")
		),
		heading=_("AMC renewal due"),
		intro=_("Prepare the renewal proposal for this contract."),
		rows=rows,
		button={"label": _("Open contract"), "url": form_url(contract)},
		doc=contract,
	)
	primary = [r.user for r in client.portal_users if r.is_primary] or [r.user for r in client.portal_users][
		:1
	]
	notify.send(
		[frappe.db.get_value("User", u, "email") for u in primary],
		subject=_("Your support contract renews on {0}").format(frappe.format(contract.end_date, "Date")),
		heading=_("Time to renew your support contract"),
		intro=_(
			"Your LabQubit support contract is ending soon. Your account manager will contact you with renewal options."
		),
		rows=rows,
		button={
			"label": _("View contract"),
			"url": frappe.utils.get_url(f"/portal/contracts/{contract.name}"),
		},
		doc=contract,
	)
