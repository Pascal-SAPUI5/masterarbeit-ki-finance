#!/usr/bin/env node
/**
 * WSL2 MCP Bridge for Windows
 * This bridges MCP requests from Windows to WSL2
 */

const readline = require('readline');
const http = require('http');

const wslUrl = process.argv[2] || 'http://localhost:3001';
console.error(`MCP Bridge: Connecting to ${wslUrl}`);

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

// Handle incoming MCP requests from Claude Desktop
rl.on('line', async (line) => {
    try {
        const request = JSON.parse(line);
        console.error(`MCP Bridge: Received request - ${request.method}`);
        
        // Forward to WSL2 MCP server
        const response = await forwardRequest(wslUrl + '/mcp', request);
        
        // Send response back to Claude Desktop
        console.log(JSON.stringify(response));
        
    } catch (error) {
        console.error(`MCP Bridge Error: ${error.message}`);
        const errorResponse = {
            jsonrpc: "2.0",
            id: null,
            error: {
                code: -32603,
                message: error.message,
                data: error.stack
            }
        };
        console.log(JSON.stringify(errorResponse));
    }
});

async function forwardRequest(url, request) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify(request);
        
        const urlObj = new URL(url);
        const options = {
            hostname: urlObj.hostname,
            port: urlObj.port || 80,
            path: urlObj.pathname,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(data)
            }
        };
        
        const req = http.request(options, (res) => {
            let body = '';
            
            res.on('data', (chunk) => {
                body += chunk;
            });
            
            res.on('end', () => {
                try {
                    const response = JSON.parse(body);
                    resolve(response);
                } catch (error) {
                    reject(new Error(`Invalid JSON response: ${body}`));
                }
            });
        });
        
        req.on('error', (error) => {
            reject(error);
        });
        
        req.write(data);
        req.end();
    });
}

// Handle process termination
process.on('SIGINT', () => {
    console.error('MCP Bridge: Shutting down');
    process.exit(0);
});

process.on('uncaughtException', (error) => {
    console.error('MCP Bridge: Uncaught exception:', error);
});

console.error('MCP Bridge: Ready');