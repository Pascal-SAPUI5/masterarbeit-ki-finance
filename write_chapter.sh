#!/bin/bash
# write_chapter.sh - Automatisierter Workflow für Masterarbeit Chapter Writing
# =============================================================================

# Farben für Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Projekt Root
PROJECT_ROOT="/home/a503038/Projects/masterarbeit-ki-finance"
cd "$PROJECT_ROOT"

echo -e "${BLUE}=== Masterarbeit Chapter Writing Workflow ===${NC}"
echo -e "${BLUE}Timestamp: $(date)${NC}\n"

# 1. Virtuelle Umgebung aktivieren
echo -e "${YELLOW}[1/8] Aktiviere virtuelle Umgebung...${NC}"
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtuelle Umgebung aktiviert${NC}"
else
    echo -e "${RED}✗ Virtuelle Umgebung nicht gefunden! Erstelle neue...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# 2. MCP Server starten (Port 3000)
echo -e "\n${YELLOW}[2/8] Starte MCP Server auf Port 3000...${NC}"
# Kill existing MCP process on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start MCP server in background
npx claude-flow@alpha mcp start --port 3000 > mcp_server.log 2>&1 &
MCP_PID=$!
echo -e "${GREEN}✓ MCP Server gestartet (PID: $MCP_PID)${NC}"
sleep 3

# 3. Prüfe Docker Container Status
echo -e "\n${YELLOW}[3/8] Prüfe Docker Container Status...${NC}"

# Qdrant
QDRANT_STATUS=$(docker inspect -f '{{.State.Health.Status}}' masterarbeit-qdrant 2>/dev/null || echo "not running")
if [ "$QDRANT_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✓ Qdrant: healthy${NC}"
else
    echo -e "${YELLOW}! Qdrant Status: $QDRANT_STATUS - Versuche Neustart...${NC}"
    docker restart masterarbeit-qdrant
    sleep 10
    QDRANT_STATUS=$(docker inspect -f '{{.State.Health.Status}}' masterarbeit-qdrant 2>/dev/null || echo "failed")
    echo -e "  Qdrant nach Neustart: $QDRANT_STATUS"
fi

# Ollama
OLLAMA_CONTAINER="masterarbeit-ollama"
if docker ps -a --format "{{.Names}}" | grep -q "^${OLLAMA_CONTAINER}$"; then
    OLLAMA_STATUS=$(docker inspect -f '{{.State.Status}}' "$OLLAMA_CONTAINER" 2>/dev/null || echo "not found")
    if [ "$OLLAMA_STATUS" = "running" ]; then
        # Check if Ollama service is responding
        if curl -s -f http://localhost:11434/api/tags > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Ollama: running and healthy${NC}"
            # Check if phi3:mini model is available
            PHI3_CHECK=$(curl -s http://localhost:11434/api/tags | grep -o '"phi3:mini"' || echo "")
            if [ -n "$PHI3_CHECK" ]; then
                echo -e "${GREEN}  ✓ phi3:mini model available${NC}"
            else
                echo -e "${YELLOW}  ! phi3:mini model not found, pulling...${NC}"
                docker exec "$OLLAMA_CONTAINER" ollama pull phi3:mini
            fi
        else
            echo -e "${YELLOW}! Ollama container running but service not responding${NC}"
            echo -e "  Versuche Neustart..."
            docker restart "$OLLAMA_CONTAINER"
            sleep 10
            if curl -s -f http://localhost:11434/api/tags > /dev/null 2>&1; then
                echo -e "${GREEN}  ✓ Ollama service recovered${NC}"
            else
                echo -e "${RED}  ✗ Ollama service still not responding${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}! Ollama Status: $OLLAMA_STATUS - Versuche Start...${NC}"
        docker start "$OLLAMA_CONTAINER" 2>/dev/null || {
            echo -e "${RED}✗ Konnte Ollama nicht starten${NC}"
            echo -e "${YELLOW}Tipp: Starte Ollama manuell mit: docker run -d --name ollama -p 11434:11434 ollama/ollama${NC}"
        }
    fi
else
    echo -e "${RED}✗ Ollama Container nicht gefunden${NC}"
    echo -e "${YELLOW}Tipp: Installiere Ollama mit: docker run -d --name ollama -p 11434:11434 ollama/ollama${NC}"
fi

# 4. RAG Index Status prüfen
echo -e "\n${YELLOW}[4/8] Prüfe RAG Index Status...${NC}"
if [ -f "indexes/faiss_index" ]; then
    INDEX_SIZE=$(du -h indexes/faiss_index | cut -f1)
    INDEX_DATE=$(date -r indexes/faiss_index "+%Y-%m-%d %H:%M:%S")
    echo -e "${GREEN}✓ RAG Index vorhanden (Größe: $INDEX_SIZE, Letzte Änderung: $INDEX_DATE)${NC}"
else
    echo -e "${RED}✗ RAG Index nicht gefunden!${NC}"
fi

# 5. Chapter auswählen
echo -e "\n${YELLOW}[5/8] Verfügbare Kapitel:${NC}"
echo "1) Einleitung"
echo "2) Theoretische Grundlagen"
echo "3) Stand der Forschung"
echo "4) Methodologie"
echo "5) Implementierung"
echo "6) Evaluation"
echo "7) Diskussion"
echo "8) Fazit und Ausblick"
echo -n "Wähle Kapitel (1-8) oder 'all' für alle: "
read CHAPTER_CHOICE

# 6. Qualitätsstufe wählen
echo -e "\n${YELLOW}[6/8] Qualitätsstufe:${NC}"
echo "1) Draft (schnell, erste Version)"
echo "2) Standard (normale Qualität)"
echo "3) High Quality (mit umfassender Recherche)"
echo -n "Wähle Qualitätsstufe (1-3): "
read QUALITY_CHOICE

case $QUALITY_CHOICE in
    1) QUALITY="draft" ;;
    2) QUALITY="standard" ;;
    3) QUALITY="high" ;;
    *) QUALITY="standard" ;;
