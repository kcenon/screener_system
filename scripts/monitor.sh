#!/bin/bash

echo "Starting health monitor..."
echo "Press Ctrl+C to stop"
echo ""

while true; do
  clear
  echo "╔════════════════════════════════════════════════════════════╗"
  echo "║         Stock Screening Platform - Health Monitor          ║"
  echo "╚════════════════════════════════════════════════════════════╝"
  echo ""
  echo "Time: $(date '+%Y-%m-%d %H:%M:%S')"
  echo ""

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Service Status"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not running"
  echo ""

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Health Endpoints"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  # Backend Health
  echo -n "Backend API:       "
  if health=$(curl -s -f http://localhost:8000/health 2>/dev/null); then
    echo "✅ Healthy - $(echo $health | jq -r '.status' 2>/dev/null || echo 'OK')"
  else
    echo "❌ Down"
  fi

  # Database Health
  echo -n "Database:          "
  if health=$(curl -s -f http://localhost:8000/health/db 2>/dev/null); then
    echo "✅ Connected - $(echo $health | jq -r '.database' 2>/dev/null || echo 'OK')"
  else
    echo "❌ Disconnected"
  fi

  # Redis Health
  echo -n "Redis Cache:       "
  if health=$(curl -s -f http://localhost:8000/health/redis 2>/dev/null); then
    echo "✅ Connected - $(echo $health | jq -r '.redis' 2>/dev/null || echo 'OK')"
  else
    echo "❌ Disconnected"
  fi

  # Airflow Health (if available)
  echo -n "Airflow:           "
  if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Running"
  else
    echo "⚠️  Not responding"
  fi

  echo ""

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Resource Usage"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "Docker not running"
  echo ""

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "Recent Backend Logs (last 5)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  docker-compose logs --tail=5 backend 2>/dev/null || echo "Backend logs unavailable"
  echo ""

  echo "Refreshing in 5 seconds..."
  sleep 5
done
