#!/bin/bash
# Comprehensive endpoint testing script

BASE_URL="http://localhost:8001/api"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}     Organization Contributions API - Endpoint Testing      ${NC}"
echo -e "${BLUE}============================================================${NC}\n"

# Step 1: Get tokens
echo -e "${BLUE}Step 1: Authentication - Getting Tokens${NC}\n"

echo -e "${YELLOW}Getting CEO token...${NC}"
CEO_TOKEN=$(curl -s -X POST "$BASE_URL/token/" \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "CEO001"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access'])" 2>/dev/null)
if [ -n "$CEO_TOKEN" ]; then
  echo -e "${GREEN}✓ CEO token obtained${NC}"
else
  echo -e "${RED}✗ Failed to get CEO token${NC}"
  exit 1
fi

echo -e "${YELLOW}Getting HOD token...${NC}"
HOD_TOKEN=$(curl -s -X POST "$BASE_URL/token/" \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "HOD001"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access'])" 2>/dev/null)
if [ -n "$HOD_TOKEN" ]; then
  echo -e "${GREEN}✓ HOD token obtained${NC}"
else
  echo -e "${RED}✗ Failed to get HOD token${NC}"
  exit 1
fi

echo -e "${YELLOW}Getting Pod Lead token...${NC}"
PL_TOKEN=$(curl -s -X POST "$BASE_URL/token/" \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "PL001"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access'])" 2>/dev/null)
if [ -n "$PL_TOKEN" ]; then
  echo -e "${GREEN}✓ Pod Lead token obtained${NC}"
else
  echo -e "${RED}✗ Failed to get Pod Lead token${NC}"
  exit 1
fi

echo -e "${YELLOW}Getting Employee token...${NC}"
EMP_TOKEN=$(curl -s -X POST "$BASE_URL/token/" \
  -H "Content-Type: application/json" \
  -d '{"employee_code": "EMP001"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access'])" 2>/dev/null)
if [ -n "$EMP_TOKEN" ]; then
  echo -e "${GREEN}✓ Employee token obtained${NC}"
else
  echo -e "${RED}✗ Failed to get Employee token${NC}"
  exit 1
fi

# Step 2: Seed products
echo -e "\n${BLUE}Step 2: Seeding Products${NC}"
cd /home/nikhil/Projects/Org_contributions_backend
source venv/bin/activate 2>/dev/null || true
python manage.py seed_products > /dev/null 2>&1
echo -e "${GREEN}✓ Products seeded${NC}"

# Step 3: Upload CSV file
echo -e "\n${BLUE}Step 3: File Upload${NC}"
CSV_FILE="/home/nikhil/Projects/Org_contributions_backend/organization_contributions_2025-10.csv"
if [ ! -f "$CSV_FILE" ]; then
  echo -e "${RED}✗ CSV file not found: $CSV_FILE${NC}"
  exit 1
fi

echo -e "${YELLOW}Uploading CSV file...${NC}"
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/uploads/csv/" \
  -H "Authorization: Bearer $HOD_TOKEN" \
  -F "file=@$CSV_FILE")

RAW_FILE_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data', {}).get('raw_file_id', ''))" 2>/dev/null)

if [ -n "$RAW_FILE_ID" ] && [ "$RAW_FILE_ID" != "None" ]; then
  echo -e "${GREEN}✓ File uploaded successfully! Raw File ID: $RAW_FILE_ID${NC}"
  echo "$UPLOAD_RESPONSE" | python3 -m json.tool | head -30
else
  echo -e "${RED}✗ File upload failed${NC}"
  echo "$UPLOAD_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$UPLOAD_RESPONSE"
  exit 1
fi

# Step 4: Test Entity Endpoints
echo -e "\n${BLUE}Step 4: Entity Endpoints${NC}"

echo -e "${YELLOW}GET /api/products/${NC}"
curl -s -X GET "$BASE_URL/products/" \
  -H "Authorization: Bearer $CEO_TOKEN" | python3 -m json.tool | head -20
echo ""

echo -e "${YELLOW}GET /api/features/?product_id=1${NC}"
curl -s -X GET "$BASE_URL/features/?product_id=1" \
  -H "Authorization: Bearer $CEO_TOKEN" | python3 -m json.tool | head -20
echo ""

# Step 5: Test Upload Management
if [ -n "$RAW_FILE_ID" ] && [ "$RAW_FILE_ID" != "None" ]; then
  echo -e "\n${BLUE}Step 5: Upload Management Endpoints${NC}"
  
  echo -e "${YELLOW}GET /api/uploads/$RAW_FILE_ID/${NC}"
  curl -s -X GET "$BASE_URL/uploads/$RAW_FILE_ID/" \
    -H "Authorization: Bearer $CEO_TOKEN" | python3 -m json.tool | head -20
  echo ""
fi

# Step 6: Test Dashboards
echo -e "\n${BLUE}Step 6: Dashboard Endpoints${NC}"
MONTH="2025-10"

echo -e "${YELLOW}GET /api/dashboards/org/?month=$MONTH (CEO)${NC}"
curl -s -X GET "$BASE_URL/dashboards/org/?month=$MONTH" \
  -H "Authorization: Bearer $CEO_TOKEN" | python3 -m json.tool | head -40
echo ""

echo -e "${YELLOW}GET /api/dashboards/department/1/?month=$MONTH (HOD)${NC}"
curl -s -X GET "$BASE_URL/dashboards/department/1/?month=$MONTH" \
  -H "Authorization: Bearer $HOD_TOKEN" | python3 -m json.tool | head -40
echo ""

echo -e "${YELLOW}GET /api/pods/1/contributions/?month=$MONTH (Pod Lead)${NC}"
curl -s -X GET "$BASE_URL/pods/1/contributions/?month=$MONTH" \
  -H "Authorization: Bearer $PL_TOKEN" | python3 -m json.tool | head -40
echo ""

echo -e "${YELLOW}GET /api/employees/1/contributions/?month=$MONTH (Employee)${NC}"
curl -s -X GET "$BASE_URL/employees/1/contributions/?month=$MONTH" \
  -H "Authorization: Bearer $EMP_TOKEN" | python3 -m json.tool | head -40
echo ""

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}All endpoint tests completed!${NC}"
echo -e "${GREEN}============================================================${NC}"

