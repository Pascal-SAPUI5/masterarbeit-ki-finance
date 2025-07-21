#!/usr/bin/env python3
"""
Memory System für Claude Code
=============================

Persistiert Kontext, Regeln und Projektstatus für kontinuierliche Arbeit.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib


class MemorySystem:
    """Verwaltet persistenten Speicher für Claude Code Sessions."""
    
    def __init__(self, project_root: Path = None):
        """Initialisiert das Memory System."""
        self.project_root = project_root or Path(__file__).parent
        self.memory_dir = self.project_root / ".claude_memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory-Dateien
        self.context_file = self.memory_dir / "context.json"
        self.rules_file = self.memory_dir / "rules.yaml"
        self.session_file = self.memory_dir / "session_history.json"
        self.checkpoints_dir = self.memory_dir / "checkpoints"
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # Lade existierende Memory
        self.context = self._load_context()
        self.rules = self._load_rules()
        self.session_history = self._load_session_history()
        
        # Citation tracking
        self.citations_file = self.memory_dir / "citations_tracking.json"
        self.citations = self._load_citations()
    
    def _load_context(self) -> Dict[str, Any]:
        """Lädt gespeicherten Kontext."""
        if self.context_file.exists():
            with open(self.context_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Standard-Kontext
        return {
            "project_info": {
                "name": "Masterarbeit KI Finance",
                "topic": "AI Agents in Finance - Multi-Agent Systems and RAG",
                "language": "Deutsch",
                "academic_level": "Master MBA",
                "university": "Technische Hochschule",
                "start_date": "2025-01-01",
                "deadlines": {
                    "proposal": "2025-02-15",
                    "first_draft": "2025-04-30",
                    "final_submission": "2025-06-30",
                    "defense": "2025-07-15"
                }
            },
            "current_state": {
                "phase": "research",  # research, writing, revision, finalization
                "current_chapter": None,
                "completed_chapters": [],
                "word_count": 0,
                "sources_collected": 0,
                "last_backup": None
            },
            "preferences": {
                "citation_style": "APA 7th",
                "language_style": "formal_academic_german",
                "tools_preference": ["scholarly", "crossref"],
                "backup_frequency": "daily"
            },
            "important_notes": []
        }
    
    def _load_rules(self) -> Dict[str, Any]:
        """Lädt Projekt-spezifische Regeln."""
        if self.rules_file.exists():
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        
        # Standard-Regeln
        return {
            "writing_rules": [
                "Verwende durchgängig wissenschaftlichen Schreibstil",
                "Zitiere ALLE Aussagen mit Quellen",
                "Nutze nur Q1-Journals (Impact Factor > 3.0)",
                "Schreibe in Deutsch, technische Begriffe auf Englisch",
                "Strukturiere jeden Abschnitt: Einleitung → Hauptteil → Zusammenfassung",
                "Vermeide Ich-Form, nutze Passiv-Konstruktionen",
                "Definiere Fachbegriffe bei erster Verwendung"
            ],
            "technical_rules": [
                "Aktiviere IMMER das Virtual Environment",
                "Führe nach Änderungen Tests aus",
                "Erstelle tägliche Backups",
                "Dokumentiere alle Code-Änderungen",
                "Nutze Git für Versionierung"
            ],
            "content_rules": [
                "Fokus auf SAP BTP und Finanzsektor",
                "RAG-Systeme als Kernthema",
                "Multi-Agent-Architekturen hervorheben",
                "Praxisbeispiele aus deutschen Banken",
                "Regulatorische Aspekte (BaFin, GDPR) beachten"
            ],
            "quality_standards": {
                "min_sources": 50,
                "min_q1_percentage": 80,
                "min_words": 20000,
                "max_words": 30000,
                "min_chapters": 8
            }
        }
    
    def _load_session_history(self) -> List[Dict[str, Any]]:
        """Lädt Session-Historie."""
        if self.session_file.exists():
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def save_context(self, updates: Dict[str, Any] = None):
        """Speichert aktualisierten Kontext."""
        if updates:
            # Deep merge updates
            self._deep_merge(self.context, updates)
        
        with open(self.context_file, 'w', encoding='utf-8') as f:
            json.dump(self.context, f, indent=2, ensure_ascii=False)
    
    def save_rules(self, new_rules: Dict[str, Any] = None):
        """Speichert aktualisierte Regeln."""
        if new_rules:
            self._deep_merge(self.rules, new_rules)
        
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.rules, f, default_flow_style=False, allow_unicode=True)
    
    def add_session_entry(self, action: str, details: Dict[str, Any]):
        """Fügt einen Eintrag zur Session-Historie hinzu."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details
        }
        
        self.session_history.append(entry)
        
        # Behalte nur die letzten 1000 Einträge
        if len(self.session_history) > 1000:
            self.session_history = self.session_history[-1000:]
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_history, f, indent=2, ensure_ascii=False)
    
    def create_checkpoint(self, name: str = None):
        """Erstellt einen Checkpoint des aktuellen Zustands."""
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        checkpoint = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "context": self.context.copy(),
            "rules": self.rules.copy(),
            "stats": self.get_current_stats()
        }
        
        checkpoint_file = self.checkpoints_dir / f"checkpoint_{name}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        return checkpoint_file
    
    def restore_checkpoint(self, name: str):
        """Stellt einen Checkpoint wieder her."""
        checkpoint_file = self.checkpoints_dir / f"checkpoint_{name}.json"
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint nicht gefunden: {name}")
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        self.context = checkpoint["context"]
        self.rules = checkpoint["rules"]
        
        self.save_context()
        self.save_rules()
        
        return checkpoint
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Sammelt aktuelle Projekt-Statistiken."""
        from scripts.utils import get_project_root
        
        project_root = get_project_root()
        
        # Zähle Dateien
        chapter_files = list((project_root / "writing" / "chapters").glob("*.docx"))
        template_files = list((project_root / "writing" / "templates").glob("*.md"))
        
        # Lade Literatur-Stats
        lit_file = project_root / "research" / "validated-literature.json"
        sources_count = 0
        if lit_file.exists():
            with open(lit_file, 'r') as f:
                sources = json.load(f)
                sources_count = len(sources)
        
        return {
            "chapters_written": len(chapter_files),
            "templates_created": len(template_files),
            "sources_collected": sources_count,
            "last_activity": datetime.now().isoformat()
        }
    
    def get_context_summary(self) -> str:
        """Erstellt eine Zusammenfassung des aktuellen Kontexts."""
        summary = f"""# Aktueller Projekt-Kontext

