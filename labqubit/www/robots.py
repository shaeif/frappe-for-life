import frappe
from frappe.utils import get_url

base_template_path = "www/robots.txt"

DEFAULT = """User-agent: *
Disallow: /app
Disallow: /api/
Disallow: /portal
Disallow: /login
Disallow: /update-password
Disallow: /thank-you
Disallow: /styleguide
Disallow: /private/

Sitemap: {sitemap}
"""


def get_context(context):
	"""Website Settings > Robots.txt wins when set; otherwise a safe default."""
	custom = frappe.db.get_single_value("Website Settings", "robots_txt")
	return {"robots_txt": custom or DEFAULT.format(sitemap=get_url("/sitemap.xml"))}
