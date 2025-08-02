// Test script to debug the bridge
const http = require('http');

const testUrl = 'http://localhost:3001/mcp';

// Test initialize request
const testRequest = {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: {}
};

console.log('Testing URL:', testUrl);
console.log('Request:', JSON.stringify(testRequest, null, 2));

const url = new URL(testUrl);
const data = JSON.stringify(testRequest);

const options = {
    hostname: url.hostname,
    port: url.port || 80,
    path: url.pathname,
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data)
    }
};

const req = http.request(options, (res) => {
    console.log('\nStatus Code:', res.statusCode);
    console.log('Headers:', res.headers);
    
    let body = '';
    res.on('data', (chunk) => {
        body += chunk;
    });
    
    res.on('end', () => {
        console.log('\nRaw Response:', body);
        try {
            const parsed = JSON.parse(body);
            console.log('\nParsed Response:', JSON.stringify(parsed, null, 2));
        } catch (e) {
            console.log('\nFailed to parse JSON:', e.message);
        }
    });
});

req.on('error', (error) => {
    console.error('\nRequest Error:', error.message);
});

req.write(data);
req.end();