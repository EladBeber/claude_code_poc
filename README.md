# Next.js 16.0.6 Security Research Repository

Comprehensive security research for extracting environment variables from Next.js 16.0.6 / Vercel deployments.

## Target Information

- **URL**: https://nextjs-cve-hackerone.vercel.app/
- **Next.js Version**: 16.0.6
- **React Version**: 19.2.1
- **Node Version**: v24.11.0
- **Goal**: Extract `VERCEL_PLATFORM_PROTECTION` environment variable
- **Webhook**: https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a

## Repository Structure

### Alternative Attack Vectors (Non-RCE)

Since React2Shell RCE is blocked by runtime mitigation, focus on information disclosure vectors:

1. **ALTERNATIVE_VECTORS_SUMMARY.md** - START HERE
   - Executive summary and quick start guide
   - Explains why RCE won't work and what will
   - Recommended testing workflow
   - Most promising attack vectors

2. **alternative_attack_vectors.md** - Complete Technical Research
   - All 10 attack vectors in detail
   - CVE information and exploitation techniques
   - Specific URLs and payloads to test
   - References to security research

3. **QUICK_TEST_URLS.md** - Manual Testing Reference
   - Copy-paste URLs for immediate testing
   - Priority-ordered endpoints
   - One-liner commands
   - Quick grep patterns for secrets

### Testing Tools

4. **quick_scan.sh** - Fast Automated Scan (2 min)
   ```bash
   ./quick_scan.sh
   ```
   - Tests critical endpoints
   - Color-coded output
   - Saves accessible content to files
   - Searches for environment variables

5. **test_alternative_vectors.py** - Comprehensive Testing (10 min)
   ```bash
   ./test_alternative_vectors.py
   ```
   - Tests all 10 attack vector categories
   - Advanced pattern matching for secrets
   - Parses JSON and source maps
   - Detailed logging

### React2Shell RCE Research (Blocked)

6. **FINDINGS.md** - React2Shell Exploitation Attempts
   - All RCE attempts and results
   - WAF and runtime mitigation analysis
   - Error digest tracking
   - Why RCE doesn't work

7. **SUMMARY.md** - Comprehensive React2Shell Summary
   - 50+ payload variations tested
   - Defense mechanisms encountered
   - Technical insights

8. **react2shell_poc.py** - Basic React2Shell POC
   - Prototype pollution vector
   - Command execution attempts

9. **react2shell_advanced.py** - Advanced React2Shell Techniques
   - $F Function Reference method
   - Module gadget approaches
   - WAF bypass attempts

## Quick Start

### Option 1: Automated Testing (Recommended)

```bash
# Run quick scan
./quick_scan.sh

# Review output files
ls -lh response_*.txt

# Run comprehensive scan
./test_alternative_vectors.py
```

### Option 2: Manual Testing (High Priority Targets)

```bash
# Critical: Vercel special paths
curl https://nextjs-cve-hackerone.vercel.app/_src
curl https://nextjs-cve-hackerone.vercel.app/_logs

# High: Source maps
curl https://nextjs-cve-hackerone.vercel.app/_next/static/chunks/main.js.map

# High: API routes
curl https://nextjs-cve-hackerone.vercel.app/api/env
curl https://nextjs-cve-hackerone.vercel.app/api/config

# High: CVE-2025-55183 (Source exposure)
curl -H "Accept: text/x-component" \
     -H "Next-Router-State-Tree: %5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D" \
     https://nextjs-cve-hackerone.vercel.app/
```

## Attack Vector Summary

### Most Promising (In Priority Order)

1. **Vercel Special Paths** (`/_src`, `/_logs`)
   - Direct access to source and build logs
   - If misconfigured, immediately exposes what we need

2. **Source Map Exposure** (.map files)
   - Real-world history of exposing secrets
   - Check if `productionBrowserSourceMaps: true`

3. **CVE-2025-55183** (Source Code Exposure)
   - Target is vulnerable (16.0.6)
   - Information disclosure in RSC responses

4. **API Route Enumeration**
   - Common developer mistake
   - `/api/env`, `/api/config`, `/api/debug`

5. **Cache Poisoning** (CVE-2025-49005)
   - RSC payload leak via cache
   - May contain environment variables

6. **SSRF** (CVE-2024-34351, CVE-2025-57822)
   - Access to Vercel metadata service
   - Similar to AWS IMDS

7. **Path Traversal** (CVE-2020-5284)
   - Access `.env` files
   - Likely patched but worth testing

8. **Build Artifacts**
   - Manifests and configuration files
   - May reveal sensitive information

