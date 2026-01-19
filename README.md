# 🔓 Vulnerable React Server - Security Testing Environment

⚠️ **WARNING: THIS APPLICATION CONTAINS INTENTIONAL SECURITY VULNERABILITIES** ⚠️

This is a deliberately vulnerable React/Express application designed for testing defensive security products, intrusion detection systems, and security monitoring tools.

**DO NOT DEPLOY TO PRODUCTION**
**DO NOT EXPOSE TO THE INTERNET**
**USE IN ISOLATED TESTING ENVIRONMENTS ONLY**

## 🎯 Purpose

This application is designed to help security professionals:
- Test defensive security products
- Validate intrusion detection systems (IDS)
- Test web application firewalls (WAF)
- Practice security analysis and penetration testing
- Demonstrate common web vulnerabilities
- Train security teams on attack detection

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
npm install

# Build the React frontend
npm run build

# Start the server
npm start
```

The server will start on `http://localhost:3000`

### Development Mode

```bash
# Start with auto-reload
npm run dev
```

## 🐛 Included Vulnerabilities

### 1. Command Injection (OS Command Injection)
**Endpoint:** `POST /api/exec`
**Description:** Executes arbitrary system commands via `child_process.exec()`

**Payload Examples:**
```bash
# Basic command
whoami

# Command chaining
ls -la; cat /etc/passwd

# Command substitution
echo $(whoami)

# Pipe commands
cat /etc/passwd | grep root
```

**MITRE ATT&CK:** T1059 - Command and Scripting Interpreter

---

### 2. Ping Command Injection
**Endpoint:** `POST /api/ping`
**Description:** Command injection via unsanitized ping utility

**Payload Examples:**
```bash
# Command chaining
127.0.0.1; whoami

# Command substitution
127.0.0.1 && cat /etc/hosts

# Pipe injection
127.0.0.1 | ls -la
```

**MITRE ATT&CK:** T1059.004 - Unix Shell

---

### 3. Code Injection (eval)
**Endpoint:** `POST /api/calc`
**Description:** Executes arbitrary JavaScript code via `eval()`

**Payload Examples:**
```javascript
// Access environment variables
process.env

// Read system information
require('os').userInfo()

// Execute commands
require('child_process').execSync('whoami').toString()

// Read files
require('fs').readFileSync('/etc/passwd', 'utf8')
```

**MITRE ATT&CK:** T1059.007 - JavaScript

---

### 4. Path Traversal (Directory Traversal)
**Endpoint:** `GET /api/file?filename=`
**Description:** Read arbitrary files using path traversal

**Payload Examples:**
```bash
# Read package.json
../package.json

# Read system files
../../../etc/passwd

# Windows systems
..\..\..\windows\system32\drivers\etc\hosts

# Read server configuration
../server.js
```

**MITRE ATT&CK:** T1005 - Data from Local System

---

### 5. Server-Side Request Forgery (SSRF)
**Endpoint:** `POST /api/fetch`
**Description:** Make requests from the server to arbitrary URLs

**Payload Examples:**
```bash
# Access internal services
http://localhost:3000/api/health

# Access cloud metadata (AWS)
http://169.254.169.254/latest/meta-data/

# Access cloud metadata (GCP)
http://metadata.google.internal/computeMetadata/v1/

# File protocol
file:///etc/passwd
```

**MITRE ATT&CK:** T1590.005 - Gather Victim Network Information

---

### 6. Shell Injection via spawn()
**Endpoint:** `POST /api/shell`
**Description:** Execute commands via `child_process.spawn()` with shell option

**Payload Examples:**
```bash
# Command: sh
# Args: -c "whoami"

# Command: bash
# Args: -c "cat /etc/passwd"

# Command: node
# Args: -e "console.log(process.env)"
```

**MITRE ATT&CK:** T1059 - Command and Scripting Interpreter

---

### 7. Arbitrary File Write
**Endpoint:** `POST /api/writefile`
**Description:** Write arbitrary content to files with path traversal

**Payload Examples:**
```bash
# Filename: ../../../tmp/pwned.txt
# Content: You've been pwned!

# Filename: ../public/backdoor.html
# Content: <script>alert('XSS')</script>
```

**MITRE ATT&CK:** T1105 - Ingress Tool Transfer

---

### 8. Unsafe Deserialization
**Endpoint:** `POST /api/deserialize`
**Description:** Evaluates serialized data without validation

**MITRE ATT&CK:** T1027.002 - Software Packing

---

### 9. Arbitrary Module Loading
**Endpoint:** `POST /api/require`
**Description:** Require arbitrary Node.js modules

**Payload Examples:**
```javascript
// Module: child_process
// Module: fs
// Module: net
```

**MITRE ATT&CK:** T1129 - Shared Modules

---

