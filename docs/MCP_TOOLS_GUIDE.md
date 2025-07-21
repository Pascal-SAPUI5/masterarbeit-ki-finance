# MCP Tools Guide - Masterarbeit KI Finance

Diese Anleitung erklärt, wie Claude Code die MCP-Tools für Ihre Forschung nutzt.

## 🔧 Verfügbare Tools

### 1. **search_literature** - Akademische Literatursuche
```python
# Beispiel: PRISMA-Framework suchen
result = search_literature(
    query="PRISMA framework systematic review guidelines",
    databases=["IEEE Xplore", "ACM Digital Library"],
    years="2020-2025",
    quality="q1"
)
# Findet: Page et al. (2021), Moher et al. (2020), etc.
```

### 2. **rag_search** - Intelligente PDF-Suche mit KI
```python
# Nutzt automatisch Ollama/phi3:mini für Antwortgenerierung
result = rag_search(
    query="PRISMA 2020 checklist items for systematic review",
    top_k=5
)
# Gibt KI-generierte Zusammenfassung + exakte Quellenstellen
```

### 3. **verify_citations** - Zitationsprüfung & Formatierung
```python
result = verify_citations(
    text="Die systematische Literaturanalyse folgt dem PRISMA-Framework",
    source="Page et al. 2021"
)
# Output: "...PRISMA-Framework (Page et al., 2021, S. 3)"
```

### 4. **create_writing_template** - Schreibvorlagen
```python
template = create_writing_template(
    chapter="Methodik",
    section="Systematische Literaturanalyse"
)
# Erstellt: writing/templates/Methodik_Systematische_Literaturanalyse.md
```

### 5. **manage_references** - Referenzverwaltung
```python
# Importieren aus Suchergebnissen
manage_references(action="import", source="search_results_20250121.json")

# Export für Citavi
manage_references(action="export", format="citavi")

# Referenz finden
manage_references(action="find", source="PRISMA 2020")
```

### 6. **Memory System Tools**
```python
# Kontext abrufen
get_context()  # Zeigt: Projektphase, Fortschritt, Deadlines, Regeln

# Notiz hinzufügen
add_note("Wichtig: PRISMA-Checkliste hat 27 Items, nicht 22")

# Fortschritt aktualisieren
update_progress(chapter="Methodik", section="Forschungsdesign", status="completed")

# Fortschritt prüfen
check_progress()  # Zeigt: 45% fertig, nächste Deadline in 25 Tagen
```

### 7. **index_documents** - PDFs für RAG vorbereiten
```python
index_documents(path="literatur/methodik/")
# Indexiert alle PDFs im Verzeichnis für spätere Suche
```

## 🔄 Typischer Workflow

### Beispiel: PRISMA-Kapitel schreiben

1. **Literatur suchen:**
   ```
   Claude: "Ich nutze search_literature für PRISMA-Guidelines..."
   → Findet 15 relevante Q1-Papers
   ```

2. **PDFs indexieren:**
   ```
   Claude: "Ich indexiere die heruntergeladenen Papers..."
   → index_documents("literatur/methodik/")
   ```

3. **Spezifische Infos finden:**
   ```
   Claude: "Ich suche die 27-Item Checkliste..."
   → rag_search("PRISMA 2020 checklist 27 items")
   → KI: "Die PRISMA 2020 Checkliste umfasst 27 Items..."
   ```

4. **Zitation formatieren:**
   ```
   Claude: "Ich formatiere die Zitation korrekt..."
   → verify_citations(text="...", source="Page 2021")
   → "(Page et al., 2021, S. 3)"
   ```

5. **Template erstellen:**
   ```
   Claude: "Ich erstelle eine Vorlage für diesen Abschnitt..."
   → create_writing_template("Methodik", "PRISMA-Framework")
   ```

## 🤖 Automatische Features

### Ollama/phi3:mini Integration
- **Automatisch aktiv**: Wenn Ollama läuft, nutzt RAG-Search phi3:mini
- **Intelligente Antworten**: Fasst Suchergebnisse zusammen
- **Fallback**: Ohne Ollama → nur Dokumenten-Retrieval
- **Konfiguration**: `config/rag_config.yaml` → `llm_model: "phi3:mini"`

### Qualitätskontrolle
- Nur Q1-Journals (Impact Factor > 3.0)
- Publikationsjahre 2020-2025
- Automatische APA-Formatierung
- Citavi-kompatible Exporte

### Memory-Persistenz
- Alle Änderungen werden gespeichert
- Kontext bleibt zwischen Sessions erhalten
- Fortschritt wird automatisch getrackt
- Regeln werden durchgesetzt

## 💡 Tipps für Nutzer

1. **Starten Sie Ollama** für beste Ergebnisse:
   ```bash
   ollama serve &
   ```

2. **Fragen Sie spezifisch**:
   - ❌ "Suche etwas über PRISMA"
   - ✅ "Finde die 27-Item Checkliste aus PRISMA 2020 mit Seitenzahlen"

3. **Nutzen Sie den Kontext**:
   ```
   "Was ist der aktuelle Stand meiner Arbeit?"
   → Claude nutzt get_context() automatisch
   ```

4. **Batch-Operationen**:
   ```
   "Indexiere alle PDFs im Literatur-Ordner"
   → Claude findet alle Unterordner und indexiert systematisch
   ```

## 🚀 Quick Start

```bash
# 1. MCP Server ist bereits konfiguriert in Claude Desktop

# 2. In Claude Code:
"Suche aktuelle Literatur über AI Agents in Finance und erstelle eine Übersicht"

# Claude wird automatisch:
- search_literature nutzen
- Relevante Papers finden
- PDFs indexieren (wenn vorhanden)
- Zusammenfassung mit korrekten Zitationen erstellen
- Fortschritt aktualisieren
```

---
**Hinweis**: Alle Tools sind über den MCP-Server verfügbar. Claude Code erkennt automatisch, welches Tool für Ihre Anfrage am besten geeignet ist.