# Administrator guide

Everything is managed from the Desk at `/app/labqubit`.

## First steps after install

1. **Setup wizard:** sign in as Administrator and choose language, time zone and currency.
2. **Email:** go to Desk → *Email Account* → New. Tick *Enable Outgoing* and *Default
   Outgoing*, using your mail provider's SMTP details. Notifications, form acknowledgements and
   portal invitations need it. Until it's set up, records are still saved; emails just aren't
   sent.
3. **LQ Settings** (Desk → LabQubit → Website Settings):
   - *Company:* logos (light and dark), contact email, phone, WhatsApp, address (English and
     Arabic), social links.
   - *Home page:* hero texts in both languages, and the animated stats (0 hides a stat).
   - *Leads & support:* notification emails, SLA "at risk" threshold, default SLA policy,
     Turnstile keys.
   - *SEO:* default meta description and social share image, Search Console verification code.
4. **Staff users** (Desk → User):

   | Role | Who |
   |---|---|
   | LQ Content Editor | marketing / website content |
   | LQ Sales User | salespeople; new leads are assigned round-robin among them |
   | LQ Sales Manager | can also delete, export and reopen won/lost leads |
   | LQ Support Agent | engineers; new tickets are assigned round-robin among them |
   | LQ Support Manager | full access to clients, contracts, assets, SLA policies |
   | LQ HR User | job openings and applications |

## Website content

| What | Where | Notes |
|---|---|---|
| Services | LQ Service | category, icon, short description, highlights, partners, industries, SEO |
| Solutions | LQ Solution | combines services; tagline shows in the menu |
| Industries | LQ Industry | challenges + relevant services |
| Case studies | LQ Case Study | name the client only with written permission; metrics show as tiles |
| Partners | LQ Partner | upload official logos (light and optional dark version) |
| Testimonials | LQ Testimonial | publish only with the client's written approval |
| Certifications | LQ Certification | |
| Blog | Blog Post | Markdown or rich text; categories become `/blog/<category>` |
| Careers | LQ Job Opening | applications close automatically after "Applications Close On" |

- Every content record has Arabic fields (`… (Arabic)`). Arabic pages fall back to English when
  one is empty.
- Tick **Published** to show a record and **Show on Home Page** to feature it. Use *Display
  Order* to sort.
- Upload images as JPG or PNG. A WebP copy is created automatically and served to browsers that
  support it.

**Sample content:** the starter seed publishes services, solutions and industries. Partners,
case studies, testimonials, certifications, job openings and the sample blog post are
**unpublished samples**. Replace them with real details before publishing. To preview the full
design on a test site:
`bench --site <site> execute labqubit.setup.demo.publish_samples`.

## Leads

- **How leads arrive:** website forms create **LQ Lead** records, of type Contact, Quote Request
  or Consultation.
- **Assignment:** each new lead goes to the LQ Sales User with the fewest open leads. If you
  create a Frappe *Assignment Rule* for LQ Lead, it takes over.
- **Workflow:** New → Contacted → Qualified → Proposal Sent → Won / Lost. Use the *Actions*
  button. A lost reason is required. Sales Managers can reopen.
- **Notifications:** the assigned person and the sales inbox get an email; the visitor gets an
  acknowledgement (can be switched off in LQ Settings).
- **Dashboard:** the LabQubit workspace shows new and open leads, conversion rate (last 90 days),
  leads by source, pipeline and leads per month.

## Clients, contracts and support

1. **Create the client:** add an **LQ Client** (with account manager and default SLA policy).
2. **Give portal access:** on the client, click **Create Portal User**. The contact gets an
   invitation email to set a password, then signs in at `/login` and lands on `/portal`.
3. **Register assets:** add **LQ Client Asset** records (serial numbers are unique per client).
4. **Create the contract:** create an **LQ AMC Contract**, add the covered assets, then
   **Activate**.
   - The status changes itself: Active → Expiring Soon (inside the reminder window) → Expired.
   - A renewal reminder goes to the account manager, the support inbox and the client's primary
     contact.
   - **Create Renewal** drafts the next term.
5. **Tickets:** clients raise tickets in the portal, or staff create them in Desk.
   - SLA targets come from the contract's policy, then the client's default, then the site
     default.
   - Every 15 minutes tickets are marked *At Risk* or *Breached*; a breach emails the assignees
     and the support inbox once.
   - Staff reply by adding a row to the ticket's *Replies* table; the client is emailed and sees
     it in the portal.
6. **Documents:** quotations, invoices and service reports are **LQ Client Document** records.
   Untick *Visible in Client Portal* to keep one internal.

## Translations

UI text is in `labqubit/locale/ar.po`. After changing templates:

```bash
bench generate-pot-file --app labqubit
bench update-po-files --app labqubit --locale ar   # merges new strings into ar.po
# translate the new empty msgstr entries, then:
bench build --app labqubit                          # also compiles .po -> .mo
```

Content (services, case studies…) is translated in the records' Arabic fields, not in `ar.po`.
