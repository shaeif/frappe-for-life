"""WebP copies of public images, generated on upload and served with <picture>.

Editors can upload JPG/PNG as usual; templates call webp_url() to offer the lighter version.
"""

import os

import frappe

CONVERTIBLE = (".jpg", ".jpeg", ".png")
MAX_WIDTH = 2400
QUALITY = 82


def _public_path(file_url):
	if not file_url or not file_url.startswith("/files/") or ".." in file_url:
		return None
	return frappe.get_site_path("public", file_url.lstrip("/"))


def create_webp(doc, method=None):
	"""File after_insert hook."""
	if doc.is_private or not (doc.file_url or "").lower().endswith(CONVERTIBLE):
		return
	source = _public_path(doc.file_url)
	if not source or not os.path.exists(source):
		return
	try:
		from PIL import Image

		with Image.open(source) as img:
			if img.width > MAX_WIDTH:
				img = img.resize((MAX_WIDTH, round(img.height * MAX_WIDTH / img.width)))
			if img.mode not in ("RGB", "RGBA"):
				img = img.convert("RGBA" if "transparency" in img.info else "RGB")
			img.save(source + ".webp", "WEBP", quality=QUALITY, method=4)
	except Exception:
		frappe.log_error(title=f"WebP conversion failed for {doc.file_url}"[:140])


def delete_webp(doc, method=None):
	"""File on_trash hook."""
	source = _public_path(doc.file_url)
	if source and os.path.exists(source + ".webp"):
		os.remove(source + ".webp")


def webp_url(file_url):
	"""Jinja: URL of the WebP copy if one exists, else ''."""
	source = _public_path(file_url)
	return file_url + ".webp" if source and os.path.exists(source + ".webp") else ""
