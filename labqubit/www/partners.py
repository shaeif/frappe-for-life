from frappe import _

from labqubit.website.context import PARTNER_FIELDS, published


def get_context(context):
	context.title = _("Partners")
	context.description = _("LabQubit technology partnerships and certifications.")
	context.partners = published(
		"LQ Partner",
		fields=[*PARTNER_FIELDS, "description", "description_ar"],
		order_by="display_order asc, partner_name asc",
	)
	context.certifications = published(
		"LQ Certification",
		fields=["title", "issuer", "logo", "description", "description_ar"],
		order_by="display_order asc",
	)
