import React, { useState } from 'react';

// Vulnerability testing component for Command Injection
const CommandInjection = () => {
    const [command, setCommand] = useState('ls -la');
    const [output, setOutput] = useState('');

    const executeCommand = async () => {
        try {
            const response = await fetch('/api/exec', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });
            const data = await response.json();
            setOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            setOutput(`Error: ${error.message}`);
        }
    };

    return (
        <div className="vulnerability-card">
            <h2>💉 Command Injection</h2>
            <p>Executes arbitrary system commands via child_process.exec()</p>
            <div className="input-group">
                <label>Command:</label>
                <input
                    type="text"
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    placeholder="ls -la"
                />
            </div>
            <button onClick={executeCommand}>Execute Command</button>
            {output && <div className="output"><pre>{output}</pre></div>}
            <div style={{marginTop: '10px', fontSize: '11px', color: '#999'}}>
                Try: <code>whoami</code>, <code>cat /etc/passwd</code>, <code>ls -la; whoami</code>
            </div>
        </div>
    );
};

// Vulnerability testing component for Ping
const PingInjection = () => {
    const [host, setHost] = useState('127.0.0.1');
    const [output, setOutput] = useState('');

    const executePing = async () => {
        try {
            const response = await fetch('/api/ping', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ host })
            });
            const data = await response.json();
            setOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            setOutput(`Error: ${error.message}`);
        }
    };

    return (
        <div className="vulnerability-card">
            <h2>🏓 Ping Command Injection</h2>
            <p>Command injection via ping utility</p>
            <div className="input-group">
                <label>Host:</label>
                <input
                    type="text"
                    value={host}
                    onChange={(e) => setHost(e.target.value)}
                    placeholder="127.0.0.1"
                />
            </div>
            <button onClick={executePing}>Ping Host</button>
            {output && <div className="output"><pre>{output}</pre></div>}
            <div style={{marginTop: '10px', fontSize: '11px', color: '#999'}}>
                Try: <code>127.0.0.1; whoami</code>, <code>google.com && cat /etc/hosts</code>
            </div>
        </div>
    );
};

// Vulnerability testing component for Code Injection
const CodeInjection = () => {
    const [expression, setExpression] = useState('2 + 2');
    const [output, setOutput] = useState('');

    const evaluateExpression = async () => {
        try {
            const response = await fetch('/api/calc', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ expression })
            });
            const data = await response.json();
            setOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            setOutput(`Error: ${error.message}`);
        }
    };

    return (
        <div className="vulnerability-card">
            <h2>📝 Code Injection (eval)</h2>
            <p>Executes arbitrary JavaScript code via eval()</p>
            <div className="input-group">
                <label>Expression:</label>
                <input
                    type="text"
                    value={expression}
                    onChange={(e) => setExpression(e.target.value)}
                    placeholder="2 + 2"
                />
            </div>
            <button onClick={evaluateExpression}>Evaluate</button>
            {output && <div className="output"><pre>{output}</pre></div>}
            <div style={{marginTop: '10px', fontSize: '11px', color: '#999'}}>
                Try: <code>require('os').userInfo()</code>, <code>process.env</code>
            </div>
        </div>
    );
};

// Vulnerability testing component for Path Traversal
const PathTraversal = () => {
    const [filename, setFilename] = useState('sample.txt');
    const [output, setOutput] = useState('');

    const readFile = async () => {
        try {
            const response = await fetch(`/api/file?filename=${encodeURIComponent(filename)}`);
            const data = await response.json();
            setOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            setOutput(`Error: ${error.message}`);
        }
    };

    return (
        <div className="vulnerability-card">
            <h2>📁 Path Traversal</h2>
            <p>Read arbitrary files using directory traversal</p>
            <div className="input-group">
                <label>Filename:</label>
                <input
                    type="text"
                    value={filename}
                    onChange={(e) => setFilename(e.target.value)}
                    placeholder="sample.txt"
                />
            </div>
            <button onClick={readFile}>Read File</button>
            {output && <div className="output"><pre>{output}</pre></div>}
            <div style={{marginTop: '10px', fontSize: '11px', color: '#999'}}>
                Try: <code>../package.json</code>, <code>../../etc/passwd</code>
            </div>
        </div>
    );
};

// Vulnerability testing component for SSRF
const SSRFVulnerability = () => {
    const [url, setUrl] = useState('http://localhost:3000/api/health');
    const [output, setOutput] = useState('');

    const fetchUrl = async () => {
        try {
            const response = await fetch('/api/fetch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });
            const data = await response.json();
            setOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            setOutput(`Error: ${error.message}`);
        }
    };

    return (
        <div className="vulnerability-card">
            <h2>🌐 SSRF (Server-Side Request Forgery)</h2>
            <p>Make requests from the server to arbitrary URLs</p>
            <div className="input-group">
                <label>URL:</label>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="http://localhost:3000/api/health"
                />
            </div>
            <button onClick={fetchUrl}>Fetch URL</button>
            {output && <div className="output"><pre>{output}</pre></div>}
            <div style={{marginTop: '10px', fontSize: '11px', color: '#999'}}>
                Try: <code>http://localhost:3000/api/health</code>, <code>file:///etc/passwd</code>
            </div>
        </div>
    );
};

// Vulnerability testing component for Shell Injection
const ShellInjection = () => {
    const [cmd, setCmd] = useState('echo');
    const [args, setArgs] = useState('Hello World');
    const [output, setOutput] = useState('');

    const executeShell = async () => {
        try {
            const response = await fetch('/api/shell', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ cmd, args: [args] })
            });
            const data = await response.json();
            setOutput(JSON.stringify(data, null, 2));
        } catch (error) {
            setOutput(`Error: ${error.message}`);
        }
    };

    return (
        <div className="vulnerability-card">
            <h2>🐚 Shell Injection (spawn)</h2>
            <p>Execute commands via child_process.spawn() with shell option</p>
            <div className="input-group">
                <label>Command:</label>
                <input
                    type="text"
                    value={cmd}
                    onChange={(e) => setCmd(e.target.value)}
                    placeholder="echo"
                />
            </div>
            <div className="input-group">
                <label>Arguments:</label>
                <input
                    type="text"
                    value={args}
                    onChange={(e) => setArgs(e.target.value)}
                    placeholder="Hello World"
                />
            </div>
            <button onClick={executeShell}>Execute</button>
            {output && <div className="output"><pre>{output}</pre></div>}
            <div style={{marginTop: '10px', fontSize: '11px', color: '#999'}}>
                Try cmd: <code>sh</code> args: <code>-c "whoami"</code>
            </div>
        </div>
    );
};

// Main App Component
const App = () => {
    return (
        <div className="vulnerability-grid">
            <CommandInjection />
            <PingInjection />
            <CodeInjection />
            <PathTraversal />
            <SSRFVulnerability />
            <ShellInjection />
        </div>
    );
};

export default App;
