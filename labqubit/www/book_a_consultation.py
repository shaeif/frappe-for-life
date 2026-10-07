from frappe import _
from frappe.utils import add_days, today

from labqubit.website.forms import form_options

sitemap = 1


def get_context(context):
	context.title = _("Book a Consultation")
	context.description = _("Book a free consultation with a LabQubit engineer.")
	context.min_date = add_days(today(), 1)
	context.max_date = add_days(today(), 365)
	form_options(context)
