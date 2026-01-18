# Alternative Attack Vectors Research - Summary

## Executive Summary

This research explores **non-RCE attack vectors** for extracting the `VERCEL_PLATFORM_PROTECTION` environment variable from a Next.js 16.0.6 application, given that all React2Shell RCE attempts are blocked by Vercel's runtime mitigation.

**Key Finding**: Since code execution is blocked, we must focus on **information disclosure vulnerabilities** that leak environment variables without executing arbitrary code.

## Research Context

- **Target**: https://nextjs-cve-hackerone.vercel.app/
- **Next.js Version**: 16.0.6 (vulnerable to multiple CVEs)
- **React Version**: 19.2.1
- **Node Version**: v24.11.0
- **Goal**: Extract `VERCEL_PLATFORM_PROTECTION` environment variable
- **Constraint**: Runtime mitigation blocks all code execution (Function constructor access denied)

## Most Promising Attack Vectors

### 🔴 CRITICAL PRIORITY

#### 1. Vercel Special Paths (`/_src`, `/_logs`)
**Impact**: CRITICAL - Direct access to source code and build logs

**What it is**:
- Vercel provides special URL paths to access deployment source and build logs
- `/_src` - Complete source code including `.env` files
- `/_logs` - Build logs that may print environment variables during compilation

**Why it matters**:
- Build logs often echo environment variables for debugging
- Source code may contain hardcoded secrets or `.env` files
- **Default**: Protected by authentication
- **Risk**: If "Logs and Source Protection" is disabled in Project Settings, these are publicly accessible

**How to test**:
```bash
curl https://nextjs-cve-hackerone.vercel.app/_src
curl https://nextjs-cve-hackerone.vercel.app/_logs
```

**Expected if vulnerable**:
- 200 OK with source code or log content
- Build logs may contain: `VERCEL_PLATFORM_PROTECTION=flag{...}`

**Historical precedent**: Known Vercel misconfiguration that has exposed sensitive data in bug bounty programs.

---

#### 2. Source Map Exposure
**Impact**: CRITICAL - Can expose hardcoded secrets in original source code

**What it is**:
- Source maps (.map files) allow reconstruction of original JavaScript source from minified production code
- By default, Next.js disables source maps in production
- BUT Vercel may enable them for debugging purposes

**Why it matters**:
- Real-world examples of API keys, tokens, and secrets found in source maps
- **GETTR breach**: Entire codebase exposed via source maps, revealing undocumented API endpoints
- **Stripe API leak**: Secret keys hardcoded in source, visible through source maps

**How to test**:
```bash
# Check if source maps are referenced
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js | grep sourceMappingURL

# Try to access source map files
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js.map
```

**What to look for**:
- `sourcesContent` field containing original source code
- Search for: `VERCEL_`, `process.env`, `API_KEY`, `SECRET`, `TOKEN`

---

### 🟠 HIGH PRIORITY

#### 3. CVE-2025-55183 (Source Code Exposure in RSC)
**Impact**: HIGH - Next.js 16.0.6 is vulnerable (patched in 16.0.10+)

**What it is**:
- Medium severity vulnerability in React Server Components
- Can expose server-side source code through specially crafted requests
- Disclosed December 11, 2025

**Why it matters**:
- **Target is running vulnerable version 16.0.6**
- May leak server-side code containing environment variable references
- Does not require RCE

**How to test**:
```bash
curl -H "Accept: text/x-component" \
     -H "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D" \
     https://nextjs-cve-hackerone.vercel.app/
```

**Expected if vulnerable**:
- RSC payload format (starts with `1:`, `0:`, `S`, or `M`)
- May contain server component source code
- Search for environment variable references

---

#### 4. API Route Enumeration
**Impact**: HIGH - Common misconfiguration in Next.js apps

**What it is**:
- Next.js API routes in `/api/*` directory
- Developers may create debug/config endpoints that expose env vars
- Common patterns: `/api/env`, `/api/config`, `/api/debug`

**Why it matters**:
- Very common developer mistake to create debug endpoints
- Often forgotten and left enabled in production
- May return `process.env` directly

