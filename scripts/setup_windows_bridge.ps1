# PowerShell script to setup Windows Claude Desktop integration with WSL2 MCP Server
# Run this script as Administrator in Windows

Write-Host "🚀 Setting up Windows Claude Desktop Bridge to WSL2..." -ForegroundColor Green

# Get WSL2 IP address
$wsl2IP = wsl hostname -I
if ($wsl2IP) {
    $wsl2IP = $wsl2IP.Trim().Split()[0]
    Write-Host "✅ WSL2 IP Address: $wsl2IP" -ForegroundColor Green
} else {
    Write-Host "❌ Could not get WSL2 IP address. Is WSL2 running?" -ForegroundColor Red
    exit 1
}

# Claude Desktop config path
$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"
$claudeConfigDir = Split-Path $claudeConfigPath -Parent

# Create directory if it doesn't exist
if (!(Test-Path $claudeConfigDir)) {
    New-Item -ItemType Directory -Path $claudeConfigDir -Force | Out-Null
    Write-Host "📁 Created Claude config directory" -ForegroundColor Yellow
}

# Create or update Claude config
$config = @{
    mcpServers = @{
        "masterarbeit-rag" = @{
            command = "node"
            args = @("$env:USERPROFILE\wsl-mcp-bridge.js", "http://${wsl2IP}:3001")
        }
    }
}

# Write config file
$config | ConvertTo-Json -Depth 4 | Set-Content $claudeConfigPath
Write-Host "✅ Updated Claude Desktop configuration" -ForegroundColor Green

# Create bridge script
$bridgeScript = @'
// WSL2 MCP Bridge for Windows
const http = require('http');
const https = require('https');

const wslUrl = process.argv[2];
if (!wslUrl) {
    console.error('Usage: node wsl-mcp-bridge.js <wsl-url>');
    process.exit(1);
}

console.error('Bridging MCP requests to: ' + wslUrl);

// Handle incoming MCP requests and forward to WSL2
process.stdin.on('data', async (data) => {
    try {
        const request = JSON.parse(data.toString());
        
        // Forward to WSL2 MCP server
        const response = await fetch(wslUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(request)
        });
        
        const result = await response.json();
        process.stdout.write(JSON.stringify(result) + '\n');
        
    } catch (error) {
        console.error('Bridge error: ' + error.message);
        process.stdout.write(JSON.stringify({ error: error.message }) + '\n');
    }
});
'@

$bridgeScript | Set-Content "$env:USERPROFILE\wsl-mcp-bridge.js"
Write-Host "✅ Created WSL-MCP bridge script" -ForegroundColor Green

# Configure Windows Firewall
Write-Host "`n🔥 Configuring Windows Firewall..." -ForegroundColor Yellow

# Add firewall rule for MCP port
$ruleName = "WSL2 MCP Server (Port 3001)"
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "⚠️ Firewall rule already exists" -ForegroundColor Yellow
} else {
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 3001 `
        -Action Allow `
        -Profile Any | Out-Null
    Write-Host "✅ Added firewall rule for port 3001" -ForegroundColor Green
}

# Add firewall rule for Ollama port
$ollamaRuleName = "WSL2 Ollama (Port 11434)"
$existingOllamaRule = Get-NetFirewallRule -DisplayName $ollamaRuleName -ErrorAction SilentlyContinue

if ($existingOllamaRule) {
    Write-Host "⚠️ Ollama firewall rule already exists" -ForegroundColor Yellow
} else {
    New-NetFirewallRule -DisplayName $ollamaRuleName `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 11434 `
        -Action Allow `
        -Profile Any | Out-Null
    Write-Host "✅ Added firewall rule for port 11434" -ForegroundColor Green
}

Write-Host "`n🎉 Windows Bridge Setup Complete!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Start services in WSL2: ./start_mcp_server.sh" -ForegroundColor White
Write-Host "2. Restart Claude Desktop application" -ForegroundColor White
Write-Host "3. Check MCP connection in Claude Desktop settings" -ForegroundColor White
Write-Host "`n💡 Test connection:" -ForegroundColor Yellow
Write-Host "curl http://${wsl2IP}:3001/health" -ForegroundColor White