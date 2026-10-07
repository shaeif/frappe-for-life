# LabQubit: build roadmap

The plan for the LabQubit website and client portal, built as the Frappe app `labqubit`.
Each phase starts only after the previous one is approved.

| Phase | Deliverable | Status |
|---|---|---|
| 0 | Environment, app skeleton, Tailwind pipeline, Docker | Done |
| 1 | Design system: tokens, type, components, `/styleguide` | Done |
| 2 | Data model: 27 DocTypes, roles, naming, business rules | Done |
| 3 | Public website: layout, navbar/mega menu, components, pages | Done |
| 4 | Lead capture: quote, consultation, contact, job applications | Done |
| 5 | Lead workflow, assignment, notifications, SLA, dashboards | Done |
| 6 | Client portal, row-level permissions, login restyle | Done |
| 7 | Arabic translations, SEO, performance (Lighthouse 95+) | Done |
| 8 | Tests (26), security hardening, HTTPS, backups, docs | Done |
| Next | ERPNext integration, WhatsApp notifications, AI chatbot, AMC payments | Planned |

### Next: phase 2 extras (recommendations)

- **ERPNext:** install on the same bench. Map LQ Client to Customer (`erpnext_customer`
  field is ready), generate Quotations from Proposal Sent leads, create Sales Invoices for AMC
  renewals, and attach them to the portal as LQ Client Documents automatically.
- **WhatsApp:** use Frappe's Notification channels or a provider API (e.g. Meta Cloud API) for
  ticket updates. Opt-in per client contact.
- **AI chatbot:** first-level enquiries answered from published services and case studies.
  Hand off to a human by creating an LQ Lead.
- **Payments:** online AMC renewal payments with the Frappe Payments app and a regional
  gateway. The renewal reminder links to a payment request.

## Target app structure

```
labqubit/                         repo root = apps/labqubit in the bench
├── pyproject.toml                Python package + Frappe version constraint
├── package.json, yarn.lock       Tailwind CLI (bench build runs `yarn build`)
├── styles/tailwind.css           Tailwind entry + design tokens (Phase 1)
├── docs/ROADMAP.md
└── labqubit/                     Python package
    ├── hooks.py                  how the app plugs into Frappe
    ├── modules.txt               lists the app's modules
    ├── patches.txt               data migrations
    ├── install.py                after_install: roles, default records (P2)
    ├── permissions.py            portal row-level permission rules (P6)
    ├── api/                      whitelisted endpoints, each one audited
    │   ├── leads.py              public form submissions (P4)
    │   └── portal.py             logged-in client actions (P6)
    ├── utils/
    │   ├── jinja.py              asset_url() and other template helpers
    │   └── seo.py                meta / OpenGraph / JSON-LD builders (P7)
    ├── lq_website/               module: Service, Solution, Industry, Case Study,
    │   └── doctype/…             Partner Vendor, Testimonial, Certification
    ├── lq_sales/                 module: lead / enquiry DocTypes
    ├── lq_service_desk/          module: Client, AMC Contract, Client Asset, Support Ticket
    ├── lq_careers/               module: Job Opening, Job Application
    ├── fixtures/                 exported custom fields, roles, workflow, assignment rules…
    ├── templates/
    │   ├── lq_base.html          our base layout, replaces Frappe's website base
    │   ├── includes/             navbar, mega menu, mobile drawer, footer
    │   ├── components/           Jinja macros: hero, card, cta_band, stats, testimonial, logo_strip
    │   └── pages/
    ├── www/                      static-route pages: home, about, contact, partners, careers,
    │                             portal pages under www/portal/
    ├── public/
    │   ├── css/labqubit.css      built by Tailwind (git-ignored)
    │   ├── js/site.js            small vanilla JS: navbar, theme, counters, reveal, slider
    │   ├── fonts/                self-hosted woff2 (Latin + Arabic subsets)
    │   ├── icons/                Lucide SVGs actually used
    │   └── images/               WebP
    ├── locale/ar.po              Arabic translations (P7)
    └── tests/
```

The default `LabQubit` module (`labqubit/labqubit/`) holds app-wide records such as the
Desk workspace.

## Decisions already made (and why)

- **Tailwind runs on its own CLI.** It does not go through Frappe's esbuild bundler.
  Frappe's bundler only processes `*.bundle.css` files and runs `rtlcss` on them to
  generate RTL copies. That would double-flip our logical `ms-*`/`pe-*` utilities.
  `bench build` still runs our `yarn build` automatically, because Frappe calls each
  app's `build` script.
- **Cache busting is handled by `asset_url()`.** Production nginx caches `/assets` for a
  year, so every file URL carries a content hash.
- **Module and DocType names get an `LQ` prefix**, for example `LQ Service` and
  `LQ Support Ticket`. ERPNext and HRMS already have modules and DocTypes named `Support`,
  `CRM`, `Portal`, `Job Opening` and `Lead`, so unprefixed names would collide when
  ERPNext is added later. Public URLs come from a `route` field, so the prefix never
  shows on the site. This gets confirmed in Phase 2.
- **Animations use a tiny IntersectionObserver script plus CSS** instead of AOS or GSAP:
  about 1 KB against 14–70 KB, which helps the Lighthouse target. Everything respects
  `prefers-reduced-motion`.
- **Fonts are self-hosted woff2 subsets.** There is no Google Fonts request, which is
  faster and avoids a third-party privacy issue.

## Decisions taken during the build

1. **Client entity:** `LQ Client` was added; portal users belong to exactly one client.
2. **One lead DocType:** `LQ Lead` with `lead_type` (Contact / Quote Request / Consultation).
   Three public forms feed one workflow and one dashboard.
3. **Forms:** custom Jinja forms posting to a validated, rate-limited API, instead of Frappe
   Web Forms.
4. **Blog:** Frappe's Blog Post DocType, rendered with LabQubit templates.

## Security watch-list (all addressed, see SECURITY.md)

- Every `@frappe.whitelist(allow_guest=True)` method gets an explicit field allowlist,
  type and length validation, `@rate_limit`, a honeypot, and optionally Cloudflare
  Turnstile.
- Portal reads go through `has_website_permission` and `permission_query_conditions`,
  never through client-supplied filters alone.
- Uploads are limited by extension, MIME sniffing and size, and attachments are always
  private files.
- The Desk is never reachable by the client role (`desk_access = 0`).
- `developer_mode`, `allow_tests` and server-script toggles are off in production.
