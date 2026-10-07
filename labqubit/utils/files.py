import frappe


def make_attachments_private(doc, *fieldnames):
	"""Move public uploads in the given Attach fields to private storage.

	Private files are only downloadable by users who can read the attached document,
	so contracts, CVs, invoices and reports never end up at a guessable public URL.
	"""
	for fieldname in fieldnames:
		file_url = doc.get(fieldname)
		if not file_url or not file_url.startswith("/files/"):
			continue

		file_name = frappe.db.get_value(
			"File",
			{"file_url": file_url, "is_private": 0},
			"name",
			order_by="creation desc",
		)
		if not file_name:
			continue

		file_doc = frappe.get_doc("File", file_name)
		if not file_doc.attached_to_doctype:
			file_doc.attached_to_doctype = doc.doctype
			file_doc.attached_to_name = doc.name
			file_doc.attached_to_field = fieldname
		file_doc.is_private = 1
		file_doc.save(ignore_permissions=True)
		doc.set(fieldname, file_doc.file_url)
		frappe.db.set_value(doc.doctype, doc.name, fieldname, file_doc.file_url, update_modified=False)
