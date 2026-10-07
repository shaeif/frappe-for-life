# LabQubit data model

All DocTypes are prefixed `LQ`. This avoids clashes with ERPNext, HRMS and Frappe CRM
(`Lead`, `Job Opening`, `Support`…), so ERPNext can be installed later without renaming
anything. Public URLs come from each record's `route`, so the prefix never appears on the site.

## Modules

| Module | DocTypes |
|---|---|
| LQ Website | Service, Solution, Industry, Case Study, Partner, Testimonial, Certification, **LQ Settings** (single) |
| LQ Sales | Lead |
| LQ Service Desk | Client, Client Asset, AMC Contract, Support Ticket, SLA Policy, Client Document |
| LQ Careers | Job Opening, Job Application |

Child tables: Feature Item, Metric, Service/Industry/Solution/Partner Link (multi-select), Client User,
AMC Asset, SLA Target, Ticket Reply.

## Public pages (has_web_view)

| DocType | Route | Published when |
|---|---|---|
| LQ Service | `/services/<slug>` | `published` is ticked |
| LQ Solution | `/solutions/<slug>` | `published` |
| LQ Industry | `/industries/<slug>` | `published` |
| LQ Case Study | `/case-studies/<slug>` | `published` |
| LQ Job Opening | `/careers/<slug>` | `published` |

Record name = title, so Desk links are readable. The slug is generated from the title on first
publish and can be edited. Every content DocType has `_ar` fields for Arabic, and pages fall back
to English when an Arabic field is empty.

## Naming

| DocType | Pattern | Example |
|---|---|---|
| LQ Lead | `LEAD-.YYYY.-.#####` | LEAD-2026-00042 |
| LQ Support Ticket | `TKT-.YYYY.-.#####` | TKT-2026-00107 |
| LQ AMC Contract | `AMC-.YYYY.-.####` | AMC-2026-0012 |
| LQ Client Asset | `ASSET-.#####` | ASSET-00311 |
| LQ Client Document | `DOC-.YYYY.-.#####` | DOC-2026-00090 |
| LQ Job Application | `APP-.YYYY.-.#####` | APP-2026-00015 |
| LQ Testimonial | `TST-.####` | TST-0003 |
| Others | by title / name field | |

## Key rules (enforced in controllers)

- **Lead:** email is normalized; `closed_on` is set when the status becomes Won or Lost.
- **Client:** a portal user belongs to exactly one client. Saving a client gives its portal users
  the `LQ Client` role.
- **Asset:** serial numbers are unique per client; warranty expiry cannot be before installation.
- **AMC Contract:**
  - The end date must be after the start date, and covered assets must belong to the same client.
  - The status is derived from the dates: Active → Expiring Soon (inside the reminder window) →
    Expired. Draft and Cancelled are set manually.
  - Assets point to the contract while it is in force.
  - **Create Renewal** makes a Draft for the next term; the current contract stays in force
    until its end date.
  - The SLA policy defaults to the client's policy, otherwise to the policy named like the
    coverage level.
- **SLA Policy:** exactly one target per priority, and only one default policy.
- **Ticket:** the asset and contract must belong to the ticket's client; the contract is filled in
  from the asset.
- **Client Document / AMC contract file / CV uploads:** always moved to **private** storage, so
  only users allowed to read the record can download them.

## Roles

| Role | Desk | Purpose |
|---|---|---|
| LQ Content Editor | yes | website content |
| LQ Sales User / Manager | yes | leads (managers can delete and export) |
| LQ Support Agent / Manager | yes | tickets, assets, contracts |
| LQ HR User | yes | job openings and applications |
| LQ Client | **no** | portal users; lands on `/portal` after login |

Roles are created by `labqubit/install.py` on install and re-checked after every migrate. Default SLA
policies (Standard, Premium) are seeded on install.
