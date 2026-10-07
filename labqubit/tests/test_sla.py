import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import add_to_date, now_datetime

from labqubit.service_desk import sla
from labqubit.tests.utils import make_client, make_ticket


class TestSLA(FrappeTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		make_client("_Test SLA Client")

	def test_targets_from_default_policy(self):
		ticket = make_ticket("_Test SLA Client", "Critical")
		policy = frappe.get_doc("LQ SLA Policy", ticket.sla_policy)
		target = policy.get_target("Critical")
		hours = (ticket.response_due_by - ticket.opened_on).total_seconds() / 3600
		self.assertAlmostEqual(hours, target.response_hours, places=2)
		self.assertEqual(ticket.sla_status, "On Track")

	def test_priority_change_before_response_recalculates(self):
		ticket = make_ticket("_Test SLA Client", "Critical")
		ticket.priority = "Low"
		ticket.save()
		low = frappe.get_doc("LQ SLA Policy", ticket.sla_policy).get_target("Low")
		hours = (ticket.response_due_by - ticket.opened_on).total_seconds() / 3600
		self.assertAlmostEqual(hours, low.response_hours, places=2)

	def test_status_progression(self):
		opened = add_to_date(now_datetime(), hours=-10)
		t = frappe._dict(
			opened_on=opened,
			response_due_by=add_to_date(opened, hours=4),
			resolution_due_by=add_to_date(opened, hours=24),
			first_responded_on=None,
			resolved_on=None,
		)
		self.assertEqual(sla.status_at(t, at=add_to_date(opened, hours=1), at_risk_percent=75), "On Track")
		self.assertEqual(sla.status_at(t, at=add_to_date(opened, hours=3.5), at_risk_percent=75), "At Risk")
		self.assertEqual(sla.status_at(t, at=add_to_date(opened, hours=5), at_risk_percent=75), "Breached")
		t.first_responded_on = add_to_date(opened, hours=1)
		self.assertEqual(sla.status_at(t, at=add_to_date(opened, hours=5), at_risk_percent=75), "On Track")
		t.resolved_on = add_to_date(opened, hours=20)
		self.assertEqual(sla.status_at(t, at_risk_percent=75), "Met")
		t.resolved_on = add_to_date(opened, hours=30)
		self.assertEqual(sla.status_at(t, at_risk_percent=75), "Breached")

	def test_resolve_and_reopen(self):
		ticket = make_ticket("_Test SLA Client")
		ticket.status = "Resolved"
		ticket.save()
		self.assertTrue(ticket.resolved_on)
		ticket.status = "In Progress"
		ticket.save()
		self.assertFalse(ticket.resolved_on)
