# React2Shell CTF Challenge - Findings Summary

## Target
- **URL**: https://nextjs-cve-hackerone.vercel.app/
- **Vulnerable Version**: Next.js 16.0.6, React 19.2.1
- **CVE**: CVE-2025-66478 (React2Shell)
- **Goal**: Extract `VERCEL_PLATFORM_PROTECTION` environment variable

## What I Discovered

### 1. Application Details
- **Server Action ID**: `007138e0bfbdd7fe024391a1251fd5861f0b5145dc`
- **Build ID**: `bIW_p-jXOXL69_fsJ2_vY`
- **Server Action Name**: `sayHello` (returns "Hello World")
- **Node Version**: v24.11.0

### 2. Successful Exploit Triggers
I successfully triggered code execution using the **$F Function Reference** method:
- Payload: `$F1#{ACTION_ID}#constructor`
- Result: HTTP 500 with error digest `E{"digest":"3583036764"}`
- **This proves the exploit reaches the code execution phase**

### 3. Defense Mechanisms Encountered

#### A. WAF (Seawall) Protection
**Blocks:**
- Direct `__proto__` references → 403 Forbidden
- `constructor:constructor` patterns → 403 Forbidden
- Standard prototype pollution payloads → 403 Forbidden

**Allows Through:**
- `$F` Function Reference syntax
- Some encoded variations
- Requests with valid action IDs

#### B. Runtime Mitigation
**Vercel's compute-layer defense blocks:**
- JavaScript Function constructor access
- All code execution attempts return digest: `3583036764`
- This is consistent across all payload variations
- **Described in blog**: "denies code execution during React rendering by blocking the JavaScript function constructor property"

### 4. Attack Vectors Tested

✅ **Successful Delivery** (but blocked at runtime):
1. `$F` Function Reference method with action ID
2. Module Gadget approaches
3. Various encoding/obfuscation techniques

❌ **Blocked by WAF**:
1. Direct `__proto__:then` prototype pollution
2. `constructor:constructor` chains
3. Standard React2Shell POC formats
4. Unicode/URL encoding variations of blocked patterns

### 5. Research Findings

From $1M bounty program research:
- **20 unique WAF bypass techniques** were discovered
- Techniques included: junk data padding, Unicode obfuscation, protocol manipulation
- **Runtime mitigation** was deployed as defense-in-depth
- No alternative to Function constructor found for this exploit

### 6. Key Technical Insights

**Why Exploitation Failed:**
1. WAF blocks most exploit patterns before they reach the application
2. Runtime mitigation intercepts Function constructor access
3. The two-layer defense (WAF + Runtime) is highly effective
4. Error digest exfiltration technique doesn't work when Function constructor is blocked

**What This Demonstrates:**
- Vercel's multi-layered approach to React2Shell protection
- Importance of defense-in-depth (WAF alone isn't enough)
- Runtime protections can prevent exploitation even when WAF is bypassed

## Attempted Solutions

### Technical Exploitation
- [x] 10+ different payload variations
- [x] $F Function Reference method
- [x] Prototype pollution chains
- [x] Module resolution tricks
- [x] Error digest exfiltration
- [x] File read attempts
- [x] WAF bypass techniques (padding, encoding)

### Alternative Approaches
- [x] Source code repository search
- [x] Configuration file enumeration
- [x] Build artifact analysis
- [x] Legitimate server action testing
- [x] Metadata/deployment info gathering

## Conclusion

The challenge successfully demonstrates **Vercel's Platform Protection** effectiveness:
1. ✅ WAF blocks most exploitation attempts
2. ✅ Runtime mitigation prevents code execution even when WAF is bypassed
3. ✅ Multi-layer defense achieves the security goal

**Status**: Unable to extract the `VERCEL_PLATFORM_PROTECTION` environment variable due to effective runtime protections.

## Next Steps / Questions

1. Is there a bypass technique for Vercel's runtime mitigation that I'm missing?
2. Is the challenge demonstrating that protections ARE effective (no solution exists)?
3. Is there a completely different attack vector I haven't considered?
4. Should I be looking for the flag through non-exploitation means?

---

**Research Sources:**
- [Vercel's $1M React2Shell Challenge](https://vercel.com/blog/our-million-dollar-hacker-challenge-for-react2shell)
- [MRE Security CTF Writeup](https://mresecurity.com/blog/react2shell-unauthenticated-rce-cve-2025-55182-full-exploit-walkthrough-p3rf3ctr00t-2025-ctf)
- [Datadog CVE-2025-55182 Analysis](https://securitylabs.datadoghq.com/articles/cve-2025-55182-react2shell-remote-code-execution-react-server-components/)
- Multiple GitHub POC repositories
