# Masterarbeit KI-Finance: RAG-System & Forschungsautomatisierung

Automatisierte Forschungsumgebung für die Masterarbeit "Agile Prozessautomatisierung und Wissensmanagement durch KI-Agenten: Innovationspotenziale der SAP Business Technology Platform im Finanzwesen". Integriert Literatursuche, RAG-basierte Dokumentenanalyse und akademische Schreibhilfen.

## Projektübersicht

### Kernkomponenten
- **RAG-System**: CPU-basierte Dokumentensuche mit LLM-Integration (Ollama/phi3:mini)
- **Literaturverwaltung**: Automatisierte Suche in Q1-Journals mit Citavi-Integration
- **Research Assistant**: Gliederung, Templates und Fortschrittsverfolgung
- **Memory System**: Persistente Kontextspeicherung zwischen Sessions

### Architektur
- **MCP Server**: Stellt alle Funktionen als Tools für Claude Code bereit
- **Docker Stack**: PostgreSQL, Redis, Qdrant für Datenmanagement
- **Memory-basiert**: Projektkontext und Regeln werden dauerhaft gespeichert

## 🆕 Für neue Nutzer: Anpassung an Ihre Masterarbeit

**➡️ Siehe [ANPASSUNG_NEUE_MASTERARBEIT.md](ANPASSUNG_NEUE_MASTERARBEIT.md) für die vollständige Anleitung!**

Diese Vorlage ist für "KI-Agenten im Finanzwesen" konfiguriert. Für Ihr eigenes Thema müssen Sie:
- 6 Haupt-Konfigurationsdateien anpassen (ca. 2-3 Stunden)
- Ihre Gliederung, Keywords und Theorien eintragen
- Universitäts-spezifische Anforderungen konfigurieren

## Installation

### 1. Systemvoraussetzungen
- Linux/WSL mit Ubuntu 22.04+
- 16 GB RAM (32 GB empfohlen)
- Python 3.10+
- Git und Docker

### 2. Abhängigkeiten installieren
```bash
# Virtual Environment aktivieren
source venv/bin/activate

# Python Dependencies (CPU-optimiert)
pip install -r requirements.txt --constraint constraints.txt

# Ollama für LLM (optional aber empfohlen für intelligente Antworten)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve &
ollama pull phi3:mini  # 2.2 GB, CPU-optimiert
```

### 3. Projekt initialisieren
```bash
# Setup-Script ausführen (erstellt Verzeichnisse, lädt Modelle)
cd scripts && ./setup_research.sh

# Docker-Services starten
docker-compose up -d

# Memory System initialisieren
python memory_system.py init
```

## Nutzung

### 📚 Beispiel-Workflow: Methodenkapitel mit PRISMA-Framework

Angenommen, Sie schreiben: *"Das Methodenkapitel operationalisiert den Design-Science-Ansatz durch eine methodische Triangulation aus systematischer Literaturanalyse, semi-strukturierten Experteninterviews und prototypischer Implementierung. Die systematische Literaturanalyse folgt dem PRISMA-Framework und fokussiert auf peer-reviewed Publikationen der Jahre 2020-2025..."*

#### 1️⃣ **Literatursuche mit MCP Tools** (Claude Code führt aus)
```bash
# Claude nutzt search_literature Tool für PRISMA-konforme Suche
search_literature --query "PRISMA framework systematic literature review guidelines" \
                 --databases "IEEE Xplore, ACM Digital Library, ScienceDirect" \
                 --years "2020-2025" \
                 --quality "q1"

# Ergebnis: 15 relevante Papers gefunden, z.B.:
# - Moher et al. (2020): "PRISMA 2020 statement" 
# - Page et al. (2021): "The PRISMA 2020 statement: an updated guideline"
```

