# Claude Desktop Regelwerk für Masterarbeit KI-Finance MCP Tools

## 🎯 Zweck
Dieses Regelwerk definiert, wie Claude Desktop die MCP Tools für die Masterarbeit "KI-Agenten im Finanzsektor" korrekt nutzt und Research-Platzhalter systematisch befüllt.

## 📋 Verfügbare MCP Tools

### 1. **search_literature**
- **Zweck**: Sucht wissenschaftliche Literatur in Q1-Journals
- **Parameter**: 
  - `keywords`: Array von Suchbegriffen
  - `max_results`: Maximale Anzahl (Standard: 50)

### 2. **check_progress**
- **Zweck**: Zeigt aktuellen Fortschritt der Masterarbeit
- **Rückgabe**: Kapitel, Abschnitte, Completion-Status

### 3. **create_writing_template**
- **Zweck**: Erstellt Schreibvorlagen für Kapitel/Abschnitte
- **Parameter**: `chapter`, `section`

### 4. **get_context**
- **Zweck**: Liefert Projektkontext und MBA-Standards
- **Parameter**: `include_rules`, `include_progress`

### 5. **add_note**
- **Zweck**: Speichert Notizen und Erkenntnisse
- **Parameter**: `note`, `category`

## 🔍 Research-Platzhalter Identifikation

### Erkennungsmuster
Claude soll folgende Muster in Dokumenten erkennen und befüllen:
- `[Research Needed: ...]`
- `[Literatur erforderlich: ...]`
- `[TODO: Research ...]`
- `[Quelle benötigt: ...]`

### Systematisches Vorgehen

1. **Platzhalter identifizieren**
   ```
   Wenn [Research Needed: X] gefunden:
   1. Extrahiere Thema X
   2. Bestimme relevante Keywords
   3. Führe Literatursuche durch
   ```

2. **Literatursuche durchführen**
   ```
   search_literature({
     "keywords": ["extrahierte", "relevante", "begriffe"],
     "max_results": 20
   })
   ```

3. **Ergebnisse verarbeiten**
   - Sortiere nach Relevanz und Quartil (Q1 bevorzugt)
   - Prüfe Aktualität (idealerweise 2020-2024)
   - Validiere Zitationszahl

4. **Platzhalter ersetzen**
   ```
   Original: [Research Needed: Systematic literature review methodology for AI/finance research]
   
   Ersetzt durch:
   Aktuelle Forschung zeigt verschiedene Ansätze für systematische Literaturreviews im Bereich AI/Finance:
   - Smith et al. (2023) entwickelten ein Framework speziell für KI-Anwendungen im Finanzsektor
   - Johnson & Lee (2022) präsentieren eine hybride Methodik für interdisziplinäre Reviews
   - Wagner (2024) bietet Best Practices für die Qualitätssicherung in Finance-AI Reviews
   ```

## 📝 Formatierungsregeln

### Zitierweise
```
Autor et al. (Jahr) für Fließtext
(Autor et al., Jahr) für Referenzen am Satzende
```

### Quellenintegration
- Mindestens 3-5 hochwertige Quellen pro Research-Platzhalter
- Bevorzuge Q1-Journals und aktuelle Publikationen
- Integriere sowohl theoretische als auch praktische Quellen

### Verbesserungsvorschläge
Im unteren Abschnitt eines Dokuments darf Claude Verbesserungen vorschlagen:
```
[Verbesserung: Erwägen Sie die Integration von Blockchain-spezifischen KI-Agenten 
als zusätzliche Fallstudie, da dies ein aufstrebendes Forschungsgebiet ist]

[Verbesserung: Die Methodik könnte durch ein Mixed-Methods-Design gestärkt werden, 
das quantitative Performance-Metriken mit qualitativen Experteninterviews kombiniert]
```

## 🔄 Workflow für Research-Tasks

### 1. Dokumentanalyse
```python
# Pseudo-Code für Claude's Vorgehen
1. get_context(include_progress=True)
2. Identifiziere alle [Research Needed] Marker
3. Kategorisiere nach Themenbereich
```

