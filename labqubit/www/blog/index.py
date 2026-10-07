import frappe
from frappe import _


def get_context(context):
	category = frappe.form_dict.category
	context.categories = frappe.get_all(
		"Blog Category", filters={"published": 1}, fields=["name", "title", "route"], order_by="title asc"
	)
	filters = {"published": 1}
	context.category = None
	if category:
		context.category = next((c for c in context.categories if c.name == category), None)
		if not context.category:
			raise frappe.PageDoesNotExistError
		filters["blog_category"] = category

	context.posts = frappe.get_all(
		"Blog Post",
		filters=filters,
		fields=[
			"title",
			"route",
			"blog_intro",
			"published_on",
			"meta_image",
			"blog_category",
			"read_time",
			"blogger",
		],
		order_by="published_on desc, creation desc",
		limit=60,
	)
	context.title = context.category.title if context.category else _("Blog")
	context.description = _("Insights on networks, cybersecurity and data centers from LabQubit engineers.")
