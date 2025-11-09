#!/bin/bash
set -e

echo "🚀 Starting comprehensive testing..."
echo ""

echo "1️⃣ Building services..."
docker-compose build
echo ""

echo "2️⃣ Starting services..."
docker-compose up -d
echo ""

echo "3️⃣ Waiting for services to be healthy..."
echo "   (This may take 30-60 seconds...)"
sleep 30
echo ""

echo "4️⃣ Testing PostgreSQL..."
docker-compose exec -T postgres psql -U screener_user -d screener_db -c "SELECT 1;" > /dev/null
echo "   ✅ PostgreSQL OK"
echo ""

echo "5️⃣ Testing Redis..."
docker-compose exec -T redis redis-cli -a redis_password ping > /dev/null 2>&1
echo "   ✅ Redis OK"
echo ""

echo "6️⃣ Testing Backend Health..."
response=$(curl -s -f http://localhost:8000/health)
echo "   ✅ Backend Health OK"
echo "   Response: $response"
echo ""

echo "7️⃣ Testing Backend DB Health..."
response=$(curl -s -f http://localhost:8000/health/db)
echo "   ✅ Backend DB Connection OK"
echo "   Response: $response"
echo ""

echo "8️⃣ Testing Backend Redis Health..."
response=$(curl -s -f http://localhost:8000/health/redis)
echo "   ✅ Backend Redis Connection OK"
echo "   Response: $response"
echo ""

echo "9️⃣ Testing Rate Limiting..."
count=0
for i in {1..105}; do
  response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
  if [ "$response" == "429" ]; then
    count=$i
    break
  fi
done

if [ $count -gt 0 ]; then
  echo "   ✅ Rate Limiting OK (hit limit at request $count)"
else
  echo "   ⚠️  Rate Limiting Warning (did not hit limit in 105 requests)"
fi
echo ""

echo "🔟 Testing Request Logging..."
curl -s http://localhost:8000/ > /dev/null
sleep 1
if docker-compose logs backend | grep -q "Request started"; then
  echo "   ✅ Request Logging OK"
else
  echo "   ⚠️  Request Logging Warning (logs not found)"
fi
echo ""

echo "1️⃣1️⃣ Testing CORS Headers..."
response=$(curl -s -v http://localhost:8000/ 2>&1 | grep -i "access-control")
if [ -n "$response" ]; then
  echo "   ✅ CORS Headers OK"
  echo "   $response"
else
  echo "   ⚠️  CORS Headers Warning (not found)"
fi
echo ""

echo "1️⃣2️⃣ Testing Rate Limit Headers..."
response=$(curl -s -v http://localhost:8000/ 2>&1 | grep -i "x-ratelimit")
if [ -n "$response" ]; then
  echo "   ✅ Rate Limit Headers OK"
  echo "   $response"
else
  echo "   ⚠️  Rate Limit Headers Warning (not found)"
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 All tests completed!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Services running at:"
echo "  - Backend API:  http://localhost:8000"
echo "  - API Docs:     http://localhost:8000/docs"
echo "  - Airflow:      http://localhost:8080 (admin/admin)"
echo "  - Frontend:     http://localhost:5173"
echo "  - Prometheus:   http://localhost:9090"
echo "  - Grafana:      http://localhost:3001 (admin/admin)"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
