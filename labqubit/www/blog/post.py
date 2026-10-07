import frappe
from frappe.utils import md_to_html


def get_context(context):
	route = f"blog/{frappe.form_dict.category}/{frappe.form_dict.name}"
	name = frappe.db.get_value("Blog Post", {"route": route, "published": 1})
	if not name:
		raise frappe.PageDoesNotExistError

	post = frappe.get_doc("Blog Post", name)
	if post.content_type == "Markdown":
		context.content_html = md_to_html(post.content_md or "")
	elif post.content_type == "HTML":
		context.content_html = post.content_html
	else:
		context.content_html = post.content

	context.post = post
	context.title = post.meta_title or post.title
	context.description = post.meta_description or post.blog_intro
	context.og_image = post.meta_image
	context.og_type = "article"
	context.category = frappe.db.get_value(
		"Blog Category", post.blog_category, ["title", "route"], as_dict=True
	)
	context.author = frappe.db.get_value(
		"Blogger", post.blogger, ["full_name", "avatar", "bio"], as_dict=True
	)
	context.related = frappe.get_all(
		"Blog Post",
		filters={"published": 1, "blog_category": post.blog_category, "name": ["!=", post.name]},
		fields=["title", "route", "published_on"],
		order_by="published_on desc",
		limit=3,
	)
	context.schema = [
		{
			"@context": "https://schema.org",
			"@type": "BlogPosting",
			"headline": post.title,
			"datePublished": str(post.published_on or post.creation.date()),
			"dateModified": str(post.modified.date()),
			"author": {
				"@type": "Organization",
				"name": (context.author or {}).get("full_name") or "LabQubit",
			},
			"description": context.description or "",
			"mainEntityOfPage": frappe.utils.get_url(post.route),
			**({"image": frappe.utils.get_url(post.meta_image)} if post.meta_image else {}),
		}
	]
