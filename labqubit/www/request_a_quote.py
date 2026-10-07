from frappe import _

from labqubit.website.forms import form_options


def get_context(context):
	context.title = _("Request a Quote")
	context.description = _("Tell LabQubit about your project and receive a tailored proposal.")
	form_options(context)
