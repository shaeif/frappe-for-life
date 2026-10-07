import frappe
from frappe.website.website_generator import WebsiteGenerator


class LQWebsiteGenerator(WebsiteGenerator):
	"""Base for LabQubit DocTypes that have their own public page.

	- The record name is the title (readable links in Desk), not the URL slug.
	- The route is `<doctype route>/<slug of title>`, e.g. services/sd-wan.
	- Page context is built in labqubit.website.context (Phase 3).
	"""

	def autoname(self):
		self.name = self.title.strip()

	def get_context(self, context):
		from labqubit.website.context import build_generator_context

		build_generator_context(self, context)