**How to test**:
```bash
curl https://nextjs-cve-hackerone.vercel.app/api/env
curl https://nextjs-cve-hackerone.vercel.app/api/config
curl https://nextjs-cve-hackerone.vercel.app/api/debug
curl https://nextjs-cve-hackerone.vercel.app/api/health
curl https://nextjs-cve-hackerone.vercel.app/api/status
```

**What to look for**:
- JSON responses containing environment variables
- 200 OK status (endpoint exists)
- Try POST if GET returns 405 Method Not Allowed

---

#### 5. Cache Poisoning (CVE-2025-49005)
**Impact**: HIGH - Can leak RSC payloads containing sensitive data

**What it is**:
- Vulnerability in Next.js >= 15.3.0 < 15.3.3 (patched)
- Missing `Vary` header allows RSC payloads to be cached and served as HTML
- **Note**: Target runs 16.0.6, may or may not be patched

**Why it matters**:
- RSC payloads can contain server component props and state
- May include environment variables passed to components
- Cached responses can be accessed by anyone

**How to test**:
```bash
# Step 1: Send RSC request to poison cache
curl -H "Accept: text/x-component" \
     -H "RSC: 1" \
     https://nextjs-cve-hackerone.vercel.app/

# Step 2: Send normal request to check if cache poisoned
curl https://nextjs-cve-hackerone.vercel.app/
```

**Expected if vulnerable**:
- Second request returns RSC payload (JSON format) instead of HTML
- Response starts with `1:` or `0:` instead of `<!DOCTYPE html>`

---

### 🟡 MEDIUM PRIORITY

#### 6. SSRF in Server Actions (CVE-2024-34351, CVE-2025-57822)
**Impact**: MEDIUM - Patched but worth testing

**What it is**:
- Server-Side Request Forgery in Next.js Server Actions
- CVE-2024-34351: SSRF via Host header manipulation (< 14.1.1)
- CVE-2025-57822: SSRF via middleware headers (< 14.2.32, < 15.4.7)

**Why it matters**:
- If SSRF exists, could access Vercel's internal metadata service
- Similar to AWS IMDS, may expose environment variables
- Could make requests to `http://169.254.169.254` or internal services

**How to test**:
```bash
curl -X POST https://nextjs-cve-hackerone.vercel.app/ \
  -H "Host: 169.254.169.254" \
  -H "Next-Action: 007138e0bfbdd7fe024391a1251fd5861f0b5145dc" \
  --data "..."
```

**Expected if vulnerable**:
- Response reflects internal service data
- Ability to make server-side HTTP requests

---

#### 7. Path Traversal (CVE-2020-5284)
**Impact**: MEDIUM - Old vulnerability, likely patched

**What it is**:
- Directory traversal in `/_next` routes (< 9.3.2)
- Could access files in `.next` directory or parent directories

**How to test**:
```bash
curl https://nextjs-cve-hackerone.vercel.app/_next/../../.env
curl https://nextjs-cve-hackerone.vercel.app/_next/../../.env.production
```

**Expected if vulnerable**:
- Access to `.env` files containing environment variables

---

#### 8. Build Artifacts and Manifests
**Impact**: MEDIUM - May reveal configuration information

**What it is**:
- Next.js build manifests and configuration files
- May contain route information, middleware config, etc.

**How to test**:
```bash
BUILD_ID="bIW_p-jXOXL69_fsJ2_vY"
curl https://nextjs-cve-hackerone.vercel.app/_next/static/$BUILD_ID/_buildManifest.js
curl https://nextjs-cve-hackerone.vercel.app/_next/static/$BUILD_ID/_middlewareManifest.js
```

---

## CVE Summary for Next.js 16.0.6

| CVE | Severity | Status | Impact |
|-----|----------|--------|--------|
| CVE-2025-66478 | Critical (10.0) | Known (React2Shell) | RCE - Blocked by runtime mitigation |
| CVE-2025-55183 | Medium | **VULNERABLE** | Source code exposure |
| CVE-2025-55184 | High | **VULNERABLE** | DoS (not useful for flag extraction) |
| CVE-2025-49005 | High (7.5) | Unknown | Cache poisoning - RSC payload leak |
| CVE-2024-34351 | High (7.4) | Likely patched | SSRF via Server Actions |
| CVE-2025-57822 | Unknown | Likely patched | SSRF via Middleware |
| CVE-2020-5284 | Medium | Patched | Path traversal |

