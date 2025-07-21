# 🎓 Anpassungsanleitung für Ihre Masterarbeit

Diese Anleitung zeigt Schritt für Schritt, wie Sie das System für Ihre eigene Masterarbeit anpassen.

## ⚡ Quick Start - Die wichtigsten 6 Dateien

### 1. **`config/mba-standards.json`** - Universitäts-Einstellungen
```json
{
  "thesis_requirements": {
    "university": "Ihre Universität",  // ← ÄNDERN
    "program": "Ihr Studiengang",      // ← ÄNDERN (MBA, MSc, MA)
    "pages": {"min": 60, "max": 80},   // ← ANPASSEN
    "language": "de"                    // ← de/en
  },
  "deadlines": {
    "proposal_submission": "2025-02-15",  // ← IHRE DEADLINES
    "first_draft": "2025-04-30",
    "final_submission": "2025-06-30",
    "defense": "2025-07-15"
  },
  "supervisor": {
    "name": "Prof. Dr. Ihr Betreuer",    // ← ÄNDERN
    "email": "betreuer@uni.de"           // ← ÄNDERN
  },
  "evaluation_criteria": {
    // ← Bewertungskriterien Ihrer Uni eintragen
  }
}
```

### 2. **`config/research-criteria.yaml`** - Forschungskriterien
```yaml
keywords:
  primary:
    - "Ihr Hauptthema"          # ← ERSETZEN (statt "AI agents")
    - "Ihre Technologie"        # ← ERSETZEN (statt "SAP BTP")
    - "Ihr Anwendungsbereich"   # ← ERSETZEN (statt "finance")
  secondary:
    - "verwandte Begriffe"      # ← ANPASSEN
    
databases:
  - "Ihre Fachdatenbanken"      # ← Z.B. PubMed für Medizin

quality_criteria:
  impact_factor:
    minimum: 3.0                # ← Je nach Fachgebiet anpassen
```

### 3. **`config/writing-style.yaml`** - Ihre Gliederung
```yaml
structure:
  chapters:
    - number: 1
      title: "Einleitung"       # ← IHRE KAPITEL
      sections:
        - "Problemstellung"     # ← IHRE ABSCHNITTE
        - "Zielsetzung"
        - "Forschungsfragen"
    - number: 2
      title: "Ihr Theoriekapitel"  # ← KOMPLETT ERSETZEN
      sections:
        - "Ihre Theorie 1"
        - "Ihre Theorie 2"
    # ... weitere Kapitel
```

### 4. **`writing/thesis_outline.json`** - Detaillierte Gliederung
```json
{
  "title": "Ihr Masterarbeits-Titel",  // ← ERSETZEN
  "subtitle": "Ihr Untertitel",
  "chapters": [
    {
      "number": 1,
      "title": "Einleitung",
      "sections": ["Ihre Abschnitte"],
      "pages": 10,  // ← Seitenplanung
      "keywords": ["Ihre Keywords"]
    }
    // ... alle Kapitel definieren
  ]
}
```

### 5. **`.claude_memory/context.json`** - Projektkontext
```json
{
  "project_info": {
    "topic": "Ihr Thema",              // ← ÄNDERN
    "field": "Ihr Fachgebiet",         // ← ÄNDERN
    "university": "Ihre Uni",          // ← ÄNDERN
    "supervisor": "Ihr Betreuer"       // ← ÄNDERN
  },
  "current_state": {
    "phase": "research",               // ← Startphase
    "completed_chapters": [],          // ← Leer lassen
    "word_count": 0                    // ← Bei 0 starten
  }
}
```

### 6. **`mcp.json`** - Projekt-Metadaten
```json
{
  "name": "masterarbeit-ihr-thema",    // ← ÄNDERN
  "description": "MCP Server für Masterarbeit über [Ihr Thema]",  // ← ANPASSEN
  "author": "Ihr Name"                 // ← ÄNDERN
}
```

## 📝 Fachspezifische Anpassungen

### Für Informatik/Technik:
- IEEE-Datenbanken in `research-criteria.yaml` ergänzen
- Impact Factor ggf. auf 2.0 senken
- ACM Computing Classification hinzufügen

### Für Wirtschaftswissenschaften:
- SSRN, EconLit als Datenbanken
- Journal Rankings (A+, A, B) statt Impact Factor
- Case Study Struktur anpassen

