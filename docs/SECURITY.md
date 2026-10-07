# Security model

## Guest-accessible endpoints

Only two methods accept anonymous requests. Both live in `labqubit/api/leads.py`:

| Method | Purpose | Protections |
|---|---|---|
| `submit_enquiry` | Contact, quote and consultation forms → LQ Lead | POST only, 8/hour per IP, field allowlist, length/choice/link validation, honeypot, minimum time on page, optional Turnstile, internal fields set server-side |
| `submit_application` | Job applications → LQ Job Application | POST only, 5/hour per IP, same validation, CV checked by extension, file signature and size (5 MB), random file name, private storage, PDFs with JavaScript rejected |

Neither response contains a document name, so records can't be enumerated. Bots get a fake
success and nothing is saved.

`labqubit.api.preferences.set_language` is POST-only and only changes the caller's own language.

## Client portal

- A **portal user** is a *Website User* with the `LQ Client` role, listed on exactly one
  LQ Client. The role has no Desk access (enforced on every migrate) and lands on `/portal`.
- **Row-level security** (`labqubit/permissions.py`, wired in `hooks.py`):
  - `permission_query_conditions` restrict every list query to the user's client.
  - `has_permission` checks every single-document read.

  Both apply to the portal pages, the REST API (`/api/resource/...`), reports and private file
  downloads, since a File is only downloadable if the user can read its parent document.
- **Read-only role:** portal users can only read. Ticket creation, replies and resolve/reopen go
  through `labqubit/api/portal.py`, which:
  - checks the ticket belongs to the user's client;
  - sets internal fields on the server;
  - validates attachments (type, signature, size, count);
  - rate-limits per user.
- **Internal fields** use permission level 1, which portal users can't read: ticket resolution
  notes, client, asset and document notes, management IPs, reminder flags.
- **Documents:** only those with *Visible in Client Portal* ticked are shown.
- **Private files:** contracts, CVs, client documents and ticket attachments are always moved to
  private storage (`labqubit/utils/files.py`).
- **No caching:** portal pages are `no_cache`, so personal data is never stored in the page cache.

This is verified by `labqubit/tests/test_portal_permissions.py`, and was also checked manually
over HTTP:

- another client's pages return 404, its REST records 403 and its files 403;
- internal fields are absent from API responses;
- direct REST writes are refused.

## Accounts

- **Public signup is disabled.** Staff create portal users from the LQ Client form
  ("Create Portal User").
- **Install-time defaults:** password policy on (minimum score 3), 5 failed logins lock the
  account for 5 minutes, sessions are logged out on password reset, guests can't upload files.
- **Two-factor authentication:** Frappe supports it (System Settings → Enable Two Factor Auth),
  and the login page handles the verification step. Enable it for staff.

## Transport and headers

- **HTTPS:** Caddy terminates HTTPS with automatic Let's Encrypt certificates (`compose.prod.yml`).
- **Security headers:** frappe_docker's nginx adds HSTS, `X-Frame-Options: SAMEORIGIN`,
  `X-Content-Type-Options: nosniff` and `Referrer-Policy`. Caddy adds `Permissions-Policy` and
  removes the `Server` header.
- **Client IPs:** real client IPs are trusted only from the internal Docker subnet, so per-IP
  rate limits and logs see visitors, not the proxy.

## Templates

Frappe renders Jinja **without auto-escaping**. All database values in LabQubit templates are
escaped with `| e`. Rich-text fields edited in Desk are output as HTML; Frappe sanitizes them
on save. JSON-LD uses `json_script`, which escapes `<`, `>` and `&`.

## Known limitations / follow-ups

- **No Content-Security-Policy yet.** Pages use small inline scripts (theme, forms), so a strict
  CSP needs nonces. A good hardening step after launch.
- **SLA timers count calendar hours (24x7).** Business-hours calendars are a possible extension.
- **Error tracebacks:** a REST read of another client's record returns 403 rather than 404. Names
  are sequential and reveal nothing else. Tracebacks are shown only in developer mode, which must
  be off in production.