**Key Insight**: CVE-2025-55183 is confirmed vulnerable in 16.0.6 and focuses on information disclosure, not RCE.

---

## Testing Tools Provided

### 1. Quick Scan Script (Bash)
**File**: `quick_scan.sh`

Fast automated scan of all critical vectors:
```bash
./quick_scan.sh
```

**What it does**:
- Tests all critical endpoints
- Searches responses for environment variables
- Saves accessible content to files
- Provides color-coded output
- ~2 minutes to complete

**Best for**: Quick initial assessment

---

### 2. Comprehensive Python Script
**File**: `test_alternative_vectors.py`

Detailed testing with secret detection:
```bash
./test_alternative_vectors.py
```

**What it does**:
- Tests all 10 attack vector categories
- Advanced pattern matching for secrets
- Parses JSON/source maps
- Detailed logging
- Saves all findings to files

**Best for**: Thorough investigation

---

### 3. Quick Reference URLs
**File**: `QUICK_TEST_URLS.md`

Copy-paste URLs for manual testing:
- Critical endpoints to test first
- One-liner commands
- cURL examples with proper headers
- Priority ordering

**Best for**: Manual testing, understanding each attack

---

### 4. Comprehensive Research Document
**File**: `alternative_attack_vectors.md`

Complete technical details:
- All 10 attack vectors explained
- CVE details and references
- Exploitation techniques
- Example payloads
- Historical context
- References to security research

**Best for**: Deep understanding, reference material

---

## Recommended Testing Workflow

### Phase 1: Quick Wins (5 minutes)
```bash
# Test the most critical vectors manually
curl https://nextjs-cve-hackerone.vercel.app/_src
curl https://nextjs-cve-hackerone.vercel.app/_logs
curl https://nextjs-cve-hackerone.vercel.app/api/env
curl https://nextjs-cve-hackerone.vercel.app/api/config
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js.map
```

### Phase 2: Automated Scan (2 minutes)
```bash
./quick_scan.sh
```

Review output files for any accessible content.

### Phase 3: Detailed Analysis (10 minutes)
```bash
./test_alternative_vectors.py
```

Review all saved files for sensitive data.

### Phase 4: Manual Verification (15 minutes)
- If Phase 1-3 find accessible endpoints, manually investigate
- Use browser DevTools to inspect responses
- Try variations of successful attacks
- Test with different HTTP methods (GET, POST, OPTIONS)

---

## What to Look For in Responses

When testing these vectors, search for:

1. **Direct match**: `VERCEL_PLATFORM_PROTECTION=flag{...}`
2. **Environment variable list**: JSON/text containing all env vars
3. **Process.env references**: `process.env.VERCEL_PLATFORM_PROTECTION`
4. **Base64 encoded data**: May be encoded environment variables
5. **Build output**: Logs showing env vars during compilation
6. **Error messages**: Stack traces revealing env var values
7. **Source code**: Comments or debug code with secrets
8. **RSC payloads**: Serialized component props containing env data

## Why These Vectors Work (When RCE Doesn't)

Traditional exploitation path:
```
Code Injection → Code Execution → Command Execution → Exfiltration
     ❌ Blocked by runtime mitigation
```

Alternative path:
```
Misconfiguration → Information Disclosure → Direct Access to Env Vars
     ✅ No code execution required
```

**Key principle**: We're not trying to execute code; we're looking for places where the environment variables are *already exposed* due to misconfigurations or vulnerabilities in the application/platform itself.

---

## Success Indicators

You've found the flag if you see:

1. **Direct exposure**: Response contains `VERCEL_PLATFORM_PROTECTION=...`
2. **Source code**: `.env` file or source code with the variable
3. **Build logs**: Logs showing the variable during deployment
4. **API response**: JSON containing all environment variables
5. **Source map**: Original source code with hardcoded values

---

## Known Next.js/Vercel Weak Points

