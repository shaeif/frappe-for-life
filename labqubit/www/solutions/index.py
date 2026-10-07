from frappe import _

sitemap = 1


def get_context(context):
	context.title = _("Solutions")
	context.description = _("Proven architectures that combine LabQubit services and partner technology.")
