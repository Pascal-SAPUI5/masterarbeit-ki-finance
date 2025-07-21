#!/bin/bash
# Installiert den MCP Server in Claude Code

echo "🚀 MCP Server Installation für Claude Code"
echo "========================================"

# Projekt-Verzeichnis
PROJECT_DIR="$(pwd)"

# Claude Config Pfad ermitteln
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows
    CONFIG_DIR="$APPDATA/Claude"
else
    # Linux
    CONFIG_DIR="$HOME/.config/claude"
fi

CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

echo "📁 Projekt-Verzeichnis: $PROJECT_DIR"
echo "📄 Claude Config: $CONFIG_FILE"

# Prüfe ob Config-Verzeichnis existiert
if [ ! -d "$CONFIG_DIR" ]; then
    echo "❌ Claude Config-Verzeichnis nicht gefunden!"
    echo "   Bitte stellen Sie sicher, dass Claude Code installiert ist."
    exit 1
fi

# Backup der existierenden Config
if [ -f "$CONFIG_FILE" ]; then
    echo "📋 Erstelle Backup der existierenden Konfiguration..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# MCP Server Konfiguration
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "masterarbeit-ki-finance": {
      "command": "$PROJECT_DIR/start_mcp_server.sh",
      "cwd": "$PROJECT_DIR",
      "env": {
        "PYTHONPATH": "$PROJECT_DIR"
      }
    }
  }
}
EOF

# Start-Script ausführbar machen
chmod +x "$PROJECT_DIR/start_mcp_server.sh"

echo "✅ MCP Server erfolgreich installiert!"
echo ""
echo "📝 Nächste Schritte:"
echo "1. Claude Code neu starten"
echo "2. In einem neuen Chat '/mcp' eingeben"
echo "3. Server 'masterarbeit-ki-finance' sollte verfügbar sein"
echo ""
echo "🔧 Verfügbare Tools:"
echo "   - search_literature"
echo "   - verify_citations"
echo "   - search_documents"
echo "   - index_documents"
echo "   - get_context"
echo "   - und viele mehr..."
echo ""
echo "💡 Tipp: Nutzen Sie '/help' in Claude Code für mehr Informationen"