#### 2️⃣ **PDFs einbetten und indexieren**
```bash
# Papers herunterladen und in Projekt-Struktur ablegen
literatur/
├── methodik/
│   ├── Moher_2020_PRISMA_statement.pdf
│   ├── Page_2021_PRISMA_updated_guideline.pdf
│   └── Tricco_2022_PRISMA_extensions.pdf

# RAG-System indexiert Dokumente
python scripts/rag_system.py index --path literatur/methodik/ --cpu-only
# → Extrahiert Text, Metadaten, erstellt Embeddings
```

#### 3️⃣ **Präzise Zitationsstellen finden**
```bash
# Suche nach konkreten Aussagen für korrekte Zitation
python scripts/rag_system.py search \
  "PRISMA framework checklist items systematic review" --top-k 5

# Antwort mit Ollama/LLM:
{
  "answer": "Das PRISMA 2020 Framework definiert eine 27-Item Checkliste für systematische Reviews. Die Kern-Items umfassen: Title (Item 1), Abstract (Item 2), Introduction mit Rationale (Item 3) und Objectives (Item 4). Besonders wichtig für die Methodendarstellung sind Items 6-9, die Search Strategy, Selection Process, Data Collection und Study Risk of Bias Assessment beschreiben.",
  
  "sources": [{
    "information": "The PRISMA 2020 statement comprises a 27-item checklist addressing the introduction, methods, results and discussion sections of a systematic review report",
    "source": "Page et al., 2021, S. 3",
    "citation": "(Page et al., 2021, S. 3)",
    "context": "...The checklist items guide authors..."
  }]
}
```

#### 4️⃣ **Korrekte Zitation generieren**
```bash
# MCP Tool verify_citations prüft und formatiert
verify_citations --text "Die systematische Literaturanalyse folgt dem PRISMA-Framework" \
                --source "Page et al. 2021"

# Output:
"Die systematische Literaturanalyse folgt dem PRISMA-Framework (Page et al., 2021, S. 3)"

# Vollständige Referenz für Literaturverzeichnis:
"Page, M. J., McKenzie, J. E., Bossuyt, P. M., et al. (2021). The PRISMA 2020 statement: 
an updated guideline for reporting systematic reviews. BMJ, 372, n71."
```

#### 5️⃣ **Integration in Thesis-Dokument**
```bash
# Template mit korrekten Zitationen erstellen
python scripts/research_assistant.py template \
  --chapter "Methodik" \
  --section "Systematische Literaturanalyse" \
  --citations "Page2021,Moher2020"

# Citavi-Export für Literaturverzeichnis
python scripts/manage_references.py --export citavi \
  --papers "Page2021,Moher2020,Tricco2022"
```

### 🔄 Workflow-Diagramm

```
[Forschungsfrage] → [MCP: search_literature] → [15 Papers gefunden]
        ↓                                              ↓
[PDF Download] ← [Relevanz-Prüfung] ← [Quality Check: Q1 Journals]
        ↓
[RAG Indexierung] → [Embeddings] → [FAISS Vector DB]
        ↓
[Zitat-Suche] → [Ollama/LLM] → [Präzise Textstellen]
        ↓
[verify_citations] → [APA-Format] → [Integration in Thesis]
        ↓
[Citavi Export] → [Literaturverzeichnis]
```

### Forschungs-Workflow (Standard Commands)
```bash
# 1. Literatur durchsuchen
python scripts/search_literature.py --query "AI agents finance" --quality q1

# 2. Referenzen verwalten
python scripts/manage_references.py --import results.json --citavi

# 3. PDFs indizieren für RAG
python scripts/rag_system.py index --path literatur/finance/ --cpu-only

# 4. Dokumente durchsuchen (mit Ollama für intelligente Antworten)
python scripts/rag_system.py search "SAP BTP capabilities" --top-k 5
# Falls Ollama nicht läuft, automatischer Fallback zu Retrieval-only

# 5. Schreibvorlagen erstellen
python scripts/research_assistant.py template --chapter "Einleitung" --section "Problemstellung"
```

