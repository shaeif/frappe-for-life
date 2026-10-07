from frappe import _

from labqubit.website.context import open_jobs


def get_context(context):
	context.title = _("Careers")
	context.description = _("Join LabQubit's team of network, security and data center engineers.")
	context.jobs = open_jobs()
