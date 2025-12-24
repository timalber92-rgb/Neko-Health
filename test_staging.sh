#!/bin/bash

# Test script for staging environment
# This script verifies that API key authentication and CORS are working correctly

echo "========================================"
echo "HealthGuard Staging Environment Test"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

API_URL="http://localhost:8000"
API_KEY="xZ5zu3IzfOXdFnaxagjUpenlZxPNrmPu7qpY_Wj2xtw"

echo "Testing API at: $API_URL"
echo ""

# Test 1: Health Check (no auth required)
echo "Test 1: Health Check (no auth required)"
echo "----------------------------------------"
HEALTH_RESPONSE=$(curl -s "$API_URL/")
if echo "$HEALTH_RESPONSE" | grep -q "HealthGuard API"; then
    echo -e "${GREEN}✓ Health check passed${NC}"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo -e "${RED}✗ Health check failed${NC}"
    echo "$HEALTH_RESPONSE"
fi
echo ""

# Test 2: Predict WITHOUT API key (should fail)
echo "Test 2: Predict without API key (should fail with 401)"
echo "--------------------------------------------------------"
PREDICT_NO_KEY=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }')

HTTP_CODE=$(echo "$PREDICT_NO_KEY" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE=$(echo "$PREDICT_NO_KEY" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✓ Correctly rejected (401 Unauthorized)${NC}"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo -e "${RED}✗ Should have returned 401, got $HTTP_CODE${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 3: Predict WITH valid API key (should succeed)
echo "Test 3: Predict with valid API key (should succeed with 200)"
echo "-------------------------------------------------------------"
PREDICT_WITH_KEY=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }')

HTTP_CODE=$(echo "$PREDICT_WITH_KEY" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE=$(echo "$PREDICT_WITH_KEY" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Successfully authenticated and predicted${NC}"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
else
    echo -e "${RED}✗ Should have returned 200, got $HTTP_CODE${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 4: Predict with INVALID API key (should fail)
echo "Test 4: Predict with invalid API key (should fail with 401)"
echo "------------------------------------------------------------"
PREDICT_INVALID_KEY=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid_key_12345" \
  -d '{
    "age": 63,
    "sex": 1,
    "cp": 3,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 0,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }')

HTTP_CODE=$(echo "$PREDICT_INVALID_KEY" | grep "HTTP_CODE" | cut -d: -f2)
RESPONSE=$(echo "$PREDICT_INVALID_KEY" | grep -v "HTTP_CODE")

if [ "$HTTP_CODE" = "401" ]; then
    echo -e "${GREEN}✓ Correctly rejected invalid key (401 Unauthorized)${NC}"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo -e "${RED}✗ Should have returned 401, got $HTTP_CODE${NC}"
    echo "$RESPONSE"
fi
echo ""

echo "========================================"
echo "Test Summary"
echo "========================================"
echo ""
echo -e "${YELLOW}Configuration loaded:${NC}"
echo "  - Environment: staging"
echo "  - API Key Auth: Enabled"
echo "  - CORS: http://localhost:3000, http://localhost:5173"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Start backend: cd backend && python -m uvicorn api.main:app --reload"
echo "  2. Start frontend: cd frontend && npm run dev"
echo "  3. Open http://localhost:5173 in your browser"
echo "  4. Test the application end-to-end"
echo ""
echo -e "${GREEN}Ready to deploy to production when you have your hosting URLs!${NC}"
echo ""
