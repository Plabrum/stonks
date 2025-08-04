#!/bin/bash
set -e

SERVICE_NAME="webhook"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USER="$(whoami)"

if [ -z "$WORKDIR" ]; then
  echo "Error: WORKDIR environment variable is not set."
  echo "Please set WORKDIR before running this script."
  exit 1
fi

EXEC_START="/usr/bin/python3 ${WORKDIR}/scripts/deploy_webhook_listener.py"

# You can adjust these variables above if needed

echo "Creating systemd service file at ${SERVICE_FILE}..."

sudo tee "${SERVICE_FILE}" >/dev/null <<EOF
[Unit]
Description=GitHub Webhook Listener
After=network.target

[Service]
User=${USER}
WorkingDirectory=${WORKDIR}
ExecStart=${EXEC_START}
Restart=always
RestartSec=5
Environment=FLASK_ENV=production
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=${SERVICE_NAME}

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling and starting ${SERVICE_NAME} service..."
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl restart "${SERVICE_NAME}.service"

echo "Service status:"
sudo systemctl status "${SERVICE_NAME}.service" --no-pager