## 🧪 Testing the Application

### Using the Web Interface

1. Open `http://localhost:3000` in your browser
2. Each vulnerability has its own card with input fields
3. Enter payloads and click the execute button
4. View results in the output section

### Using cURL

```bash
# Command Injection
curl -X POST http://localhost:3000/api/exec \
  -H "Content-Type: application/json" \
  -d '{"command":"whoami"}'

# Path Traversal
curl "http://localhost:3000/api/file?filename=../package.json"

# Code Injection
curl -X POST http://localhost:3000/api/calc \
  -H "Content-Type: application/json" \
  -d '{"expression":"process.env"}'

# SSRF
curl -X POST http://localhost:3000/api/fetch \
  -H "Content-Type: application/json" \
  -d '{"url":"http://localhost:3000/api/health"}'
```

### Using Python

```python
import requests

# Command Injection
response = requests.post('http://localhost:3000/api/exec',
    json={'command': 'whoami'})
print(response.json())

# Path Traversal
response = requests.get('http://localhost:3000/api/file',
    params={'filename': '../package.json'})
print(response.json())
```

## 🔍 Expected Defensive Detections

A properly configured security product should detect:

1. **Command Injection Attempts**
   - Shell metacharacters in input (`;`, `|`, `&&`, `||`)
   - Command substitution patterns (`$()`, `` ` ` ``)
   - Suspicious system commands (`whoami`, `cat`, `ls`, etc.)

2. **Path Traversal Attempts**
   - Directory traversal patterns (`../`, `..\`)
   - Attempts to access sensitive files (`/etc/passwd`, `/etc/shadow`)

3. **Code Injection**
   - Use of `eval()`, `Function()` constructors
   - Dynamic code execution patterns

4. **SSRF Attempts**
   - Requests to internal IP ranges (127.0.0.1, 169.254.169.254)
   - Cloud metadata service access
   - File protocol usage

5. **Suspicious Process Execution**
   - Spawning of shells (`/bin/sh`, `/bin/bash`)
   - Execution of system utilities

## 📊 Logging

All vulnerable endpoints log attempted attacks to the console:
```
[VULN] Command Injection attempt: whoami
[VULN] Path traversal attempt: ../../../etc/passwd
[VULN] Code injection attempt via eval: process.env
[VULN] SSRF attempt: http://169.254.169.254/latest/meta-data/
```

## 🛡️ Testing Your Defenses

### Recommended Test Scenarios

1. **Basic Detection Test**
   - Execute simple commands: `whoami`, `ls`, `pwd`
   - Verify your security product detects and blocks these

2. **Evasion Techniques**
   - Try obfuscation: `who``ami`, `w'h'o'a'm'i`
   - Test encoding: URL encoding, base64
   - Use alternative commands: `id` instead of `whoami`

3. **Chained Attacks**
   - Combine vulnerabilities
   - Use SSRF to access internal command execution endpoints

4. **Performance Testing**
   - Send high volumes of attack requests
   - Test rate limiting and throttling

5. **Lateral Movement Simulation**
   - Use SSRF to scan internal network
   - Attempt to access cloud metadata services

## 🏗️ Architecture

```
vulnerable-react-server/
├── server.js              # Vulnerable Express server
├── src/
│   ├── index.jsx         # React entry point
│   └── App.jsx           # React components with vulnerability testing UI
├── public/
│   ├── index.html        # HTML template
│   └── bundle.js         # Webpack bundle (generated)
├── files/                # Test files for path traversal
├── uploads/              # Directory for file write tests
├── package.json          # Dependencies
└── webpack.config.js     # Webpack configuration
```

## 🔒 Security Notes

### Running Safely

1. **Use in isolated environments only**
   - Virtual machines
   - Docker containers
   - Isolated networks

2. **Never expose to the internet**
   - Bind to localhost only
   - Use firewall rules
   - No port forwarding

3. **Monitor system activity**
   - Watch for unexpected process execution
   - Monitor file system changes
   - Check network connections

### Container Deployment

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

```bash
# Build and run in container
docker build -t vulnerable-react-server .
docker run -p 127.0.0.1:3000:3000 vulnerable-react-server
```

## 📚 Educational Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

## ⚖️ Legal Disclaimer

This application is provided for educational and authorized security testing purposes only. Users are responsible for:

- Obtaining proper authorization before testing
- Complying with all applicable laws and regulations
- Using the application ethically and responsibly
- Not deploying in production environments
- Not exposing the application to unauthorized users

The authors assume no liability for misuse of this software.

## 🤝 Contributing

This is a security testing tool. If you find additional vulnerabilities to add or improvements to existing ones, please contribute responsibly.

## 📝 License

MIT License - Use at your own risk

---

**Remember: With great power comes great responsibility. Use this tool ethically and legally.**
