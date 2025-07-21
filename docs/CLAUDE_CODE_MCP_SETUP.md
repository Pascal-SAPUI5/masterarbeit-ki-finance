# Claude Code MCP Server Installation

## 1. MCP Server in Claude Code installieren

### Option A: Über die Claude Code Oberfläche

1. Öffnen Sie Claude Code
2. Gehen Sie zu **Settings** (Zahnrad-Icon)
3. Navigieren Sie zu **Developer** → **Edit Config** 
4. Fügen Sie folgende Konfiguration hinzu:

```json
{
  "mcpServers": {
    "masterarbeit-ki-finance": {
      "command": "/home/a503038/Projects/masterarbeit-ki-finance/start_mcp_server.sh",
      "cwd": "/home/a503038/Projects/masterarbeit-ki-finance",
      "env": {
        "PYTHONPATH": "/home/a503038/Projects/masterarbeit-ki-finance"
      }
    }
  }
}
```

### Option B: Über die Konfigurationsdatei

1. Öffnen Sie die Claude Code Konfigurationsdatei:
   - Linux/Mac: `~/.config/claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Fügen Sie die MCP Server Konfiguration hinzu:

```json
{
  "mcpServers": {
    "masterarbeit-ki-finance": {
      "command": "/home/a503038/Projects/masterarbeit-ki-finance/start_mcp_server.sh",
      "cwd": "/home/a503038/Projects/masterarbeit-ki-finance",
      "env": {
        "PYTHONPATH": "/home/a503038/Projects/masterarbeit-ki-finance"
      }
    }
  }
}
```

## 2. Claude Code neu starten

Nach dem Hinzufügen der Konfiguration:
1. Schließen Sie Claude Code komplett
2. Starten Sie Claude Code neu

## 3. MCP Server aktivieren

In Claude Code:
1. Öffnen Sie ein neues Gespräch
2. Tippen Sie `/` um die verfügbaren Befehle zu sehen
3. Nutzen Sie `/mcp` oder schauen Sie nach dem 🔌 Icon
4. Der Server "masterarbeit-ki-finance" sollte verfügbar sein

## 4. Tools nutzen

Nach erfolgreicher Installation können Sie die Tools direkt nutzen:

```
/search_literature query="SAP BTP AI capabilities"
/verify_citations text_file="test_citation_text.txt"
/search_documents query="explainable AI finance"
```

## Troubleshooting

### Server erscheint nicht
1. Prüfen Sie die Pfade in der Konfiguration
2. Stellen Sie sicher, dass `start_mcp_server.sh` ausführbar ist:
   ```bash
   chmod +x /home/a503038/Projects/masterarbeit-ki-finance/start_mcp_server.sh
   ```

### Server startet nicht
1. Testen Sie manuell:
   ```bash
   cd /home/a503038/Projects/masterarbeit-ki-finance
   ./start_mcp_server.sh
   ```
2. Prüfen Sie die Logs in Claude Code Developer Tools

### Tools nicht verfügbar
1. Nutzen Sie `/reload` in Claude Code
2. Prüfen Sie die mcp.json Syntax
3. Schauen Sie in die Developer Console für Fehler