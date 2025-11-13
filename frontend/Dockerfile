# ============================================================================
# Stock Screening Platform - Frontend Dockerfile (Production)
# ============================================================================

ARG NODE_VERSION=20

# ============================================================================
# STAGE 1: Base Image
# ============================================================================

FROM node:${NODE_VERSION}-alpine AS base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git

# ============================================================================
# STAGE 2: Dependencies
# ============================================================================

FROM base AS dependencies

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm ci --only=development

# ============================================================================
# STAGE 3: Builder
# ============================================================================

FROM dependencies AS builder

# Copy application code
COPY . .

# Build application
RUN npm run build

# ============================================================================
# STAGE 4: Production
# ============================================================================

FROM nginx:alpine AS production

# Copy nginx configuration
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Add healthcheck script
RUN echo '#!/bin/sh' > /healthcheck.sh && \
    echo 'wget --no-verbose --tries=1 --spider http://localhost:80/index.html || exit 1' >> /healthcheck.sh && \
    chmod +x /healthcheck.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD /healthcheck.sh

# Expose HTTP port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
