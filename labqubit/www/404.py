from frappe import _


def get_context(context):
	context.http_status_code = 404
	context.title = _("Page not found")
	context.noindex = True
