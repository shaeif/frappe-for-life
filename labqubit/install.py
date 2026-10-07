import frappe

# (role, desk access, home page). The client home page is left empty on purpose: a Role
# home page also replaces "/" for that user. The login page sends clients to /portal instead.
ROLES = [
	("LQ Content Editor", 1, None),
	("LQ Sales User", 1, None),
	("LQ Sales Manager", 1, None),
	("LQ Support Agent", 1, None),
	("LQ Support Manager", 1, None),
	("LQ HR User", 1, None),
	("LQ Client", 0, None),
]

DEFAULT_SLA_POLICIES = {
	"Standard": [("Low", 24, 120), ("Medium", 8, 48), ("High", 4, 24), ("Critical", 1, 8)],
	"Premium": [("Low", 8, 72), ("Medium", 4, 24), ("High", 2, 8), ("Critical", 0.5, 4)],
}


def after_install():
	ensure_roles()
	ensure_default_records()


def after_migrate():
	ensure_roles()


def ensure_roles():
	for role_name, desk_access, home_page in ROLES:
		if frappe.db.exists("Role", role_name):
			continue
		frappe.get_doc(
			{
				"doctype": "Role",
				"role_name": role_name,
				"desk_access": desk_access,
				"home_page": home_page,
			}
		).insert(ignore_permissions=True)


def ensure_default_records():
	for policy_name, targets in DEFAULT_SLA_POLICIES.items():
		if frappe.db.exists("LQ SLA Policy", policy_name):
			continue
		frappe.get_doc(
			{
				"doctype": "LQ SLA Policy",
				"policy_name": policy_name,
				"is_default": policy_name == "Standard",
				"targets": [
					{"priority": p, "response_hours": resp, "resolution_hours": res}
					for p, resp, res in targets
				],
			}
		).insert(ignore_permissions=True)

	settings = frappe.get_single("LQ Settings")
	if not settings.default_sla_policy:
		settings.default_sla_policy = "Standard"
		settings.save(ignore_permissions=True)
