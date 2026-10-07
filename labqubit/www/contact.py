from frappe import _

from labqubit.website.forms import form_options


def get_context(context):
	context.title = _("Contact")
	context.description = _(
		"Contact LabQubit about networks, cybersecurity, data centers and managed services."
	)
	form_options(context)
