import hashlib
import os
from functools import lru_cache

import frappe


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
