"""SLA rules for support tickets. Targets are calendar hours (24x7)."""

import frappe
from frappe.utils import add_to_date, cint, get_datetime, now_datetime

OPEN_STATUSES = ("Open", "In Progress", "Waiting on Client")
DONE_STATUSES = ("Resolved", "Closed")


def resolve_policy(ticket):
	"""Contract policy → client default → LQ Settings default → any default policy."""
	name = None
	if ticket.amc_contract:
		name = frappe.db.get_value("LQ AMC Contract", ticket.amc_contract, "sla_policy")
	if not name and ticket.client:
		name = frappe.db.get_value("LQ Client", ticket.client, "default_sla_policy")
	if not name:
		name = frappe.get_cached_doc("LQ Settings").default_sla_policy
	if not name:
		name = frappe.db.get_value("LQ SLA Policy", {"is_default": 1})
	return frappe.get_cached_doc("LQ SLA Policy", name) if name else None


def set_targets(ticket):
	policy = resolve_policy(ticket)
	if not policy:
		ticket.sla_policy = ticket.response_due_by = ticket.resolution_due_by = None
		return
	target = policy.get_target(ticket.priority)
	ticket.sla_policy = policy.name
	ticket.response_due_by = add_to_date(ticket.opened_on, hours=target.response_hours)
	ticket.resolution_due_by = add_to_date(ticket.opened_on, hours=target.resolution_hours)


def status_at(ticket, at=None, at_risk_percent=None):
	"""On Track / At Risk / Breached for an open ticket; Met / Breached once resolved."""
	if not ticket.get("response_due_by"):
		return None
	at = get_datetime(at or now_datetime())
	opened = get_datetime(ticket.opened_on)
	response_due = get_datetime(ticket.response_due_by)
	resolution_due = get_datetime(ticket.resolution_due_by)
	responded = ticket.get("first_responded_on") and get_datetime(ticket.first_responded_on)
	resolved = ticket.get("resolved_on") and get_datetime(ticket.resolved_on)

	response_breached = (responded or at) > response_due
	if resolved:
		return "Breached" if response_breached or resolved > resolution_due else "Met"
	if response_breached or at > resolution_due:
		return "Breached"

	if at_risk_percent is None:
		at_risk_percent = cint(frappe.get_cached_doc("LQ Settings").sla_at_risk_percent) or 75
	due = resolution_due if responded else response_due
	window = (due - opened).total_seconds() or 1
	used = (at - opened).total_seconds() / window * 100
	return "At Risk" if used >= at_risk_percent else "On Track"
