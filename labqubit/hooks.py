app_name = "labqubit"
app_title = "LabQubit"
app_publisher = "LabQubit"
app_description = "LabQubit company website and client portal"
app_email = ""
app_license = "Proprietary"

# Apps
# ------------------

# required_apps = []

# Includes in <head>
# ------------------

# CSS and JS are linked from templates/lq_base.html via asset_url() (content-hashed URLs),
# not web_include_css/js, so they are cache-busted on every build.

# Website
# ------------------

# "/" is the marketing home page for everyone (www/index.html)
home_page = "index"

# Every website page (ours and Frappe's built-in ones) renders inside our layout
base_template = "templates/lq_base.html"
update_website_context = "labqubit.website.context.update_website_context"

# Blog posts are written with Frappe's Blog Post DocType but rendered by www/blog/*.
# The explicit "/blog" rule wins over Frappe's own list route for Blog Post.
website_route_rules = [
	{"from_route": "/blog", "to_route": "blog"},
	{"from_route": "/blog/<category>/<name>", "to_route": "blog/post"},
	{"from_route": "/blog/<category>", "to_route": "blog"},
]

# Phase 6: client portal sidebar
# portal_menu_items = []

# Jinja
# ----------

jinja = {
	"methods": [
		"labqubit.utils.jinja.asset_url",
		"labqubit.utils.jinja.lq_icon",
		"labqubit.utils.jinja.t",
		"labqubit.utils.jinja.is_arabic",
	],
	"filters": [
		"labqubit.utils.jinja.json_script",
	],
}

# Installation
# ------------

after_install = "labqubit.install.after_install"
after_migrate = "labqubit.install.after_migrate"

# Permissions
# -----------
# Phase 6: restrict portal users to their own records

# permission_query_conditions = {}
# has_permission = {}
# has_website_permission = {}

# Document Events
# ---------------

_clear_website = {
	"on_update": "labqubit.website.context.clear_website_cache",
	"on_trash": "labqubit.website.context.clear_website_cache",
}

doc_events = {
	doctype: _clear_website
	for doctype in (
		"LQ Service",
		"LQ Solution",
		"LQ Industry",
		"LQ Case Study",
		"LQ Partner",
		"LQ Testimonial",
		"LQ Certification",
		"LQ Job Opening",
		"LQ Settings",
		"Blog Post",
	)
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"cron": {
		"*/15 * * * *": ["labqubit.tasks.update_ticket_sla"],
	},
	"daily": ["labqubit.tasks.update_amc_contracts"],
}

# Fixtures
# --------
# Records owned by this app, exported with `bench --site <site> export-fixtures --app labqubit`.
# Roles are created in install.py (they must exist before fixtures load).

LEAD_WORKFLOW_STATES = ["New", "Contacted", "Qualified", "Proposal Sent", "Won", "Lost"]
LEAD_WORKFLOW_ACTIONS = ["Mark Contacted", "Qualify", "Send Proposal", "Mark Won", "Mark Lost", "Reopen"]

fixtures = [
	{"dt": "Workflow State", "filters": [["name", "in", LEAD_WORKFLOW_STATES]]},
	{"dt": "Workflow Action Master", "filters": [["name", "in", LEAD_WORKFLOW_ACTIONS]]},
	{"dt": "Workflow", "filters": [["name", "in", ["LQ Lead Workflow"]]]},
]

# Testing
# -------

# before_tests = "labqubit.install.before_tests"
