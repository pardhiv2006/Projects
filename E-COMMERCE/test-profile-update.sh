#!/bin/bash

# Test Script for Profile Update and Logout
API_URL="http://localhost:5001/api"
COLORS_RESET='\033[0m'
COLORS_GREEN='\033[0;32m'
COLORS_RED='\033[0;31m'
COLORS_YELLOW='\033[1;33m'

echo -e "${COLORS_YELLOW}🧪 Profile Update & Logout Test Suite${COLORS_RESET}\n"

# 1. Login to get token
echo -e "${COLORS_YELLOW}Step 1: Login to get token${COLORS_RESET}"
# Using a known user from previous tests or creating one
USER_EMAIL="prahdiv@example.com"
LOGIN_PAYLOAD="{\"email\":\"$USER_EMAIL\",\"password\":\"password123\"}"

# First try to signup in case the user doesn't exist
curl -s -X POST $API_URL/auth/signup -H "Content-Type: application/json" -d "{\"name\":\"Pardhiv\",\"email\":\"$USER_EMAIL\",\"password\":\"password123\"}" > /dev/null

LOGIN_RESPONSE=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d "$LOGIN_PAYLOAD")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ ! -z "$TOKEN" ]; then
    echo -e "${COLORS_GREEN}✓ Login successful.${COLORS_RESET}"
else
    echo -e "${COLORS_RED}✗ Login failed.${COLORS_RESET}"
    exit 1
fi

# 2. Update Profile
echo -e "${COLORS_YELLOW}Step 2: Update Profile Details${COLORS_RESET}"
UPDATE_PAYLOAD='{
    "name": "Pardhiv Updated",
    "phone": "9876543210",
    "address": "456 New Street",
    "city": "Hyderabad",
    "zipCode": "500001"
}'

UPDATE_RESPONSE=$(curl -s -X PUT $API_URL/profile \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "$UPDATE_PAYLOAD")

if [[ $UPDATE_RESPONSE == *"9876543210"* ]] && [[ $UPDATE_RESPONSE == *"Hyderabad"* ]]; then
    echo -e "${COLORS_GREEN}✓ Profile updated successfully in response.${COLORS_RESET}"
else
    echo -e "${COLORS_RED}✗ Profile update failed in response.${COLORS_RESET}"
    echo "Response: $UPDATE_RESPONSE"
    exit 1
fi

# 3. Verify persistence
echo -e "${COLORS_YELLOW}Step 3: Verify Persistence by fetching again${COLORS_RESET}"
FETCH_RESPONSE=$(curl -s -X GET $API_URL/profile \
  -H "Authorization: Bearer $TOKEN")

if [[ $FETCH_RESPONSE == *"9876543210"* ]] && [[ $FETCH_RESPONSE == *"Hyderabad"* ]]; then
    echo -e "${COLORS_GREEN}✓ Profile details persisted and fetched correctly.${COLORS_RESET}"
    echo "Profile: $FETCH_RESPONSE"
else
    echo -e "${COLORS_RED}✗ Persistence check failed.${COLORS_RESET}"
    echo "Response: $FETCH_RESPONSE"
    exit 1
fi

echo -e "\n${COLORS_GREEN}✅ All Profile Tests completed successfully!${COLORS_RESET}"
