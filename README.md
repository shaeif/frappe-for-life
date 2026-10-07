# LabQubit

Company website and client portal for LabQubit, built as a custom [Frappe Framework](https://frappeframework.com) v15 app.

See [docs/ROADMAP.md](docs/ROADMAP.md) for the phased plan.

## Development setup

Tested target: Ubuntu 24.04 (native or WSL2). macOS works with Homebrew equivalents.

### 1. System packages

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl build-essential python3-dev python3-venv python3-pip pipx \
  mariadb-server mariadb-client libmariadb-dev pkg-config redis-server \
  xvfb libfontconfig1 fontconfig cron
```

### 2. MariaDB: password auth for root, utf8mb4 for Arabic

```bash
sudo mariadb-secure-installation
# Switch to unix_socket authentication? -> n
# Change the root password? -> Y (bench needs it)
# Answer Y to the rest

sudo tee /etc/mysql/mariadb.conf.d/99-frappe.cnf > /dev/null <<'EOF'
[mysqld]
character-set-client-handshake = FALSE
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

[mysql]
default-character-set = utf8mb4
EOF
sudo systemctl restart mariadb
```

### 3. Node 20 + Yarn (Tailwind v4 needs Node 20 or newer)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.bashrc
nvm install 20 && nvm alias default 20
npm install -g yarn
```

### 4. wkhtmltopdf (PDF quotations and reports, needed in Phase 6; the jammy build works on 24.04)

```bash
wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-2/wkhtmltox_0.12.6.1-2.jammy_amd64.deb
sudo apt install -y ./wkhtmltox_0.12.6.1-2.jammy_amd64.deb
```

### 5. Bench, Frappe and the site

```bash
pipx install frappe-bench
pipx ensurepath && source ~/.bashrc

bench init frappe-bench --frappe-branch version-15
cd frappe-bench

bench new-site labqubit.localhost           # prompts for MariaDB root + Administrator passwords
bench --site labqubit.localhost set-config developer_mode 1
bench --site labqubit.localhost set-config allow_tests 1
bench use labqubit.localhost
```

### 6. Install this app

```bash
bench get-app https://github.com/shaeif/frappe-for-life.git --branch ccr-c556f6f6-47yonc
bench setup requirements --node             # installs Tailwind into apps/labqubit
bench --site labqubit.localhost install-app labqubit
bench build --app labqubit                  # also runs `yarn build` -> public/css/labqubit.css
bench start
```

`bench get-app` reads the app name from `pyproject.toml` and clones into `apps/labqubit`.

### Daily workflow

```bash
bench start                                 # terminal 1: web, workers, redis, socketio
cd apps/labqubit && yarn dev                # terminal 2: Tailwind watcher
```

## Tests

```bash
bench --site labqubit.localhost run-tests --app labqubit
```
