from frappe import _

sitemap = 1


def get_context(context):
	context.title = _("Services")
	context.description = _(
		"Network infrastructure, cybersecurity, data center, structured cabling, managed services and cloud consulting."
	)