9. **Debug Endpoints**
   - Development mode endpoints
   - Error handling that leaks info

10. **GraphQL/API Routes**
    - Introspection and schema exposure
    - Custom API routes

## Known CVEs Affecting Target

| CVE | Severity | Status | Vector |
|-----|----------|--------|--------|
| CVE-2025-66478 | Critical (10.0) | Known | React2Shell RCE - BLOCKED |
| **CVE-2025-55183** | Medium | **VULNERABLE** | **Source Code Exposure** |
| CVE-2025-55184 | High | VULNERABLE | DoS (not useful) |
| CVE-2025-49005 | High (7.5) | Unknown | Cache Poisoning |
| CVE-2024-34351 | High (7.4) | Likely Patched | SSRF |
| CVE-2025-57822 | Unknown | Likely Patched | SSRF Middleware |

**Key**: CVE-2025-55183 is the most promising confirmed vulnerability.

## Why RCE Doesn't Work

From extensive testing (50+ payloads):

1. **WAF (Seawall)** blocks:
   - `__proto__` patterns → 403 Forbidden
   - `constructor:constructor` chains → 403 Forbidden
   - Standard prototype pollution → 403 Forbidden

2. **Runtime Mitigation** blocks:
   - JavaScript Function constructor access
   - All `$F` method payloads → 500 error
   - Error digest: `3583036764` (consistent)
   - No code execution occurs at runtime

**Conclusion**: Must use information disclosure, not code execution.

## What to Look For

When testing, search responses for:

1. `VERCEL_PLATFORM_PROTECTION=...` (direct match)
2. Environment variable dumps (JSON/text)
3. `process.env.VERCEL_PLATFORM_PROTECTION` references
4. Base64 encoded data
5. Build output logs
6. Error messages with stack traces
7. Source code with hardcoded values
8. RSC payloads with serialized props

## Success Criteria

You've found the flag if you see:

- Direct exposure in API response
- `.env` file contents via path traversal or `/_src`
- Build logs showing the variable
- Source maps with original source containing the value
- RSC payload with environment data

## Documentation Navigation

**Want to understand the approach?**
→ Read `ALTERNATIVE_VECTORS_SUMMARY.md`

**Want detailed technical info?**
→ Read `alternative_attack_vectors.md`

**Want to start testing immediately?**
→ Run `./quick_scan.sh` or use `QUICK_TEST_URLS.md`

**Want to understand why RCE failed?**
→ Read `FINDINGS.md` and `SUMMARY.md`

## Key Research Sources

- [Next.js CVE-2025-66478 Advisory](https://nextjs.org/blog/CVE-2025-66478)
- [Vercel Security Bulletin](https://vercel.com/kb/bulletin/security-bulletin-cve-2025-55184-and-cve-2025-55183)
- [Assetnote: Next.js SSRF](https://www.assetnote.io/resources/research/advisory-next-js-ssrf-cve-2024-34351)
- [Sentry: Abusing Exposed Sourcemaps](https://blog.sentry.security/abusing-exposed-sourcemaps/)
- [HackTricks: Vercel Security](https://cloud.hacktricks.wiki/en/pentesting-ci-cd/vercel-security.html)
- [zhero: Next.js Cache Poisoning](https://zhero-web-sec.github.io/research-and-things/nextjs-and-cache-poisoning-a-quest-for-the-black-hole)

## Files Created

```
README.md                          - This file
ALTERNATIVE_VECTORS_SUMMARY.md     - Executive summary (START HERE)
alternative_attack_vectors.md      - Complete technical research
QUICK_TEST_URLS.md                 - Quick reference for manual testing
test_alternative_vectors.py        - Comprehensive Python testing script
quick_scan.sh                      - Fast bash scanning script

FINDINGS.md                        - React2Shell findings
SUMMARY.md                         - React2Shell comprehensive summary
react2shell_poc.py                 - Basic React2Shell POC
react2shell_advanced.py            - Advanced React2Shell techniques
```

## Testing Checklist

- [ ] Run `./quick_scan.sh`
- [ ] Check `/_src` and `/_logs` paths
- [ ] Test for source maps
- [ ] Test CVE-2025-55183 (RSC source exposure)
- [ ] Enumerate API routes
- [ ] Test cache poisoning
- [ ] Try path traversal
- [ ] Check build artifacts
- [ ] Analyze response headers
- [ ] Review all saved output files
- [ ] Run `./test_alternative_vectors.py` for comprehensive testing
- [ ] Manually verify any findings

---

**Last Updated**: 2026-01-18
**Status**: Active Research - Focused on Non-RCE Information Disclosure