## Projekt-Information
- **Thema**: {self.context['project_info']['topic']}
- **Phase**: {self.context['current_state']['phase']}
- **Fortschritt**: {len(self.context['current_state']['completed_chapters'])} Kapitel fertig

## Wichtige Deadlines
- Proposal: {self.context['project_info']['deadlines']['proposal']}
- Erster Entwurf: {self.context['project_info']['deadlines']['first_draft']}
- Finale Abgabe: {self.context['project_info']['deadlines']['final_submission']}

## Aktuelle Aufgaben
- Gesammelte Quellen: {self.context['current_state']['sources_collected']}
- Wortanzahl: {self.context['current_state']['word_count']}

## Wichtige Notizen
"""
        for note in self.context['important_notes'][-5:]:
            summary += f"- {note}\n"
        
        return summary
    
    def get_active_rules(self) -> List[str]:
        """Gibt alle aktiven Regeln als Liste zurück."""
        all_rules = []
        
        for category, rules in self.rules.items():
            if isinstance(rules, list):
                all_rules.extend(rules)
            elif isinstance(rules, dict):
                for key, value in rules.items():
                    all_rules.append(f"{key}: {value}")
        
        return all_rules
    
    def add_important_note(self, note: str):
        """Fügt eine wichtige Notiz hinzu."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.context["important_notes"].append(f"[{timestamp}] {note}")
        
        # Behalte nur die letzten 50 Notizen
        if len(self.context["important_notes"]) > 50:
            self.context["important_notes"] = self.context["important_notes"][-50:]
        
        self.save_context()
    
    def _deep_merge(self, base: dict, updates: dict):
        """Deep merge von zwei Dictionaries."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _load_citations(self) -> Dict[str, Any]:
        """Lädt Citation-Tracking Daten."""
        if self.citations_file.exists():
            with open(self.citations_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "verified_citations": {},
            "citation_usage": {},
            "quality_reports": [],
            "last_verification": None
        }
    
    def save_citations(self):
        """Speichert Citation-Tracking Daten."""
        with open(self.citations_file, 'w', encoding='utf-8') as f:
            json.dump(self.citations, f, indent=2, ensure_ascii=False)
    
    def track_citation(self, citation_key: str, citation_data: Dict[str, Any]):
        """Trackt eine verifizierte Zitation."""
        self.citations["verified_citations"][citation_key] = {
            **citation_data,
            "verified_at": datetime.now().isoformat(),
            "usage_count": self.citations["verified_citations"].get(citation_key, {}).get("usage_count", 0)
        }
        self.save_citations()
        
        # Session-Eintrag
        self.add_session_entry("citation_verified", {
            "key": citation_key,
            "title": citation_data.get("title", ""),
            "verified": citation_data.get("verified", False)
        })
    
    def track_citation_usage(self, citation_key: str, context: str):
        """Trackt die Verwendung einer Zitation."""
        if citation_key not in self.citations["citation_usage"]:
            self.citations["citation_usage"][citation_key] = []
        
        usage = {
            "timestamp": datetime.now().isoformat(),
            "context": context[:200] + "..." if len(context) > 200 else context
        }
        
        self.citations["citation_usage"][citation_key].append(usage)
        
        # Update usage count
        if citation_key in self.citations["verified_citations"]:
            self.citations["verified_citations"][citation_key]["usage_count"] += 1
        
        self.save_citations()
    
    def add_quality_report(self, report_path: str, summary: Dict[str, Any]):
        """Fügt einen Qualitätsbericht hinzu."""
        report = {
            "path": report_path,
            "timestamp": datetime.now().isoformat(),
            "summary": summary
        }
        
        self.citations["quality_reports"].append(report)
        self.citations["last_verification"] = datetime.now().isoformat()
        
        # Behalte nur die letzten 20 Reports
        if len(self.citations["quality_reports"]) > 20:
            self.citations["quality_reports"] = self.citations["quality_reports"][-20:]
        
        self.save_citations()
    
    def get_citation_stats(self) -> Dict[str, Any]:
        """Gibt Citation-Statistiken zurück."""
        verified = self.citations.get("verified_citations", {})
        usage = self.citations.get("citation_usage", {})
        
        return {
            "total_verified": len(verified),
            "total_used": len(usage),
            "most_used": sorted(
                [(k, v.get("usage_count", 0)) for k, v in verified.items()],
                key=lambda x: x[1],
                reverse=True
            )[:5],
            "last_verification": self.citations.get("last_verification"),
            "quality_reports_count": len(self.citations.get("quality_reports", []))
        }
    
    def export_memory_state(self) -> Dict[str, Any]:
        """Exportiert den kompletten Memory-Zustand."""
        return {
            "context": self.context,
            "rules": self.rules,
            "session_count": len(self.session_history),
            "checkpoints": [f.name for f in self.checkpoints_dir.glob("*.json")],
            "citation_stats": self.get_citation_stats(),
            "last_export": datetime.now().isoformat()
        }
    
    def add_note(self, note: str, category: str = "other"):
        """Fügt eine Notiz zum Memory System hinzu."""
        if "notes" not in self.context:
            self.context["notes"] = []
        
        note_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "content": note
        }
        
        self.context["notes"].append(note_entry)
        self.save_context()
        
        # Session-Eintrag
        self.add_session_entry("add_note", {
            "category": category,
            "note_preview": note[:100] + "..." if len(note) > 100 else note
        })
    
    def update_progress(self, progress_data: Dict[str, Any]):
        """Aktualisiert den Fortschritt."""
        if "progress" not in self.context:
            self.context["progress"] = {}
        
        self.context["progress"].update(progress_data)
        
        # Update quality scores if provided
        if "quality_score" in progress_data:
            if "quality_scores" not in self.context:
                self.context["quality_scores"] = {}
            self.context["quality_scores"].update(progress_data["quality_score"])
        
        # Update word count if provided
        if "word_count" in progress_data:
            self.context["current_word_count"] = progress_data["word_count"]
        
        self.save_context()
        
        # Session-Eintrag
        self.add_session_entry("update_progress", progress_data)
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """Listet alle verfügbaren Checkpoints auf."""
        checkpoints = []
        
        for checkpoint_file in sorted(self.checkpoints_dir.glob("checkpoint_*.json")):
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                checkpoints.append({
                    "name": data.get("name"),
                    "timestamp": data.get("timestamp"),
                    "file": checkpoint_file.name
                })
        
        return checkpoints
    
    def create_checkpoint(self, name: str = None, description: str = "") -> Path:
        """Erstellt einen Checkpoint mit optionaler Beschreibung."""
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        checkpoint = {
            "name": name,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "context": self.context.copy(),
            "rules": self.rules.copy(),
            "stats": self.get_current_stats()
        }
        
        checkpoint_file = self.checkpoints_dir / f"checkpoint_{name}.json"
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        # Session-Eintrag
        self.add_session_entry("create_checkpoint", {
            "name": name,
            "description": description
        })
        
        return checkpoint_file
    
    def restore_checkpoint(self, name: str) -> bool:
        """Stellt einen Checkpoint wieder her."""
        checkpoint_file = self.checkpoints_dir / f"checkpoint_{name}.json"
        
        if not checkpoint_file.exists():
            # Try without prefix
            checkpoint_file = self.checkpoints_dir / name
            if not checkpoint_file.exists():
                return False
        
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint = json.load(f)
        
        self.context = checkpoint["context"]
        self.rules = checkpoint["rules"]
        
        self.save_context()
        self.save_rules()
        
        # Session-Eintrag
        self.add_session_entry("restore_checkpoint", {
            "name": name,
            "original_timestamp": checkpoint.get("timestamp")
        })
        
        return True


# Singleton Instance
_memory_instance = None


def get_memory() -> MemorySystem:
    """Gibt die Singleton Memory-Instanz zurück."""
    global _memory_instance
    if _memory_instance is None:
        from scripts.utils import get_project_root
        _memory_instance = MemorySystem(get_project_root())
    return _memory_instance


if __name__ == "__main__":
    # Test Memory System
    from scripts.utils import print_header, print_success, print_info, console
    
    print_header("Memory System Test", "Teste Persistenz-Funktionen")
    
    memory = get_memory()
    
    # Zeige aktuellen Kontext
    print_info("\nAktueller Kontext:")
    console.print(memory.get_context_summary())
    
    # Zeige aktive Regeln
    print_info("\nAktive Regeln:")
    for i, rule in enumerate(memory.get_active_rules()[:5], 1):
        console.print(f"{i}. {rule}")
    
    # Füge Test-Notiz hinzu
    memory.add_important_note("Memory System erfolgreich getestet")
    
    # Erstelle Checkpoint
    checkpoint = memory.create_checkpoint("test_checkpoint")
    print_success(f"\nCheckpoint erstellt: {checkpoint}")
    
    # Session-Eintrag
    memory.add_session_entry("test", {"action": "Memory System Test", "status": "success"})
    
    print_success("\nMemory System funktioniert!")