### 2. Systematische Suche
```python
für jeden research_marker:
    keywords = extrahiere_keywords(marker.text)
    results = search_literature(keywords, max_results=30)
    
    gefilterte_results = filter(
        results,
        quartil="Q1",
        jahr>=2020,
        zitationen>=10
    )
    
    fülle_platzhalter(marker, gefilterte_results)
```

### 3. Qualitätssicherung
- Prüfe Kohärenz der eingefügten Literatur
- Stelle sicher, dass Quellen zum Kontext passen
- Validiere akademische Standards

## 🎯 Best Practices

### DO's ✅
1. **Immer Kontext abrufen** bevor Research beginnt
   ```
   get_context(include_rules=True, include_progress=True)
   ```

2. **Fortschritt dokumentieren**
   ```
   add_note({
     "note": "20 Quellen für Kapitel 2.1 integriert",
     "category": "progress"
   })
   ```

3. **Iterativ arbeiten**
   - Erst grobe Suche, dann verfeinern
   - Keywords basierend auf ersten Ergebnissen anpassen

4. **Quellen validieren**
   - Peer-Review Status prüfen
   - Impact Factor berücksichtigen
   - Aktualität sicherstellen

### DON'Ts ❌
1. **Keine minderwertigen Quellen** (nicht peer-reviewed, veraltet)
2. **Keine Überladung** (max. 10 Quellen pro Platzhalter)
3. **Keine thematischen Abweichungen**
4. **Keine Duplikate** über verschiedene Platzhalter

## 📊 Metriken für Erfolg

### Quantitative Kriterien
- Mindestens 80% der Platzhalter befüllt
- Durchschnittlich 5 Q1-Quellen pro Platzhalter
- 90% der Quellen aus 2020-2024

### Qualitative Kriterien
- Thematische Kohärenz
- Argumentative Stringenz
- Akademische Rigorosität

## 🔧 Spezielle Anweisungen

### Für theoretische Kapitel (2-3)
- Fokus auf Grundlagenwerke und Reviews
- Balance zwischen Klassikern und aktueller Forschung
- Definitionen und Konzepte priorisieren

### Für praktische Kapitel (5-6)
- Case Studies und Implementierungsbeispiele
- Industry Reports und Whitepapers ergänzen
- Praktische Frameworks einbeziehen

### Für Methodik (Kapitel 4)
- Methodologische Standards
- Vergleichbare Studien
- Validierungsansätze

## 🚀 Automatisierung

Claude sollte bei jedem Dokument:
1. Automatisch nach Research-Platzhaltern scannen
2. Proaktiv Literatursuche vorschlagen
3. Fortschritt in Notizen dokumentieren
4. Verbesserungsvorschläge am Ende anfügen

## 📝 Beispiel-Workflow

```
User: "Bitte fülle die Research-Platzhalter in Kapitel 2.1"

Claude:
1. get_context() → Verstehe Projektstand
2. create_writing_template("2", "2.1") → Hole Template
3. Identifiziere: [Research Needed: KI-Agent Definitionen]
4. search_literature(["AI agents", "definition", "autonomous systems"])
5. Integriere: "Nach Wooldridge (2022) sind KI-Agenten..."
6. add_note("5 Q1-Quellen für KI-Agent Definitionen integriert")
7. [Verbesserung: Erwägen Sie die Ergänzung um Multi-Agent-System Definitionen]
```

## 🎓 MBA-Standards Integration

Bei allen Research-Aktivitäten müssen die MBA-Bewertungskriterien berücksichtigt werden:
- **Wissenschaftlichkeit**: Nur peer-reviewed Quellen
- **Aktualität**: Bevorzugung neuester Forschung
- **Praxisrelevanz**: Balance Theorie/Praxis
- **Kritische Reflexion**: Pro/Contra Argumente

---

*Dieses Regelwerk ist ein lebendes Dokument und sollte basierend auf Erfahrungen und Feedback kontinuierlich verbessert werden.*