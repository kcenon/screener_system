# SSL/TLS Certificate Setup

This directory contains SSL certificate files and provisioning scripts for the Stock Screening Platform.

## Quick Start

### Development (Self-Signed Certificate)

```bash
# Generate self-signed certificate for localhost
./generate-self-signed.sh

# Or specify a custom domain
./generate-self-signed.sh screener.local
```

Then start the stack:

```bash
docker compose --profile frontend up -d
```

Access the application at `https://localhost` (browser will show a security warning for self-signed certs).

**To trust the certificate on macOS:**

```bash
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain cert.pem
```

### Production (Let's Encrypt)

**Prerequisites:**
- Domain DNS pointing to your server
- Ports 80 and 443 accessible from the internet

```bash
# Initialize Let's Encrypt certificate
./init-letsencrypt.sh screener.example.com admin@example.com
```

After certificate issuance, update `conf.d/default.conf` to use Let's Encrypt paths:

```nginx
ssl_certificate /etc/nginx/ssl/letsencrypt/live/screener.example.com/fullchain.pem;
ssl_certificate_key /etc/nginx/ssl/letsencrypt/live/screener.example.com/privkey.pem;
```

Then start with the production profile for auto-renewal:

```bash
docker compose --profile frontend --profile production up -d
```

## Files

| File | Purpose |
|------|---------|
| `generate-self-signed.sh` | Generate self-signed certificates for development |
| `init-letsencrypt.sh` | Initialize Let's Encrypt certificates for production |
| `cert.pem` | SSL certificate (git-ignored) |
| `key.pem` | SSL private key (git-ignored) |

## Environment Variables

Set these in your `.env` file for production:

```bash
# CORS must include HTTPS URLs
CORS_ORIGINS=https://screener.example.com

# OAuth callback URLs must use HTTPS
GOOGLE_REDIRECT_URI=https://screener.example.com/api/v1/oauth/google/callback
KAKAO_REDIRECT_URI=https://screener.example.com/api/v1/oauth/kakao/callback
NAVER_REDIRECT_URI=https://screener.example.com/api/v1/oauth/naver/callback
OAUTH_FRONTEND_CALLBACK_URL=https://screener.example.com/auth/callback

# Frontend must use HTTPS/WSS
VITE_API_BASE_URL=https://screener.example.com/api/v1
VITE_WS_URL=wss://screener.example.com/ws
```

## Certificate Renewal

The certbot container (production profile) automatically renews certificates every 12 hours. After renewal, reload Nginx:

```bash
docker compose --profile frontend exec nginx nginx -s reload
```

## Security Notes

- Private keys (`key.pem`) are git-ignored and should never be committed
- Self-signed certificates are for development only
- Production must use certificates from a trusted CA (e.g., Let's Encrypt)
- HSTS header is configured in Nginx with `max-age=31536000` (1 year)
