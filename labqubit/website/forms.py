import frappe

from labqubit.api.leads import BUDGETS, MEETING_MODES, TIMELINES, TIMES
from labqubit.utils.jinja import t


def form_options(context):
	"""Choices for the public lead forms, labelled in the current language."""
	context.service_options = [
		(s.name, t(s, "title"))
		for s in frappe.get_all(
			"LQ Service",
			filters={"published": 1},
			fields=["name", "title", "title_ar"],
			order_by="display_order asc",
		)
	]
	context.industry_options = [
		(i.name, t(i, "title"))
		for i in frappe.get_all(
			"LQ Industry",
			filters={"published": 1},
			fields=["name", "title", "title_ar"],
			order_by="display_order asc",
		)
	]
	context.country_options = frappe.get_all("Country", pluck="name", order_by="name asc")
	context.budgets = BUDGETS
	context.timelines = TIMELINES
	context.times = TIMES
	context.meeting_modes = MEETING_MODES
	context.endpoint = "/api/method/labqubit.api.leads.submit_enquiry"
