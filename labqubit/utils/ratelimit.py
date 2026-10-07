from functools import wraps

import frappe
from frappe import _


def per_user(limit: int, seconds: int):
	"""Limit calls per logged-in user (Frappe's rate_limit is per IP, which would let one
	office behind NAT block itself)."""

	def decorator(fn):
		@wraps(fn)
		def wrapper(*args, **kwargs):
			# make_key adds the site prefix, so sites on one Redis never share counters
			key = frappe.cache.make_key(f"labqubit:rl:{fn.__module__}.{fn.__name__}:{frappe.session.user}")
			count = frappe.cache.incrby(key, 1)
			if count == 1:
				frappe.cache.expire(key, seconds)
			if count > limit:
				frappe.local.response.http_status_code = 429
				frappe.throw(_("Too many requests. Please try again later."), frappe.RateLimitExceededError)
			return fn(*args, **kwargs)

		return wrapper

	return decorator
