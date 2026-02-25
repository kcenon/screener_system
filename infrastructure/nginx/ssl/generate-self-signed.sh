#!/usr/bin/env bash
# Generate self-signed SSL certificates for development/staging
#
# Usage: ./generate-self-signed.sh [domain]
# Default domain: localhost

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOMAIN="${1:-localhost}"
DAYS=365

CERT_FILE="${SCRIPT_DIR}/cert.pem"
KEY_FILE="${SCRIPT_DIR}/key.pem"

if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "Certificates already exist at ${SCRIPT_DIR}/"
    echo "  cert.pem: $(openssl x509 -in "$CERT_FILE" -noout -enddate 2>/dev/null || echo 'invalid')"
    read -r -p "Overwrite? [y/N] " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

echo "Generating self-signed certificate for: ${DOMAIN}"

openssl req -x509 -nodes -newkey rsa:2048 \
    -days "$DAYS" \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=KR/ST=Gyeonggi-do/L=Uijeongbu-si/O=Development/CN=${DOMAIN}" \
    -addext "subjectAltName=DNS:${DOMAIN},DNS:*.${DOMAIN},IP:127.0.0.1"

chmod 600 "$KEY_FILE"
chmod 644 "$CERT_FILE"

echo ""
echo "Certificates generated:"
echo "  Certificate: ${CERT_FILE}"
echo "  Private key: ${KEY_FILE}"
echo "  Domain:      ${DOMAIN}"
echo "  Valid for:   ${DAYS} days"
echo ""
echo "For browser trust, import cert.pem into your system keychain."
