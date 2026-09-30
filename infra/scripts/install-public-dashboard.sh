#!/usr/bin/env bash
set -Eeuo pipefail

: "${PUBLIC_DASHBOARD_HOST:=}"

if [[ -z "${PUBLIC_DASHBOARD_HOST}" ]]; then
  echo "Permanent public dashboard is disabled."
  exit 0
fi

: "${CADDY_VERSION:=v2.11.4}"
: "${CADDY_SHA512:?CADDY_SHA512 is required when the public dashboard is enabled.}"

version="${CADDY_VERSION#v}"
asset="caddy_${version}_linux_amd64.tar.gz"
release_url="https://github.com/caddyserver/caddy/releases/download/${CADDY_VERSION}"
work_dir="$(mktemp -d)"
trap 'rm -rf "${work_dir}"' EXIT

curl --fail --location --silent --show-error \
  --proto '=https' --tlsv1.2 \
  --retry 5 --retry-all-errors \
  "${release_url}/${asset}" \
  --output "${work_dir}/${asset}"

echo "${CADDY_SHA512}  ${work_dir}/${asset}" | sha512sum --check
tar -xzf "${work_dir}/${asset}" -C "${work_dir}" caddy
install -m 0755 "${work_dir}/caddy" /usr/local/bin/caddy

if ! id -u caddy >/dev/null 2>&1; then
  useradd \
    --system \
    --home /var/lib/caddy \
    --create-home \
    --shell /usr/sbin/nologin \
    caddy
fi

install -d -o caddy -g caddy /etc/caddy /var/lib/caddy /var/log/caddy

cat > /etc/caddy/Caddyfile <<EOF
{
    auto_https disable_redirects
}

${PUBLIC_DASHBOARD_HOST} {
    encode zstd gzip

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "SAMEORIGIN"
        Referrer-Policy "strict-origin-when-cross-origin"
    }

    reverse_proxy 127.0.0.1:30080 {
        health_uri /health
        health_interval 30s
        health_timeout 5s
    }
}
EOF

/usr/local/bin/caddy fmt --overwrite /etc/caddy/Caddyfile
/usr/local/bin/caddy validate --config /etc/caddy/Caddyfile

cat > /etc/systemd/system/caddy.service <<'EOF'
[Unit]
Description=Robotek HTTPS reverse proxy
Documentation=https://caddyserver.com/docs/
After=network-online.target k3s.service
Wants=network-online.target

[Service]
Type=notify
User=caddy
Group=caddy
Environment=XDG_DATA_HOME=/var/lib/caddy
Environment=XDG_CONFIG_HOME=/var/lib/caddy
ExecStart=/usr/local/bin/caddy run --environ --config /etc/caddy/Caddyfile
ExecReload=/usr/local/bin/caddy reload --config /etc/caddy/Caddyfile --force
TimeoutStopSec=5s
LimitNOFILE=1048576
PrivateTmp=true
ProtectSystem=full
ReadWritePaths=/var/lib/caddy /var/log/caddy
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
EOF

printf 'https://%s\n' "${PUBLIC_DASHBOARD_HOST}" \
  > /etc/robotek/public-dashboard-url
chmod 0644 /etc/robotek/public-dashboard-url

systemctl daemon-reload
systemctl enable caddy
systemctl restart caddy

echo "Permanent Robotek dashboard: https://${PUBLIC_DASHBOARD_HOST}"