### Memory System Commands
```bash
# Kontext abrufen
python -c "from memory_system import get_memory; print(get_memory().get_context())"

# Notizen hinzufügen
python -c "from memory_system import get_memory; get_memory().add_note('Important finding')"

# Fortschritt aktualisieren
python scripts/research_assistant.py progress --update "Kapitel 2 fertig"

# Checkpoint erstellen
python -c "from memory_system import get_memory; get_memory().create_checkpoint('chapter2_complete')"
```

### RAG-System (Erweitert)
```bash
# GUI für interaktive Suche
python scripts/rag_gui.py --port 8501

# Batch-Verarbeitung
python scripts/rag_system.py batch --input queries.txt --output results.json

# Performance-Monitoring
python scripts/rag_system.py stats
```

## Konfiguration

### Wichtige Config-Dateien
- `config/research-criteria.yaml`: Q1-Journal Kriterien, Publikationsjahre
- `config/writing-style.yaml`: Deutsche MBA-Schreibrichtlinien
- `config/mba-standards.json`: Bewertungskriterien, Deadlines
- `config/rag_config.yaml`: RAG-System Parameter (LLM-Modell: phi3:mini)
- `.claude_memory/`: Persistenter Projektkontext

### API-Integration (Optional)
```bash
# .env Datei erstellen (nicht in Git)
cp .env.example .env
# Dann ausfüllen mit Ihren Zugangsdaten
```

**Datenbank-APIs:**
```env
SCOPUS_API_KEY=your_key
WOS_API_KEY=your_key
CROSSREF_EMAIL=ihre.email@uni.de  # Für höhere Rate Limits
```

## Projektstruktur
```
├── scripts/              # Hauptprogramme
│   ├── rag_system.py     # RAG-Kern
│   ├── search_literature.py
│   ├── manage_references.py
│   └── research_assistant.py
├── config/               # Konfigurationsdateien  
├── research/             # Validierte Literatur
├── writing/              # Templates und Drafts
├── memory_system.py      # Kontextpersistierung
├── mcp_server.py         # Claude Code Integration
└── docker-compose.yml    # Infrastructure
```

## Troubleshooting

### Häufige Probleme
- **CUDA nicht gefunden**: System nutzt automatisch CPU-Versionen (PyTorch+cpu, faiss-cpu)
- **Memory-Fehler**: Reduziere `chunk_size` in `config/rag_config.yaml`
- **Ollama Connection refused**: `ollama serve &` vor der Nutzung starten
- **Ollama command not found**: Nach Installation neue Shell öffnen oder `export PATH=$PATH:/usr/local/bin`
- **Citavi nicht gefunden**: Pfad in `config/api_keys.yaml` setzen

### Performance-Optimierung
```bash
# RAM-Überwachung
python -c "import psutil; print(f'RAM: {psutil.virtual_memory().percent}%')"

# Ollama Status prüfen
ollama list  # Zeigt geladene Modelle
curl -s http://localhost:11434/api/version  # Server-Status

# Modell-Cache löschen (bei Problemen)
rm -rf ~/.cache/huggingface/transformers/

# Index neu erstellen
rm -rf indexes/ && python scripts/rag_system.py index --path literatur/ --cpu-only
```

### Logs und Debugging
```bash
# Detaillierte Logs
export PYTHONPATH=$PWD && python scripts/rag_system.py search "test" --verbose

# Memory System Status
python memory_system.py status

# Docker Logs
docker-compose logs -f qdrant postgres redis
```

## Entwicklung

### MCP Server für Claude Code
Das Projekt funktioniert als MCP-Server für Claude Code. Verfügbare Tools:
- `search_literature` - Datenbanksuche
- `manage_references` - Citavi-Integration  
- `create_writing_template` - Strukturierte Templates
- `verify_citations` - Qualitätskontrolle
- Memory-Tools für Kontextpersistierung

### Tests ausführen
```bash
pytest tests/ -v
python scripts/rag_system.py test --self-test
black scripts/*.py  # Code-Formatierung
```

---
**Letztes Update**: Januar 2025 | **Status**: Aktive Entwicklung | **Python**: 3.10+ | **Lizenz**: Academic Use 