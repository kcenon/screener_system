---
id: getting-started
title: Getting Started
description: Quick start guide for the Stock Screening Platform
sidebar_label: Overview
sidebar_position: 1
tags:
  - getting-started
  - installation
  - quick-start
---

# Getting Started

Welcome to the Stock Screening Platform! This guide will help you get up and running quickly.

## Quick Start

The fastest way to start is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/kcenon/screener_system.git
cd screener_system

# Copy environment variables
cp .env.example .env

# Start all services
docker-compose up -d

# Check service health
docker-compose ps
```

Access the application:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Airflow UI**: http://localhost:8080

## What's Next?

- [Installation Guide](./installation.md) - Detailed setup instructions
- [Architecture Overview](./architecture-overview.md) - Understand the system
- [Project Structure](./project-structure.md) - Navigate the codebase

## Need Help?

- Check the [User Guides](../02-guides/user/screening.md)
- Read the [API Reference](../03-api-reference/intro.md)
- See [Troubleshooting](../06-operations/troubleshooting.md)
