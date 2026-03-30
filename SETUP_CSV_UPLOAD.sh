#!/bin/bash

# CSV Upload System - Quick Reference & Testing Guide

echo "================================"
echo "CSV Upload Background Job Setup"
echo "================================"
echo ""

# 1. Start Docker Compose
echo "Step 1: Starting Docker Compose with all services..."
echo "Command: docker compose up --build"
echo ""
echo "This will start:"
echo "  - web       (Django API on port 8089)"
echo "  - celery    (Background worker)"
echo "  - redis     (Message broker)"
echo ""

# 2. Verify services
echo "Step 2: Verify all services are running..."
echo "Command: docker compose ps"
echo ""
echo "You should see: web, celery, redis all with status 'Up'"
echo ""

# 3. Check Celery logs
echo "Step 3: Monitor Celery processing (in another terminal)..."
echo "Command: docker compose logs -f celery"
echo ""

# 4. Upload CSV
echo "Step 4: Upload CSV file..."
echo "Command: curl -X POST \\"
echo "  -H 'Authorization: Bearer YOUR_TOKEN' \\"
echo "  -F 'file=@sample_products.csv' \\"
echo "  http://localhost:8089/api/dashboard/products/upload/csv/"
echo ""
echo "Response should be 202 Accepted with task_id"
echo ""

# 5. Check email
echo "Step 5: Check your email within 1-2 minutes..."
echo "- Subject: ✓ CSV Upload Completed Successfully"
echo "- Or: ✗ CSV Upload Failed (if errors)"
echo ""

# 6. Run Python tests
echo "Step 6: Run automated tests..."
echo "Command: python test_csv_upload_bg.py"
echo ""

# Test the upload
echo "================================"
echo "Testing CSV Upload"
echo "================================"
echo ""

# Check if sample CSV exists
if [ -f "sample_products.csv" ]; then
    echo "✓ sample_products.csv found"
    echo "  Size: $(du -h sample_products.csv | cut -f1)"
else
    echo "✗ sample_products.csv not found in current directory"
    exit 1
fi

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    echo "✗ Docker not found. Please install Docker."
    exit 1
else
    echo "✓ Docker is installed"
fi

# Check if containers are running
if docker ps | grep -q floor_bot-web; then
    echo "✓ Django web container is running"
else
    echo "✗ Django web container is not running"
    echo "  Run: docker compose up --build"
    exit 1
fi

if docker ps | grep -q floor_bot-celery; then
    echo "✓ Celery worker container is running"
else
    echo "✗ Celery worker container is not running"
    exit 1
fi

if docker ps | grep -q floor_bot-redis; then
    echo "✓ Redis container is running"
else
    echo "✗ Redis container is not running"
    exit 1
fi

echo ""
echo "================================"
echo "System Status: READY ✓"
echo "================================"
echo ""

# Quick API test
echo "Testing API endpoint..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X OPTIONS http://localhost:8089/api/dashboard/products/upload/csv/)
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 405 ] || [ "$HTTP_CODE" -eq 401 ]; then
    echo "✓ API endpoint is reachable (HTTP $HTTP_CODE)"
else
    echo "✗ API endpoint returned HTTP $HTTP_CODE"
fi

echo ""
echo "================================"
echo "Quick Commands Reference"
echo "================================"
echo ""
echo "Upload CSV (with token):"
echo "  curl -X POST -H 'Authorization: Bearer TOKEN' -F 'file=@sample_products.csv' http://localhost:8089/api/dashboard/products/upload/csv/"
echo ""
echo "View Celery logs:"
echo "  docker compose logs -f celery"
echo ""
echo "View all logs:"
echo "  docker compose logs -f"
echo ""
echo "Container status:"
echo "  docker compose ps"
echo ""
echo "Stop all services:"
echo "  docker compose down"
echo ""
echo "Restart services:"
echo "  docker compose restart"
echo ""

echo "================================"
echo "Documentation Files"
echo "================================"
echo ""
echo "1. CSV_UPLOAD_BACKGROUND_GUIDE.md"
echo "   - Full API documentation"
echo "   - Usage examples"
echo "   - Troubleshooting"
echo ""
echo "2. CSV_UPLOAD_IMPLEMENTATION.md"
echo "   - Implementation details"
echo "   - Architecture overview"
echo "   - Feature list"
echo ""
echo "3. dashboard/tasks.py"
echo "   - Celery task implementation"
echo "   - Email notification code"
echo ""
echo "4. test_csv_upload_bg.py"
echo "   - Automated tests"
echo "   - Run with: python test_csv_upload_bg.py"
echo ""

echo "Ready to upload CSV files! 🚀"
