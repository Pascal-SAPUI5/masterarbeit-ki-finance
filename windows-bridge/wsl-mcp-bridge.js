// WSL2 MCP Bridge for Windows
const http = require('http');
const https = require('https');
const readline = require('readline');

let wslUrl = process.argv[2];
if (!wslUrl) {
    console.error('Usage: node wsl-mcp-bridge.js <wsl-url>');
    process.exit(1);
}

// Ensure URL ends with /mcp
if (!wslUrl.endsWith('/mcp')) {
    wslUrl = wslUrl.replace(/\/$/, '') + '/mcp';
}

console.error('Bridging MCP requests to: ' + wslUrl);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

// Handle incoming MCP requests and forward to WSL2
rl.on('line', async (line) => {
    let requestId = null;
    try {
        const request = JSON.parse(line);
        requestId = request.id; // Save the request ID
        
        // Use http module instead of fetch
        const url = new URL(wslUrl);
        const options = {
            hostname: url.hostname,
            port: url.port || (url.protocol === 'https:' ? 443 : 80),
            path: url.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(JSON.stringify(request))
            }
        };
        
        const module = url.protocol === 'https:' ? https : http;
        
        const req = module.request(options, (res) => {
            let body = '';
            
            res.on('data', (chunk) => {
                body += chunk;
            });
            
            res.on('end', () => {
                // Check if response is empty or 204 (for notifications)
                if (res.statusCode === 204 || !body || body.trim() === '') {
                    // Don't send anything back for notifications
                    return;
                }
                
                try {
                    const result = JSON.parse(body);
                    
                    // Check if this is an error response for a notification (id is null)
                    if (result.error && result.id === null && requestId === undefined) {
                        // Don't send error responses for notifications
                        return;
                    }
                    
                    // Ensure the response has jsonrpc field
                    if (!result.jsonrpc) {
                        result.jsonrpc = "2.0";
                    }
                    // Ensure the response has the same ID as the request
                    if (requestId !== undefined && requestId !== null && !result.hasOwnProperty('id')) {
                        result.id = requestId;
                    }
                    process.stdout.write(JSON.stringify(result) + '\n');
                } catch (e) {
                    const errorResponse = {
                        jsonrpc: "2.0",
                        id: requestId,
                        error: {
                            code: -32603,
                            message: "Invalid JSON response from server",
                            data: body
                        }
                    };
                    process.stdout.write(JSON.stringify(errorResponse) + '\n');
                }
            });
        });
        
        req.on('error', (error) => {
            const errorResponse = {
                jsonrpc: "2.0",
                id: requestId,
                error: {
                    code: -32603,
                    message: error.message
                }
            };
            process.stdout.write(JSON.stringify(errorResponse) + '\n');
        });
        
        req.write(JSON.stringify(request));
        req.end();
        
    } catch (error) {
        console.error('Bridge error: ' + error.message);
        const errorResponse = {
            jsonrpc: "2.0",
            id: requestId,
            error: {
                code: -32700,
                message: "Parse error",
                data: error.message
            }
        };
        process.stdout.write(JSON.stringify(errorResponse) + '\n');
    }
});

// Handle process termination gracefully
process.on('SIGINT', () => {
    console.error('Bridge shutting down');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.error('Bridge shutting down');
    process.exit(0);
});