// Debug Bridge for MCP - logs all communication
const http = require('http');
const https = require('https');
const readline = require('readline');
const fs = require('fs');

let wslUrl = process.argv[2];
if (!wslUrl) {
    console.error('Usage: node debug-bridge.js <wsl-url>');
    process.exit(1);
}

// Ensure URL ends with /mcp
if (!wslUrl.endsWith('/mcp')) {
    wslUrl = wslUrl.replace(/\/$/, '') + '/mcp';
}

console.error('Debug Bridge: Starting, URL = ' + wslUrl);

// Create log file
const logFile = 'C:\\Users\\pasca\\mcp-debug.log';
const log = (msg) => {
    const timestamp = new Date().toISOString();
    const logMsg = `[${timestamp}] ${msg}\n`;
    fs.appendFileSync(logFile, logMsg);
    console.error('DEBUG: ' + msg);
};

log('Bridge started, connecting to: ' + wslUrl);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

let messageCount = 0;

// Handle incoming MCP requests and forward to WSL2
rl.on('line', async (line) => {
    messageCount++;
    log(`Received message #${messageCount}: ${line}`);
    
    let requestId = null;
    try {
        const request = JSON.parse(line);
        requestId = request.id;
        log(`Parsed request - Method: ${request.method}, ID: ${requestId}`);
        
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
                log(`Server response: ${body}, Status: ${res.statusCode}`);
                
                // Check if response is empty or 204 (for notifications)
                if (res.statusCode === 204 || !body || body.trim() === '') {
                    log('Empty response or 204 status (notification) - not sending response to Claude');
                    // Don't send anything back for notifications
                    return;
                }
                
                try {
                    const result = JSON.parse(body);
                    
                    // Check if this is an error response for a notification (id is null)
                    if (result.error && result.id === null && requestId === undefined) {
                        log('Error response for notification (id: null) - not sending to Claude');
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
                    const response = JSON.stringify(result);
                    log(`Sending response: ${response}`);
                    process.stdout.write(response + '\n');
                } catch (e) {
                    log(`Error parsing server response: ${e.message}`);
                    const errorResponse = {
                        jsonrpc: "2.0",
                        id: requestId,
                        error: {
                            code: -32603,
                            message: "Invalid JSON response from server",
                            data: body
                        }
                    };
                    const response = JSON.stringify(errorResponse);
                    log(`Sending error response: ${response}`);
                    process.stdout.write(response + '\n');
                }
            });
        });
        
        req.on('error', (error) => {
            log(`Request error: ${error.message}`);
            const errorResponse = {
                jsonrpc: "2.0",
                id: requestId,
                error: {
                    code: -32603,
                    message: error.message
                }
            };
            const response = JSON.stringify(errorResponse);
            log(`Sending error response: ${response}`);
            process.stdout.write(response + '\n');
        });
        
        req.write(JSON.stringify(request));
        req.end();
        
    } catch (error) {
        log(`Bridge error: ${error.message}`);
        const errorResponse = {
            jsonrpc: "2.0",
            id: requestId,
            error: {
                code: -32700,
                message: "Parse error",
                data: error.message
            }
        };
        const response = JSON.stringify(errorResponse);
        log(`Sending parse error response: ${response}`);
        process.stdout.write(response + '\n');
    }
});

// Handle process termination gracefully
process.on('SIGINT', () => {
    log('Bridge shutting down (SIGINT)');
    process.exit(0);
});

process.on('SIGTERM', () => {
    log('Bridge shutting down (SIGTERM)');
    process.exit(0);
});

process.on('exit', () => {
    log('Bridge process exiting');
});

log('Bridge ready, waiting for messages...');