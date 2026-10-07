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

# Tailwind output (built by `yarn build` / `bench build`). Not included globally yet:
# Tailwind's reset would restyle Frappe's default web pages before our own base
# template exists. Phase 3 links it from our base template via `asset_url()`.
# web_include_css = "/assets/labqubit/css/labqubit.css"
# web_include_js = "/assets/labqubit/js/site.js"

# Website
# ------------------

# Phase 3: our own base template and home page
# base_template = "templates/lq_base.html"
# home_page = "index"

# Phase 3: SEO-friendly routes for web-view DocTypes
# website_route_rules = []

# Phase 6: client portal sidebar
# portal_menu_items = []

# Jinja
# ----------

jinja = {
	"methods": [
		"labqubit.utils.jinja.asset_url",
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

# doc_events = {}

# Scheduled Tasks
# ---------------
# Phase 5: SLA checks, AMC renewal reminders

# scheduler_events = {}

# Fixtures
# --------
# Phase 2+: custom fields, roles, workflows, assignment rules exported with
# `bench --site <site> export-fixtures --app labqubit`

# fixtures = []

# Testing
# -------

# before_tests = "labqubit.install.before_tests"
