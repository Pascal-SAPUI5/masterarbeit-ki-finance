# MCP Server Architektur

## Übersicht

Das Projekt nutzt eine geschichtete MCP-Server-Architektur für die Integration mit Claude Code:

```
mcp_server_claude.py    ← Haupteinstiegspunkt (JSON-RPC 2.0)
        ↓
mcp_server.py          ← Core Business Logic (alle Tools)
        ↓
mcp_server_rag_extension.py ← RAG-spezifische Funktionen
```

## Dateien und ihre Funktionen

### 1. `mcp_server_claude.py` (Hauptserver)
- **Rolle**: JSON-RPC 2.0 Wrapper für Claude Code
- **Funktion**: 
  - Übersetzt zwischen Claude's JSON-RPC und internem Format
  - Sendet Initialisierungsnachricht beim Start
  - Wird von `start_mcp_server.sh` ausgeführt
- **Status**: ✅ Aktiv und federführend

### 2. `mcp_server.py` (Core-Implementierung)
- **Rolle**: Enthält die gesamte Business-Logik
- **Funktion**:
  - Definiert alle verfügbaren Tools
  - Integriert mit Memory System
  - Verwaltet Ressourcen und Prompts
  - Koordiniert alle Projektkomponenten
- **Status**: ✅ Aktiv als Abhängigkeit

### 3. `mcp_server_rag_extension.py` (RAG-Erweiterung)
- **Rolle**: Spezialisierte RAG-Funktionen
- **Funktion**:
  - PDF-Extraktion und Indexierung
  - Dokumentensuche mit Embeddings
  - Integration mit Ollama LLM
  - RAG-System-Statistiken
- **Status**: ✅ Aktiv als Erweiterung

## Verfügbare Tools

### Forschungs-Tools
- `search_literature` - Akademische Datenbanksuche
- `manage_references` - Citavi-Integration
- `verify_citations` - Zitationsprüfung

### RAG-Tools
- `search_documents` - Intelligente Dokumentensuche
- `index_documents` - PDF-Indexierung
- `extract_pdf_content` - PDF-Text-Extraktion
- `get_rag_stats` - System-Statistiken

### Schreib-Tools
- `create_writing_template` - Kapitel-Templates
- `check_progress` - Fortschrittsübersicht
- `update_progress` - Status-Updates

### Memory-Tools
- `get_context` - Projektkontext abrufen
- `add_note` - Notizen hinzufügen
- `memory_checkpoint` - Checkpoints verwalten

### Weitere Tools
- `backup_project` - Projekt-Backups
- `check_mba_compliance` - MBA-Standards prüfen
- `generate_outline` - Gliederung erstellen
- `generate_summary` - Zusammenfassung generieren

## Starten des Servers

```bash
# Empfohlene Methode
./start_mcp_server.sh

# Alternative (manuell)
source venv/bin/activate
export PYTHONPATH=$PWD
python mcp_server_claude.py
```

## Konfiguration

- **mcp.json**: Tool-Definitionen für Claude Code
- **config/*.yaml**: Projektspezifische Einstellungen
- **.env**: API-Keys und Credentials

## Wichtige Hinweise

1. **Keine direkte Ausführung** von `mcp_server.py` oder `mcp_server_rag_extension.py`
2. **Immer** `mcp_server_claude.py` als Einstiegspunkt verwenden
3. **Virtual Environment** muss aktiviert sein
4. **PYTHONPATH** muss auf Projektroot zeigen

## Fehlersuche

### Server startet nicht
```bash
# Prüfe Virtual Environment
which python  # Sollte in venv/ zeigen

# Prüfe Dependencies
pip list | grep -E "(torch|faiss|sentence-transformers)"

# Teste manuell
python -c "from mcp_server import MasterarbeitMCPServer; print('OK')"
```

### RAG-System nicht verfügbar
```bash
# Prüfe Ollama
ollama list
curl http://localhost:11434/api/version

# Teste RAG-Extension
python -c "from mcp_server_rag_extension import MCPRAGExtension; print('OK')"
```

### Tools nicht sichtbar in Claude
1. Prüfe `mcp.json` Syntax
2. Stelle sicher, dass Server läuft
3. Nutze `/load` in Claude Code