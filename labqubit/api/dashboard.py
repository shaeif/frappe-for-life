import frappe
from frappe.utils import add_days, today


@frappe.whitelist()
def lead_conversion_rate(filters=None):
	"""Number Card: Won ÷ (Won + Lost) for leads closed in the last 90 days."""
	frappe.has_permission("LQ Lead", "read", throw=True)
	closed = frappe.get_all(
		"LQ Lead",
		filters={"status": ["in", ["Won", "Lost"]], "closed_on": [">=", add_days(today(), -90)]},
		fields=["status", "count(name) as n"],
		group_by="status",
	)
	counts = {row.status: row.n for row in closed}
	total = counts.get("Won", 0) + counts.get("Lost", 0)
	return {"value": round(counts.get("Won", 0) * 100 / total, 1) if total else 0, "fieldtype": "Percent"}
