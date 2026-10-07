# LabQubit production image.
# Based on frappe_docker's layered image, but installs the app from this checkout
# instead of cloning it, so the image always matches the code being built.
#
# Build from the repo root:  docker compose build

ARG FRAPPE_BRANCH=version-15

FROM frappe/build:${FRAPPE_BRANCH} AS builder

ARG FRAPPE_BRANCH=version-15
ARG FRAPPE_PATH=https://github.com/frappe/frappe

USER frappe

RUN bench init \
	--frappe-branch=${FRAPPE_BRANCH} \
	--frappe-path=${FRAPPE_PATH} \
	--no-procfile \
	--no-backups \
	--skip-redis-config-generation \
	--verbose \
	/home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench

# Node deps first so they stay cached while only app code changes
COPY --chown=frappe:0 package.json yarn.lock apps/labqubit/
RUN cd apps/labqubit && yarn install --frozen-lockfile

COPY --chown=frappe:0 . apps/labqubit/

# `bench build` also runs the app's `yarn build` (Tailwind)
RUN ./env/bin/pip install --no-cache-dir -e apps/labqubit \
	&& ls -1 apps > sites/apps.txt \
	&& bench build --app labqubit \
	&& test -s apps/labqubit/labqubit/public/css/labqubit.css \
	&& echo "{}" > sites/common_site_config.json \
	&& find apps -mindepth 1 -path "*/.git" | xargs rm -fr

FROM frappe/base:${FRAPPE_BRANCH} AS backend

USER frappe

COPY --from=builder --chown=frappe:0 /home/frappe/frappe-bench /home/frappe/frappe-bench
RUN chmod -R g=u /home/frappe/frappe-bench

WORKDIR /home/frappe/frappe-bench

# Keep built assets in the image; the entrypoint links them into the sites volume,
# so a rebuilt image never serves stale CSS/JS from an old volume.
RUN cp -r sites/assets assets && rm -rf sites/assets

VOLUME [ \
	"/home/frappe/frappe-bench/sites", \
	"/home/frappe/frappe-bench/logs" \
]

USER root
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY docker/start.sh /usr/local/bin/start.sh
RUN chmod 755 /usr/local/bin/entrypoint.sh /usr/local/bin/start.sh

USER frappe
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["start.sh"]
