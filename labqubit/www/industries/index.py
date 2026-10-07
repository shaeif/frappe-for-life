from frappe import _

sitemap = 1


def get_context(context):
	context.title = _("Industries")
	context.description = _(
		"IT infrastructure and security for enterprise, government, oil & gas and hospitality."
	)
