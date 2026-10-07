import os
import unittest

import frappe

from labqubit.utils.jinja import asset_url


class TestAssetUrl(unittest.TestCase):
	def test_existing_file_gets_version_hash(self):
		path = frappe.get_app_path("labqubit", "public", "css", "_test_asset.css")
		with open(path, "w") as f:
			f.write("body{}")

		try:
			url = asset_url("css/_test_asset.css")
			self.assertTrue(url.startswith("/assets/labqubit/css/_test_asset.css?v="))

			with open(path, "w") as f:
				f.write("body{color:red}")
			os.utime(path, (0, 1))  # force a different mtime
			self.assertNotEqual(url, asset_url("css/_test_asset.css"))
		finally:
			os.remove(path)

	def test_missing_file_has_no_version(self):
		self.assertEqual(asset_url("css/does-not-exist.css"), "/assets/labqubit/css/does-not-exist.css")

	def test_path_traversal_is_rejected(self):
		with self.assertRaises(ValueError):
			asset_url("../hooks.py")
