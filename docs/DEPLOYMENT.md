# Deployment

Two supported ways to run LabQubit in production. **Docker is recommended**: one command,
reproducible images, HTTPS and backups included.

## Option A: Docker (recommended)

### Server

- Ubuntu 22.04/24.04, 2 vCPU / 4 GB RAM minimum (4 vCPU / 8 GB comfortable), 40 GB disk
- Docker Engine 24+ with the Compose v2 plugin
- DNS: `A` records for `labqubit.com` and `www.labqubit.com` pointing at the server
- Firewall: allow 22, 80, 443 only

### First deploy

```bash
git clone https://github.com/shaeif/frappe-for-life.git labqubit && cd labqubit
cp .env.example .env
```

Edit `.env`:

```bash
SITE_NAME=labqubit.com          # must equal DOMAIN
DOMAIN=labqubit.com
LETSENCRYPT_EMAIL=it@labqubit.com
ADMIN_PASSWORD=<long random>
DB_ROOT_PASSWORD=<long random>
SEED_DEMO=1                     # starter content; set 0 to start empty
```

Then:

```bash
docker compose -f compose.yml -f compose.prod.yml build
docker compose -f compose.yml -f compose.prod.yml up -d
docker compose logs -f create-site      # wait until it exits
```

Open `https://labqubit.com/app`, sign in as `Administrator`, and complete the setup wizard
(language, time zone, currency). Then continue with [ADMIN_GUIDE.md](ADMIN_GUIDE.md).

### What runs

| Service | Role |
|---|---|
| `caddy` | HTTPS (Let's Encrypt), compression, asset cache headers, ports 80/443 |
| `frontend` | nginx: static assets, proxy to backend/websocket, security headers |
| `backend` | gunicorn running Frappe |
| `websocket` | realtime updates (Socket.IO) |
| `queue-short`, `queue-long` | background jobs (emails, notifications) |
| `scheduler` | SLA checks every 15 minutes, daily AMC renewals, email sending |
| `db` | MariaDB 10.11 (utf8mb4) |
| `redis-cache`, `redis-queue` | cache and job queue |
| `backup` | daily backups, optional off-site copy with restic |

### Updating

```bash
git pull
docker compose -f compose.yml -f compose.prod.yml build
docker compose -f compose.yml -f compose.prod.yml up -d   # create-site runs `migrate`
```

### Backups and restore

- Daily: `bench --site all backup --with-files` writes to `sites/<site>/private/backups`
  (inside the `sites` volume). Backups older than `BACKUP_RETENTION_DAYS` (default 14) are deleted.
- Off-site: set `RESTIC_REPOSITORY` and `RESTIC_PASSWORD` (plus storage credentials) in `.env`.
  Keeps 7 daily, 4 weekly and 6 monthly snapshots.
- Manual backup now: `docker compose exec backend bench --site labqubit.com backup --with-files`

Restore into a running stack:

```bash
docker compose cp ./backup/ backend:/tmp/restore/
docker compose exec backend bench --site labqubit.com restore /tmp/restore/<db>.sql.gz \
  --with-public-files /tmp/restore/<files>.tar --with-private-files /tmp/restore/<private-files>.tar \
  --db-root-password "$DB_ROOT_PASSWORD"
docker compose exec backend bench --site labqubit.com migrate
```

**Test a restore at least once before launch.**

## Option B: bench on a VPS (no Docker)

Follow the development setup in the README up to step 5 on the server, using a dedicated
`frappe` user and the real domain as the site name. Then:

```bash
bench get-app https://github.com/shaeif/frappe-for-life.git --branch main
bench new-site labqubit.com --install-app labqubit
bench --site labqubit.com execute labqubit.setup.demo.create_demo_content   # optional
bench --site labqubit.com set-config host_name https://labqubit.com
bench build --app labqubit

sudo bench setup production frappe          # supervisor + nginx
bench config dns_multitenant on
sudo bench setup lets-encrypt labqubit.com  # HTTPS, auto-renewing
bench --site labqubit.com enable-scheduler
```

Backups: Frappe runs scheduled backups (System Settings → Backups). For off-site copies,
sync `sites/labqubit.com/private/backups` with restic or rclone from cron.

Updating: `bench update --pull --patch --build --requirements` (take a backup first).

## Go-live checklist

- [ ] `developer_mode` and `allow_tests` are **not** set in `site_config.json`
- [ ] Setup wizard completed; time zone correct
- [ ] Outgoing Email Account configured and a test email received (Desk → Email Account)
- [ ] LQ Settings filled: contact details, social links, notification emails, hero text, stats
- [ ] Sample records reviewed: replaced with real content or left unpublished
- [ ] Partner logos uploaded from the vendors' partner portals; partnerships verified
- [ ] Testimonials and case studies approved in writing by the clients
- [ ] Privacy policy reviewed by your legal advisor
- [ ] Staff users created with the right roles; Administrator password stored safely
- [ ] 2FA enabled for staff (System Settings → Enable Two Factor Auth)
- [ ] Turnstile keys added (optional but recommended once forms get traffic)
- [ ] Backup restore tested; off-site backup configured
- [ ] Search Console: verify the domain, submit `/sitemap.xml`