### Für Naturwissenschaften:
- PubMed, Web of Science priorisieren
- Laborergebnisse-Kapitel hinzufügen
- Statistische Auswertung betonen

### Für Geisteswissenschaften:
- JSTOR, Project MUSE als Quellen
- Qualitative Methoden-Templates
- Hermeneutische Analyse-Struktur

## 🔧 Erweiterte Anpassungen

### Theoretischer Rahmen (WICHTIG!)
In `config/mba-standards.json`:
```json
"theoretical_foundations": {
  "core_theories": {
    "primary_framework": "Ihre Haupttheorie",  // ← Z.B. "Grounded Theory"
    "application": "Wie Sie es anwenden"
  },
  "supporting_theories": [
    "Theorie 1",
    "Theorie 2"
  ],
  "mandatory_q1_literature": [
    // Grundlegende Papers Ihres Fachgebiets
  ]
}
```

### Sprache ändern (für englische Arbeiten)
1. In allen Config-Dateien: `"language": "en"`
2. Deutsche Überschriften ersetzen:
   - "Einleitung" → "Introduction"
   - "Zielsetzung" → "Objectives"
   - "Forschungsfragen" → "Research Questions"

### Zitationsstil ändern
In `config/research-criteria.yaml`:
```yaml
citation:
  style: "harvard"  # statt "apa7"
  # oder: "ieee", "chicago", "mla"
```

## 🚀 Schritt-für-Schritt Vorgehen

### Tag 1: Basis-Setup
```bash
# 1. Projekt klonen
git clone <repository> masterarbeit-mein-thema
cd masterarbeit-mein-thema

# 2. Virtuelle Umgebung
python -m venv venv
source venv/bin/activate

# 3. Dependencies
pip install -r requirements.txt --constraint constraints.txt
```

### Tag 2: Konfiguration anpassen
1. **Öffnen Sie alle 6 Quick-Start Dateien**
2. **Suchen & Ersetzen**:
   - "KI-Agenten" → Ihr Thema
   - "Finanzwesen" → Ihr Bereich
   - "SAP BTP" → Ihre Technologie
3. **Deadlines eintragen**
4. **Betreuer-Info hinzufügen**

### Tag 3: Erste Nutzung
```bash
# Ollama starten
ollama serve &

# Erste Literatursuche mit Ihren Keywords
python scripts/search_literature.py --query "Ihre Keywords" --quality q1

# Memory initialisieren
python memory_system.py init

# Kontext prüfen
python -c "from memory_system import get_memory; print(get_memory().get_context())"
```

## 🎯 Checkliste vor dem Start

- [ ] Alle 6 Quick-Start Dateien angepasst
- [ ] Thema überall ersetzt (auch in Python-Scripts)
- [ ] Deadlines eingetragen
- [ ] Gliederung komplett definiert
- [ ] Theoretischer Rahmen festgelegt
- [ ] Suchbegriffe definiert
- [ ] Betreuer-Info hinzugefügt
- [ ] Alte Daten gelöscht:
  ```bash
  rm -rf research/search-results/*
  rm -rf backups/*
  rm -rf .claude_memory/notes.json
  rm -rf indexes/*
  ```

## ⚠️ Häufige Fehler vermeiden

1. **Nicht vergessen**: SAP BTP, Finance, Banking Referenzen entfernen
2. **Theorien anpassen**: TOE Framework durch Ihre Theorien ersetzen
3. **Sprache konsistent**: Entweder alles Deutsch oder alles Englisch
4. **Impact Factor**: An Ihr Fachgebiet anpassen (Medizin: 5+, Informatik: 2+)
5. **Kapitelstruktur**: Muss in allen Config-Dateien identisch sein

## 💡 Tipp: Backup erstellen

Nach der Anpassung:
```bash
python -c "from memory_system import get_memory; get_memory().create_checkpoint('initial_setup')"
```

Dann können Sie jederzeit zurück:
```bash
python -c "from memory_system import get_memory; get_memory().restore_checkpoint('initial_setup')"
```

---
**Geschätzte Zeit für vollständige Anpassung: 2-3 Stunden**

Bei Fragen: Nutzen Sie Claude Code mit dem Befehl "Hilf mir, das System für meine Masterarbeit über [Ihr Thema] anzupassen"