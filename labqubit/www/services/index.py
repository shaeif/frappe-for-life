from frappe import _

sitemap = 1


def get_context(context):
	context.title = _("Services")
	context.description = _(
		"Network infrastructure and automation, cybersecurity, data center, structured cabling, managed services, cloud consulting, and web and application development."
	)
