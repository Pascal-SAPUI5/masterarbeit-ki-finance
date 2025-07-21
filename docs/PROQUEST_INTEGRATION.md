# ProQuest Integration Guide

## Überblick
ProQuest bietet mehrere APIs für den programmatischen Zugriff. Die empfohlene Methode ist die **SRU/XML Gateway API**, die ohne komplexe Authentifizierung funktioniert, wenn Ihre Universität IP-Whitelisting hat.

## Einrichtung

### 1. Verfügbare ProQuest APIs

**SRU/XML Gateway (EMPFOHLEN)**
- Endpoint: `http://fedsearch.proquest.com/search/sru/{database}`
- Keine Authentifizierung nötig (nur IP-Whitelisting)
- CQL-Abfragesprache, MARCXML-Response
- Beste Option für automatisierte Suchen

**RefWorks API**
- Vollständige Dokumentation: https://api.refworks.proquest.com/api-ipa/api-docs/
- OAuth-basiert, komplexere Integration
- Für Referenzverwaltung optimiert

**SAML/Shibboleth Login**
- Für Hochschule Burgenland: https://idp.hochschule-burgenland.at/
- Benötigt Browser-Automatisierung (Selenium)
- Nicht empfohlen für programmatischen Zugriff

### 2. .env Datei konfigurieren

**Empfohlene Konfiguration (SRU API):**
```env
# ProQuest SRU API - keine Anmeldung nötig!
PROQUEST_SRU_ENDPOINT=http://fedsearch.proquest.com/search/sru/
PROQUEST_DATABASE_CODES=pqdtglobal,abicomplete,pqdt

# Datenbank-Codes:
# pqdtglobal = Dissertations & Theses Global
# abicomplete = Academic Complete (E-Books)
# pqdt = ProQuest Dissertations & Theses
# academic = Academic OneFile
```

**Alternative für SAML-Login (nicht empfohlen):**
```env
# Nur falls SRU nicht funktioniert
PROQUEST_INSTITUTION_URL=https://idp.hochschule-burgenland.at/idp/profile/SAML2/Redirect/SSO
PROQUEST_USERNAME=ihre.kennung@hochschule-burgenland.at
PROQUEST_PASSWORD=ihr_passwort
```

### 3. Test der Verbindung
```bash
# Aktivieren Sie die virtuelle Umgebung
source venv/bin/activate

# Testen Sie ProQuest
python scripts/search_literature.py \
  --query "systematic literature review" \
  --databases ProQuest \
  --years "2020-2025"
```

## Unterstützte ProQuest Datenbanken

Die Integration durchsucht automatisch:
- **ProQuest Dissertations & Theses Global**
- **Academic Complete**
- **ABI/INFORM Collection** (Business)
- **ProQuest Central** (Multidisziplinär)
- **Technology Collection** (Informatik)
- **Health & Medical Collection**

## Features

### Automatische Qualitätsbewertung
- ✅ Peer-Review Status
- ✅ Volltext-Verfügbarkeit
- ✅ Publikationsjahr-Filter
- ✅ Sprach-Erkennung

### Export-Formate
```python
# Gefundene Artikel werden gespeichert mit:
- Titel, Autoren, Jahr
- Abstract
- DOI (falls vorhanden)
- ProQuest Document ID
- Peer-Review Status
```

## Troubleshooting

### "ProQuest not configured"
→ Prüfen Sie die .env Datei

### "Authentication failed"
→ Testen Sie Login manuell im Browser
→ 2FA aktiviert? Kontaktieren Sie IT

### Keine Ergebnisse
→ Andere Keywords versuchen
→ Jahresbereich erweitern

## Alternative: Manueller Export

Falls automatischer Login nicht funktioniert:

1. **ProQuest Webseite**
   - Manuell einloggen
   - Suche durchführen
   - Export als RIS/BibTeX

2. **Import in System**
   ```bash
   python scripts/manage_references.py \
     --import proquest_export.ris
   ```

## Erweiterte Nutzung

### Spezifische Sammlungen durchsuchen
```python
# In search_literature.py anpassen:
params = {
    "database": ["pqdtglobal", "abicomplete"],  # Specific collections
    "discipline": "computer science",
    "language": ["eng", "ger"]
}
```

### Batch-Suchen
```bash
# queries.txt erstellen:
# "AI agents banking"
# "retrieval augmented generation"
# "multi-agent systems finance"

for query in $(cat queries.txt); do
  python scripts/search_literature.py \
    --query "$query" \
    --databases ProQuest
done
```

## Datenschutz

- Zugangsdaten werden nur lokal in .env gespeichert
- Keine Weitergabe an Dritte
- .env ist in .gitignore (wird nicht versioniert)
- Bei öffentlichen Repos: Niemals committen!

## Support

Bei Problemen:
1. IT-Abteilung der Hochschule (ProQuest-Zugang)
2. GitHub Issues (technische Integration)
3. ProQuest Support (Datenbank-Fragen)