esac

# 7. Chapter schreiben
echo -e "\n${YELLOW}[7/8] Starte Chapter Writing Process...${NC}"

# Memory System Update
python3 -c "
from memory_system import get_memory
memory = get_memory()
memory.add_important_note('Chapter Writing gestartet - Kapitel: $CHAPTER_CHOICE, Qualität: $QUALITY')
memory.save_context({'current_state': {'phase': 'writing', 'current_chapter': '$CHAPTER_CHOICE'}})
"

# Hauptcommand basierend auf Auswahl
if [ "$CHAPTER_CHOICE" = "all" ]; then
    echo -e "${BLUE}Schreibe alle Kapitel mit Qualität: $QUALITY${NC}"
    
    # Verwende Claude Flow Swarm für parallele Bearbeitung
    npx claude-flow@alpha swarm init --topology hierarchical --agents 8
    npx claude-flow@alpha swarm run "Schreibe alle 8 Kapitel der Masterarbeit über AI Agents in Finance. Qualität: $QUALITY. Nutze RAG-System für Quellen."
else
    CHAPTER_NAME=""
    case $CHAPTER_CHOICE in
        1) CHAPTER_NAME="Einleitung" ;;
        2) CHAPTER_NAME="Theoretische Grundlagen" ;;
        3) CHAPTER_NAME="Stand der Forschung" ;;
        4) CHAPTER_NAME="Methodologie" ;;
        5) CHAPTER_NAME="Implementierung" ;;
        6) CHAPTER_NAME="Evaluation" ;;
        7) CHAPTER_NAME="Diskussion" ;;
        8) CHAPTER_NAME="Fazit und Ausblick" ;;
    esac
    
    echo -e "${BLUE}Schreibe Kapitel: $CHAPTER_NAME mit Qualität: $QUALITY${NC}"
    
    # Single Chapter mit SPARC TDD
    npx claude-flow@alpha sparc tdd "Schreibe Kapitel '$CHAPTER_NAME' für Masterarbeit über AI Agents in Finance. Qualität: $QUALITY. Nutze RAG-System für wissenschaftliche Quellen."
fi

# 8. Abschlussbericht
echo -e "\n${YELLOW}[8/8] Erstelle Abschlussbericht...${NC}"

# Status Report generieren
python3 << EOF
from memory_system import get_memory
from datetime import datetime
import json

memory = get_memory()
stats = memory.get_current_stats()
citation_stats = memory.get_citation_stats()

report = {
    "timestamp": datetime.now().isoformat(),
    "workflow": "write_chapter.sh",
    "chapter": "$CHAPTER_CHOICE",
    "quality": "$QUALITY",
    "stats": stats,
    "citations": citation_stats,
    "services": {
        "mcp_server": "running on port 3000",
        "qdrant": "$QDRANT_STATUS",
        "ollama": "$OLLAMA_STATUS" if "$OLLAMA_STATUS" != "" else "not found"
    }
}

# Speichere Report
with open('workflow_report.json', 'w') as f:
    json.dump(report, f, indent=2)

# Terminal Output
print("\n=== WORKFLOW ABSCHLUSSBERICHT ===")
print(f"Timestamp: {report['timestamp']}")
print(f"Chapter: {report['chapter']} (Qualität: {report['quality']})")
print(f"\nStatistiken:")
print(f"- Kapitel geschrieben: {stats['chapters_written']}")
print(f"- Quellen gesammelt: {stats['sources_collected']}")
print(f"- Verifizierte Zitate: {citation_stats['total_verified']}")
print(f"\nServices:")
for service, status in report['services'].items():
    print(f"- {service}: {status}")
EOF

# Cleanup
echo -e "\n${GREEN}✓ Workflow abgeschlossen!${NC}"
echo -e "${BLUE}Report gespeichert in: workflow_report.json${NC}"

# Optional: MCP Server stoppen
echo -e "\n${YELLOW}MCP Server läuft weiter im Hintergrund (PID: $MCP_PID)${NC}"
echo -e "Zum Stoppen: kill $MCP_PID"

exit 0