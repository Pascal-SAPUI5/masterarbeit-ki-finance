# Bereinigte Projekt-Struktur

## 📁 Hauptverzeichnisse

### `/config`
- `mba-standards.json` - MBA Bewertungskriterien
- `research-criteria.yaml` - Qualitätskriterien für Literatur
- `writing-style.yaml` - Akademische Schreibrichtlinien

### `/scripts`
- `search_literature.py` - Literatursuche
- `manage_references.py` - Referenzverwaltung
- `research_assistant.py` - Forschungsassistent
- `citation_quality_control.py` - Zitationsprüfung
- `utils.py` - Hilfsfunktionen

### `/research`
- `validated-literature.json` - Geprüfte Quellen
- `q1-sources/` - Q1-Journal Artikel
- `search-results/` - Suchergebnisse
- `quality_reports/` - Qualitätsberichte

### `/writing`
- `templates/` - Schreibvorlagen
- `chapters/` - Fertige Kapitel
- `drafts/` - Entwürfe
- `thesis_outline.json` - Gliederung

### `/output`
- Finale Dokumente (DOCX, PDF)
- Citavi-Exporte (RIS, BIB)

### `/windows-setup`
- Claude Desktop Konfiguration für Windows

## 🔧 Kern-Dateien

- `mcp_server.py` - MCP-Server Hauptdatei
- `mcp_server_claude.py` - Claude-spezifischer Server
- `memory_system.py` - Persistentes Memory
- `CLAUDE.md` - Projekt-Regeln
- `docker-compose.yml` - Docker-Konfiguration

## ✅ Bereinigt

- ✓ Alle Test-Dateien gelöscht
- ✓ Doppelte Konfigurationsdateien entfernt
- ✓ Temporäre Dokumentation gelöscht
- ✓ Überflüssige Python-Scripts entfernt

Das Projekt ist jetzt sauber strukturiert und bereit für die Framework-Implementierung!