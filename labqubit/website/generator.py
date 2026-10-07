import frappe
from frappe.website.website_generator import WebsiteGenerator


class LQWebsiteGenerator(WebsiteGenerator):
	"""Base for LabQubit DocTypes that have their own public page.

	- The record name is the title (readable links in Desk), not the URL slug.
	- The route is `<route_prefix>/<slug of title>`, e.g. services/sd-wan. The prefix lives on the
	  controller, not in the DocType's "Route" setting: that setting would make Frappe serve its
	  generic list page at /services instead of our www/services page.
	- Page context is built in labqubit.website.context.
	"""

	route_prefix = ""

	def autoname(self):
		self.name = self.title.strip()

	def make_route(self):
		slug = self.scrubbed_title()
		return f"{self.route_prefix}/{slug}" if self.route_prefix else slug

	def get_context(self, context):
		from labqubit.website.context import build_generator_context

		build_generator_context(self, context)
