/**
 * VULNERABLE REACT SERVER - FOR SECURITY TESTING ONLY
 *
 * WARNING: This application contains intentional security vulnerabilities
 * for testing defensive security products. DO NOT deploy to production!
 *
 * Vulnerabilities included:
 * 1. Command Injection (exec endpoint)
 * 2. Code Injection (eval endpoint)
 * 3. Unsafe Deserialization
 * 4. Path Traversal
 * 5. Server-Side Request Forgery (SSRF)
 * 6. XSS via unsafe React rendering
 */

const express = require('express');
const bodyParser = require('body-parser');
const multer = require('multer');
const { exec, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const serialize = require('serialize-javascript');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// Configure multer for multipart/form-data
const upload = multer();

// VULNERABILITY 1: Command Injection via exec
// Allows arbitrary command execution through user input
app.post('/api/exec', (req, res) => {
    const { command } = req.body;

    console.log('[VULN] Command Injection attempt:', command);

    // VULNERABLE: Direct execution of user input
    exec(command, (error, stdout, stderr) => {
        if (error) {
            res.json({
                success: false,
                error: error.message,
                stderr: stderr
            });
            return;
        }
        res.json({
            success: true,
            output: stdout,
            stderr: stderr
        });
    });
});

// VULNERABILITY 2: Command Injection via ping utility
app.post('/api/ping', (req, res) => {
    const { host } = req.body;

    console.log('[VULN] Ping command injection attempt:', host);

    // VULNERABLE: Concatenating user input directly into command
    exec(`ping -c 4 ${host}`, (error, stdout, stderr) => {
        res.json({
            success: !error,
            output: stdout,
            error: error ? error.message : null
        });
    });
});

// VULNERABILITY 3: Code Injection via eval
app.post('/api/calc', (req, res) => {
    const { expression } = req.body;

    console.log('[VULN] Code injection attempt via eval:', expression);

    try {
        // VULNERABLE: Using eval on user input
        const result = eval(expression);
        res.json({ success: true, result: result });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

// VULNERABILITY 4: Path Traversal
app.get('/api/file', (req, res) => {
    const { filename } = req.query;

    console.log('[VULN] Path traversal attempt:', filename);

    // VULNERABLE: No sanitization of file path
    const filePath = path.join(__dirname, 'files', filename);

    fs.readFile(filePath, 'utf8', (error, data) => {
        if (error) {
            res.status(404).json({ error: 'File not found', message: error.message });
            return;
        }
        res.json({ content: data });
    });
});

// VULNERABILITY 5: Unsafe Deserialization
app.post('/api/deserialize', (req, res) => {
    const { data } = req.body;

    console.log('[VULN] Unsafe deserialization attempt');

    try {
        // VULNERABLE: Evaluating serialized data without validation
        const deserializedData = eval('(' + data + ')');
        res.json({ success: true, data: deserializedData });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

// VULNERABILITY 5b: RSC-Style Multipart Deserialization (React Server Components)
// This mimics how React Server Components handle multipart form data
app.post('/api/rsc-action', upload.none(), (req, res) => {
    console.log('[VULN] RSC-style deserialization attempt via multipart/form-data');
    console.log('[VULN] Form fields received:', Object.keys(req.body));

    try {
        // VULNERABLE: Reconstruct object from multipart fields without validation
        // This simulates how RSC deserializes form data into objects
        const reconstructedObject = {};

        // Parse each form field and reconstruct the object
        for (const [key, value] of Object.entries(req.body)) {
            try {
                // VULNERABLE: Using eval to parse JSON-like strings from form fields
                // This is where prototype pollution can occur
                reconstructedObject[key] = eval('(' + value + ')');
                console.log(`[VULN] Parsed field "${key}":`, value.substring(0, 100));
            } catch (e) {
                reconstructedObject[key] = value;
            }
        }

        // VULNERABLE: Process the reconstructed object
        // In a real RSC implementation, this would trigger promise resolution
        // which can execute the polluted prototype chain
        if (reconstructedObject['0'] && typeof reconstructedObject['0'] === 'object') {
            // Simulate RSC promise/action handling
            const actionData = reconstructedObject['0'];

            // Check if this looks like an RSC action payload
            if (actionData._response && actionData._response._prefix) {
                console.log('[VULN] Detected RSC action with _prefix:', actionData._response._prefix);
            }

            // VULNERABLE: Trigger any 'then' handlers (promise chain)
            // This is where the prototype pollution attack executes
            if (actionData.then) {
                console.log('[VULN] Detected prototype pollution via "then" property');
            }
        }

        res.json({
            success: true,
            message: 'RSC action processed',
            reconstructed: reconstructedObject,
            warning: 'This endpoint is vulnerable to prototype pollution via multipart form data'
        });

    } catch (error) {
        console.log('[VULN] RSC deserialization error:', error.message);
        res.json({
            success: false,
            error: error.message,
            stack: error.stack
        });
    }
});

// VULNERABILITY 6: Server-Side Request Forgery (SSRF)
app.post('/api/fetch', (req, res) => {
    const { url } = req.body;

    console.log('[VULN] SSRF attempt:', url);

    // VULNERABLE: Fetching arbitrary URLs without validation
    const https = require('https');
    const http = require('http');

    const client = url.startsWith('https') ? https : http;

    client.get(url, (response) => {
        let data = '';
        response.on('data', (chunk) => data += chunk);
        response.on('end', () => {
            res.json({ success: true, data: data });
        });
    }).on('error', (error) => {
        res.json({ success: false, error: error.message });
    });
});

// VULNERABILITY 7: Shell Command via spawn with shell option
app.post('/api/shell', (req, res) => {
    const { cmd, args } = req.body;

    console.log('[VULN] Shell injection via spawn:', cmd, args);

    // VULNERABLE: Using shell: true with user input
    const child = spawn(cmd, args, { shell: true });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => stdout += data);
    child.stderr.on('data', (data) => stderr += data);

    child.on('close', (code) => {
        res.json({
            success: code === 0,
            output: stdout,
            error: stderr,
            exitCode: code
        });
    });
});

// VULNERABILITY 8: File Write with Path Traversal
app.post('/api/writefile', (req, res) => {
    const { filename, content } = req.body;

    console.log('[VULN] File write with path traversal:', filename);

    // VULNERABLE: No path sanitization
    const filePath = path.join(__dirname, 'uploads', filename);

    fs.writeFile(filePath, content, (error) => {
        if (error) {
            res.json({ success: false, error: error.message });
            return;
        }
        res.json({ success: true, message: 'File written successfully' });
    });
});

// VULNERABILITY 9: Arbitrary Module Require
app.post('/api/require', (req, res) => {
    const { module } = req.body;

    console.log('[VULN] Arbitrary module require:', module);

    try {
        // VULNERABLE: Requiring arbitrary modules
        const requiredModule = require(module);
        res.json({
            success: true,
            message: 'Module loaded',
            type: typeof requiredModule
        });
    } catch (error) {
        res.json({ success: false, error: error.message });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'running',
        warning: 'This is a vulnerable application for testing only!',
        vulnerabilities: [
            'Command Injection',
            'Code Injection (eval)',
            'Unsafe Deserialization',
            'Path Traversal',
            'SSRF',
            'Shell Injection',
            'Arbitrary File Write',
            'Arbitrary Module Loading'
        ]
    });
});

// Serve React app
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Create necessary directories
const dirs = ['files', 'uploads', 'public'];
dirs.forEach(dir => {
    const dirPath = path.join(__dirname, dir);
    if (!fs.existsSync(dirPath)) {
        fs.mkdirSync(dirPath, { recursive: true });
    }
});

// Create a sample file for testing
fs.writeFileSync(
    path.join(__dirname, 'files', 'sample.txt'),
    'This is a sample file for testing path traversal vulnerabilities.'
);

app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('⚠️  VULNERABLE REACT SERVER RUNNING ⚠️');
    console.log('='.repeat(60));
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log('');
    console.log('WARNING: This application contains intentional security');
    console.log('vulnerabilities for testing purposes only!');
    console.log('');
    console.log('DO NOT deploy this application to production!');
    console.log('DO NOT expose this application to the internet!');
    console.log('='.repeat(60));
});

module.exports = app;
