"""Brings sites seeded before October 2026 in line with the updated positioning: the new tagline,
"experienced, qualified engineers" instead of "certified", and the network automation and web
services. Only text that still matches the original seed is changed, so edits made in Desk are kept."""

import frappe

from labqubit.install import ensure_default_records
from labqubit.setup.demo import add_new_services

NEW_SERVICES = [
	"Network Automation",
	"Website Development",
	"Web Application Development",
	"Web Application Infrastructure & Support",
]

CABLING = (
	"Certified copper and fiber cabling with full testing and as-built documentation.",
	"Copper and fiber cabling installed to standard, with full testing and as-built documentation.",
)
CABLING_AR = (
	"تمديد كابلات نحاسية وألياف ضوئية معتمدة مع اختبار كامل ووثائق تنفيذية.",
	"تمديد كابلات نحاسية وألياف ضوئية وفق المعايير مع اختبار كامل ووثائق تنفيذية.",
)

# (field, old seed text, new text)
SERVICE_TEXT = [
	("description", "Our certified engineers", "Our experienced, qualified engineers"),
	("description_ar", "مهندسونا المعتمدون", "مهندسونا ذوو الخبرة والكفاءة"),
	("short_description", *CABLING),
	("description", *CABLING),
	("short_description_ar", *CABLING_AR),
	("description_ar", *CABLING_AR),
]


def execute():
	ensure_default_records()

	for field, old, new in SERVICE_TEXT:
		for name, value in frappe.get_all(
			"LQ Service", filters={field: ["like", f"%{old}%"]}, fields=["name", field], as_list=True
		):
			frappe.db.set_value("LQ Service", name, field, value.replace(old, new), update_modified=False)

	frappe.db.sql(
		"""update `tabLQ Feature Item` set title = %s
		where title = 'Fluke-tested and certified links' and parenttype = 'LQ Service'""",
		"Every link tested, with test reports",
	)
	frappe.db.sql(
		"update `tabLQ Partner` set partnership_level = '' where partnership_level = 'Partner' and published = 0"
	)

	add_new_services(NEW_SERVICES)
