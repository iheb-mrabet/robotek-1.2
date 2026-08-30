FROM postgres:16-alpine

COPY init.sql /docker-entrypoint-initdb.d/10-robotek.sql

USER postgres

HEALTHCHECK --interval=10s --timeout=5s --retries=8 \
  CMD pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" || exit 1
