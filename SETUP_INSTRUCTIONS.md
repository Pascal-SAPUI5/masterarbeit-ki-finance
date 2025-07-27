# Setup-Anleitung für Masterarbeit KI Finance mit Claude Desktop

## 1. Docker Container starten

### Option A: Alle Services starten
```bash
# In WSL Terminal im Projektverzeichnis
cd /home/a503038/Projects/masterarbeit-ki-finance

# Alle Services starten
docker compose up -d

# Status prüfen
docker compose ps
```

### Option B: Nur benötigte Services starten
```bash
# Minimal Setup (nur MCP Server + Ollama)
docker compose up -d ollama mcp-server

# Mit Qdrant für RAG
docker compose up -d ollama qdrant mcp-server
```

## 2. Services überprüfen

```bash
# Container Status
docker ps

# MCP Server Logs prüfen
docker logs masterarbeit-mcp-server -f

# Ollama Status prüfen
docker logs masterarbeit-ollama

# Health Check
curl http://localhost:3001/health
```

## 3. Claude Desktop MCP Konfiguration (Windows Host)

### Schritt 1: MCP Konfigurationsdatei erstellen

Erstelle die Datei `%APPDATA%\Claude\claude_desktop_config.json` mit folgendem Inhalt:

```json
{
  "mcpServers": {
    "masterarbeit-ki-finance": {
      "command": "cmd",
      "args": [
        "/c",
        "curl",
        "-X",
        "POST",
        "-H",
        "Content-Type: application/json",
        "-d",
        "@-",
        "http://localhost:3001/mcp"
      ],
      "env": {}
    }
  }
}
```

### Alternative: Direkte HTTP Integration

```json
{
  "mcpServers": {
    "masterarbeit-ki-finance": {
      "url": "http://localhost:3001",
      "type": "http"
    }
  }
}
```

### Schritt 2: Claude Desktop neu starten

1. Claude Desktop vollständig beenden (System Tray prüfen)
2. Claude Desktop neu starten
3. In Claude Desktop sollte nun "masterarbeit-ki-finance" als MCP Server verfügbar sein

## 4. Troubleshooting

### Ollama Port Konflikt
Wenn Ollama bereits auf dem Host läuft:
```bash
# In docker-compose.yml ändern:
ports:
  - "11435:11434"  # Anderen Port verwenden
```

### MCP Server startet nicht
```bash
# Container neu bauen
docker compose build mcp-server

# Mit Logs starten
docker compose up mcp-server
```

### Verbindungsprobleme Windows → WSL
```bash
# WSL IP Adresse finden
ip addr show eth0

# In Windows PowerShell:
netsh interface portproxy add v4tov4 listenport=3001 listenaddress=0.0.0.0 connectport=3001 connectaddress=<WSL-IP>
```

### Firewall Regeln (Windows)
```powershell
# Als Administrator in PowerShell
New-NetFirewallRule -DisplayName "MCP Server" -Direction Inbound -Protocol TCP -LocalPort 3001 -Action Allow
```

## 5. Verfügbare MCP Tools

Nach erfolgreicher Konfiguration stehen folgende Tools zur Verfügung:

- `search_literature`: Literatursuche in akademischen Datenbanken
- `analyze_paper`: Paper-Analyse und Zusammenfassung
- `manage_references`: Referenzverwaltung
- `check_mba_quality`: MBA-Standards Überprüfung
- `generate_outline`: Kapitelstruktur generieren
- `write_chapter`: Kapitel schreiben
- `check_citations`: Zitationsprüfung

## 6. Test der Integration

In Claude Desktop:
```
/search_literature "AI in Finance"
```

Oder direkt testen:
```bash
curl -X POST http://localhost:3001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

## 7. Logs und Monitoring

```bash
# Alle Logs anzeigen
docker compose logs -f

# Nur MCP Server
docker logs masterarbeit-mcp-server -f

# Container Ressourcen
docker stats
```

## 8. Services stoppen

```bash
# Alle Services stoppen
docker compose down

# Einzelnen Service stoppen
docker compose stop mcp-server
```