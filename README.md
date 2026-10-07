# LabQubit

Company website and client portal for **LabQubit**, an IT solutions provider (networks,
cybersecurity, data centers, structured cabling, managed services, cloud). Built as a custom
[Frappe Framework](https://frappeframework.com) v15 app with Tailwind CSS v4, in English and
Arabic (RTL).

| | |
|---|---|
| **Website** | home, services, solutions, industries, case studies, partners, about, careers, blog, contact; dark/light themes; Arabic RTL |
| **Lead capture** | Contact, Request a Quote, Book a Consultation and job application forms, with spam protection |
| **Desk** | lead workflow, round-robin assignment, email notifications, ticket SLA timers, AMC renewals, dashboards |
| **Client portal** | AMC contracts, covered assets, support tickets with attachments, documents; each client sees only its own data |

Docs: [Admin guide](docs/ADMIN_GUIDE.md) · [Deployment](docs/DEPLOYMENT.md) ·
[Security](docs/SECURITY.md) · [Design system](docs/DESIGN.md) ·
[Data model](docs/DATA_MODEL.md) · [Roadmap](docs/ROADMAP.md)

## Run it with Docker (quickest)

Needs Docker Engine 24+ with Compose v2 (Docker Desktop works on Windows and macOS).

```bash
git clone https://github.com/shaeif/frappe-for-life.git labqubit
cd labqubit
git checkout ccr-c556f6f6-47yonc
cp .env.example .env                 # set ADMIN_PASSWORD and DB_ROOT_PASSWORD
docker compose build                 # first build ~10 min
docker compose up -d
docker compose logs -f create-site   # returns when the site is ready (~2 min)
```

- Website: http://localhost:8080
- Desk: http://localhost:8080/app (user `Administrator`, password from `.env`). Complete the
  setup wizard on first login.
- The site starts with services, solutions and industries published. Partners, case studies,
  testimonials, certifications, jobs and a blog post are **unpublished samples**. To preview
  everything:
  `docker compose exec backend bench --site labqubit.localhost execute labqubit.setup.demo.publish_samples`

| Task | Command |
|---|---|
| Deploy new code | `git pull && docker compose build && docker compose up -d` (migrates automatically) |
| Logs | `docker compose logs -f backend` |
| Console | `docker compose exec backend bench --site labqubit.localhost console` |
| Tests | `docker compose exec backend bench --site labqubit.localhost set-config allow_tests 1` then `… run-tests --app labqubit` |
| Stop / wipe | `docker compose down` (keeps data) · `docker compose down -v` (deletes everything) |

For production (HTTPS, backups), see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Development setup (bench)

Tested on Ubuntu 24.04 (native or WSL2). The Docker image above is production-style (code
baked in); use bench for day-to-day development.

```bash
# 1. system packages
sudo apt install -y git curl build-essential python3-dev python3-venv python3-pip pipx \
  mariadb-server mariadb-client libmariadb-dev pkg-config redis-server xvfb libfontconfig1 fontconfig cron

# 2. MariaDB: password login for root, utf8mb4 for Arabic
sudo mariadb-secure-installation        # unix_socket auth -> n, set a root password
sudo tee /etc/mysql/mariadb.conf.d/99-frappe.cnf > /dev/null <<'EOF'
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
EOF
sudo systemctl restart mariadb

# 3. Node 20 + Yarn
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && source ~/.bashrc
nvm install 20 && npm install -g yarn

# 4. bench, Frappe, site, app
pipx install frappe-bench && pipx ensurepath && source ~/.bashrc
bench init frappe-bench --frappe-branch version-15 && cd frappe-bench
bench new-site labqubit.localhost
bench --site labqubit.localhost set-config developer_mode 1
bench use labqubit.localhost
bench get-app https://github.com/shaeif/frappe-for-life.git --branch ccr-c556f6f6-47yonc
bench --site labqubit.localhost install-app labqubit
bench --site labqubit.localhost execute labqubit.setup.demo.create_demo_content
bench build --app labqubit
bench start                              # http://labqubit.localhost:8000
```

While developing, run `cd apps/labqubit && yarn dev` in a second terminal (Tailwind watcher).
Developer mode makes Desk changes to LabQubit DocTypes export to the app's JSON files.

## Project layout

```
labqubit/                    repo root (apps/labqubit in a bench)
├── compose.yml, compose.prod.yml, docker/   Docker image, HTTPS proxy, backups
├── styles/tailwind.css      design tokens and component CSS (Tailwind v4)
├── scripts/vendor-assets.mjs  copies fonts, builds the icon sprite
└── labqubit/
    ├── hooks.py             how the app plugs into Frappe
    ├── install.py           roles, default SLA policies, security defaults
    ├── permissions.py       client-portal row-level security
    ├── tasks.py             SLA (every 15 min) and AMC renewal (daily) jobs
    ├── api/                 leads (public forms), portal, portal_admin, dashboard
    ├── website/             shared page context, detail pages, portal helpers
    ├── templates/           base layout, navbar, footer, Jinja components, emails
    ├── www/                 pages: home, services, …, portal/*, login, update-password
    ├── lq_website/ lq_sales/ lq_service_desk/ lq_careers/   DocTypes
    ├── locale/ar.po         Arabic translations
    ├── fixtures/            lead workflow
    └── tests/               integration tests
```

## Tests

```bash
bench --site labqubit.localhost set-config allow_tests 1
bench --site labqubit.localhost run-tests --app labqubit
```

The 26 integration tests cover portal data isolation, the public form API (validation,
field allowlist, bots), SLA calculations and the AMC contract lifecycle.
