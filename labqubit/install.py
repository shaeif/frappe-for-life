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


# System Settings tightened on install. Values are only changed while they still have
# Frappe's default, so an administrator's own choice is never overwritten.
SECURITY_DEFAULTS = {
	# field: (frappe default, labqubit value)
	"allow_consecutive_login_attempts": (10, 5),
	"allow_login_after_fail": (60, 300),
	"minimum_password_score": ("2", "3"),
}


def after_install():
	ensure_roles()
	ensure_default_records()
	apply_security_defaults()


def after_migrate():
	ensure_roles()


def ensure_roles():
	"""Create the roles, and enforce their desk access on every install/migrate.

	Frappe auto-creates roles named in DocType permissions while syncing DocTypes, *before*
	after_install runs, and gives them desk access. "LQ Client" must never have it, or portal
	users become Desk (System) users.
	"""
	for role_name, desk_access, home_page in ROLES:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc(
				{
					"doctype": "Role",
					"role_name": role_name,
					"desk_access": desk_access,
					"home_page": home_page,
				}
			).insert(ignore_permissions=True)
		elif frappe.db.get_value("Role", role_name, "desk_access") != desk_access:
			frappe.db.set_value("Role", role_name, "desk_access", desk_access)
	fix_portal_user_types()


def fix_portal_user_types():
	"""Users whose only real role is LQ Client must be Website Users (no Desk)."""
	ignored = {"LQ Client", "All", "Guest", "Desk User"}
	for user in frappe.get_all(
		"Has Role", filters={"role": "LQ Client", "parenttype": "User"}, pluck="parent"
	):
		if frappe.db.get_value("User", user, "user_type") != "System User":
			continue
		roles = set(frappe.get_all("Has Role", filters={"parent": user, "parenttype": "User"}, pluck="role"))
		if roles - ignored:
			continue  # also has a staff role: leave as is
		doc = frappe.get_doc("User", user)
		doc.remove_roles("Desk User")
		frappe.db.set_value("User", user, "user_type", "Website User")


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
	settings.default_sla_policy = settings.default_sla_policy or "Standard"
	settings.tagline = settings.tagline or "Resilient solutions for resilient businesses"
	settings.tagline_ar = settings.tagline_ar or "حلول مرنة لأعمال مرنة"
	settings.save(ignore_permissions=True)


def apply_security_defaults():
	settings = frappe.get_single("System Settings")
	changed = False
	for field, (frappe_default, value) in SECURITY_DEFAULTS.items():
		if str(settings.get(field)) == str(frappe_default):
			settings.set(field, value)
			changed = True
	settings.enable_password_policy = 1
	settings.allow_guests_to_upload_files = 0
	if changed:
		settings.flags.ignore_mandatory = True
		settings.save(ignore_permissions=True)
	# no public self-signup: portal accounts are created by staff
	frappe.db.set_single_value("Website Settings", "disable_signup", 1)