Based on security research and bug bounty reports:

1. **Vercel's `/_src` and `/_logs` paths**
   - Often misconfigured
   - Directly expose what we need

2. **Production source maps**
   - Developers enable for debugging
   - Forget to disable
   - Multiple documented cases of secrets leaking

3. **Debug API routes**
   - `/api/env`, `/api/config` very common
   - Often created for testing
   - Forgotten in production

4. **CVE-2025-55183**
   - Confirmed vulnerable in 16.0.6
   - Specifically designed to leak source code
   - May be the "intended" solution for this CTF

5. **Cache poisoning**
   - RSC payloads can leak server-side data
   - Affects caching layers (CDN, reverse proxy)

---

## If Nothing Works

If all these vectors fail, consider:

1. **Combination attack**: Maybe you need to chain multiple vulnerabilities
   - SSRF + metadata service access
   - Cache poison + source exposure

2. **Timing attacks**: Check if response times differ based on env var values

3. **Error-based disclosure**: Trigger errors that might leak env vars in stack traces

4. **Client-side exposure**: Check if `NEXT_PUBLIC_VERCEL_PLATFORM_PROTECTION` exists
   ```bash
   curl https://nextjs-cve-hackerone.vercel.app/ | grep NEXT_PUBLIC_
   ```

5. **The "intended" solution**: CTF challenges often have a specific path
   - CVE-2025-55183 seems most likely given it's unpatched in 16.0.6
   - May require specific payload format

---

## References

### Official Advisories
- [Next.js CVE-2025-66478](https://nextjs.org/blog/CVE-2025-66478)
- [Vercel Security Bulletin: CVE-2025-55183/55184](https://vercel.com/kb/bulletin/security-bulletin-cve-2025-55184-and-cve-2025-55183)
- [GitHub: Next.js Security Discussion](https://github.com/vercel/next.js/discussions/86939)

### Research Papers & Blog Posts
- [Assetnote: Next.js SSRF](https://www.assetnote.io/resources/research/advisory-next-js-ssrf-cve-2024-34351)
- [Sentry: Abusing Exposed Sourcemaps](https://blog.sentry.security/abusing-exposed-sourcemaps/)
- [zhero: Next.js Cache Poisoning](https://zhero-web-sec.github.io/research-and-things/nextjs-and-cache-poisoning-a-quest-for-the-black-hole)
- [HackTricks: Vercel Security](https://cloud.hacktricks.wiki/en/pentesting-ci-cd/vercel-security.html)

### Related CTF Writeups
- [MRE Security: React2Shell CTF](https://mresecurity.com/blog/react2shell-unauthenticated-rce-cve-2025-55182-full-exploit-walkthrough-p3rf3ctr00t-2025-ctf)
- [Datadog: CVE-2025-55182 Analysis](https://securitylabs.datadoghq.com/articles/cve-2025-55182-react2shell-remote-code-execution-react-server-components/)

---

## Files in This Repository

```
alternative_attack_vectors.md      - Complete technical research (10 vectors)
test_alternative_vectors.py        - Automated Python testing script
quick_scan.sh                      - Fast bash scanning script
QUICK_TEST_URLS.md                 - Manual testing reference
ALTERNATIVE_VECTORS_SUMMARY.md     - This file (overview)

# Previous React2Shell research:
FINDINGS.md                        - React2Shell exploitation attempts
SUMMARY.md                         - React2Shell comprehensive summary
react2shell_poc.py                 - Basic React2Shell POC
react2shell_advanced.py            - Advanced React2Shell techniques
```

---

## Quick Start

**If you want to start testing immediately**:

```bash
# Make scripts executable (already done)
chmod +x quick_scan.sh test_alternative_vectors.py

# Run quick scan (2 minutes)
./quick_scan.sh

# If you find something interesting, run detailed scan
./test_alternative_vectors.py

# Or manually test the most critical endpoints
curl https://nextjs-cve-hackerone.vercel.app/_src
curl https://nextjs-cve-hackerone.vercel.app/_logs
curl https://nextjs-cve-hackerone.vercel.app/api/env
```

**Good luck! The flag is out there. 🎯**
