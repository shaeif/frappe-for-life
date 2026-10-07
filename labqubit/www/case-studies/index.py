from frappe import _

from labqubit.website.context import case_study_cards

sitemap = 1


def get_context(context):
	context.title = _("Case Studies")
	context.description = _("How LabQubit delivers secure, high-performance infrastructure for its clients.")
	context.case_studies = case_study_cards()
	context.industries = sorted({c.industry for c in context.case_studies if c.industry})
