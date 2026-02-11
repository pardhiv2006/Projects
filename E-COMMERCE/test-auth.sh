#!/bin/bash

# Test Script for First Mart Authentication Flow
API_URL="http://localhost:5001/api"
COLORS_RESET='\033[0m'
COLORS_GREEN='\033[0;32m'
COLORS_RED='\033[0;31m'
COLORS_YELLOW='\033[1;33m'

echo -e "${COLORS_YELLOW}🧪 First Mart Auth System Test Suite${COLORS_RESET}\n"

# Test 1: Health Check
echo -e "${COLORS_YELLOW}Test 1: Health Check${COLORS_RESET}"
HEALTH=$(curl -s $API_URL/health)
if [[ $HEALTH == *"OK"* ]]; then
    echo -e "${COLORS_GREEN}✓ Backend is running${COLORS_RESET}"
else
    echo -e "${COLORS_RED}✗ Backend is NOT running. Please start it with 'npm run dev' in the server folder.${COLORS_RESET}"
    exit 1
fi

# Test 2: Signup
echo -e "${COLORS_YELLOW}Test 2: Signup New User${COLORS_RESET}"
RANDOM_NUM=$RANDOM
USER_EMAIL="testuser_$RANDOM_NUM@example.com"
SIGNUP_PAYLOAD="{\"name\":\"Test User\",\"email\":\"$USER_EMAIL\",\"password\":\"password123\"}"

SIGNUP_RESPONSE=$(curl -s -X POST $API_URL/auth/signup \
  -H "Content-Type: application/json" \
  -d "$SIGNUP_PAYLOAD")

TOKEN=$(echo $SIGNUP_RESPONSE | grep -o '"token":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ ! -z "$TOKEN" ]; then
    echo -e "${COLORS_GREEN}✓ Signup successful. Token received.${COLORS_RESET}"
else
    echo -e "${COLORS_RED}✗ Signup failed.${COLORS_RESET}"
    echo "Response: $SIGNUP_RESPONSE"
    exit 1
fi

# Test 3: Login
echo -e "${COLORS_YELLOW}Test 3: Login with same details${COLORS_RESET}"
LOGIN_PAYLOAD="{\"email\":\"$USER_EMAIL\",\"password\":\"password123\"}"

LOGIN_RESPONSE=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d "$LOGIN_PAYLOAD")

LOGIN_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*"' | head -1 | cut -d'"' -f4)

if [ "$TOKEN" != "" ] && [ "$LOGIN_TOKEN" != "" ]; then
    echo -e "${COLORS_GREEN}✓ Login successful. Details verified.${COLORS_RESET}"
else
    echo -e "${COLORS_RED}✗ Login failed.${COLORS_RESET}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

# Test 4: Fetch Profile
echo -e "${COLORS_YELLOW}Test 4: Fetch User Profile${COLORS_RESET}"
PROFILE_RESPONSE=$(curl -s -X GET $API_URL/profile \
  -H "Authorization: Bearer $LOGIN_TOKEN")

if [[ $PROFILE_RESPONSE == *"$USER_EMAIL"* ]]; then
    echo -e "${COLORS_GREEN}✓ Profile details fetched correctly.${COLORS_RESET}"
    echo "Profile: $PROFILE_RESPONSE"
else
    echo -e "${COLORS_RED}✗ Profile fetch failed or details mismatch.${COLORS_RESET}"
    echo "Response: $PROFILE_RESPONSE"
    exit 1
fi

echo -e "\n${COLORS_GREEN}✅ All Auth Tests completed successfully!${COLORS_RESET}"
