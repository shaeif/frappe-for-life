import hashlib
import os
import re
from functools import lru_cache

import frappe
from markupsafe import Markup, escape

ICON_NAME = re.compile(r"^[a-z0-9-]+$")


def asset_url(path: str) -> str:
	"""Return the public URL of a file in `labqubit/public`, with a content hash for cache busting.

	Production nginx caches /assets for a long time, so every deploy that changes a
	file must change its URL. Usage in Jinja: {{ asset_url("css/labqubit.css") }}
	"""
	public_dir = os.path.realpath(frappe.get_app_path("labqubit", "public"))
	file_path = os.path.realpath(os.path.join(public_dir, path.lstrip("/")))

	if os.path.commonpath([public_dir, file_path]) != public_dir:
		raise ValueError(f"Asset path escapes the public folder: {path}")

	url = "/assets/labqubit/" + os.path.relpath(file_path, public_dir).replace(os.sep, "/")
	if not os.path.isfile(file_path):
		return url

	return f"{url}?v={_file_digest(file_path, os.path.getmtime(file_path))}"


@lru_cache(maxsize=128)
def _file_digest(file_path: str, mtime: float) -> str:
	# mtime is part of the cache key so a rebuilt file gets a fresh digest
	with open(file_path, "rb") as f:
		return hashlib.sha256(f.read()).hexdigest()[:10]


def lq_icon(name: str, cls: str = "", label: str | None = None) -> Markup:
	"""Inline reference to an icon in the SVG sprite. Usage: {{ lq_icon("shield-check", "size-6") }}

	Named lq_icon (not icon) because page context also contains DocType fields called "icon".
	"""
	if not name or not ICON_NAME.match(name):
		return Markup("")
	a11y = f'role="img" aria-label="{escape(label)}"' if label else 'aria-hidden="true"'
	return Markup(
		f'<svg class="lq-icon {escape(cls)}" {a11y} focusable="false">'
		f'<use href="{asset_url("icons/sprite.svg")}#{name}"></use></svg>'
	)


def is_arabic() -> bool:
	return (getattr(frappe.local, "lang", None) or "en").split("-")[0] == "ar"


def t(doc, fieldname: str, default: str = ""):
	"""Pick the Arabic version of a field on Arabic pages, falling back to English.

	Works with Documents and dicts: {{ t(service, "title") }}
	"""
	if not doc:
		return default
	if is_arabic():
		value = doc.get(f"{fieldname}_ar")
		if value:
			return value
	return doc.get(fieldname) or default


def json_script(value) -> Markup:
	"""JSON that is safe inside <script> tags (escapes <, > and & so text can't close the tag)."""
	text = frappe.as_json(value, indent=None, separators=(",", ":"))
	return Markup(text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))
