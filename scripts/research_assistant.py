#!/usr/bin/env python3
"""
Research Assistant for thesis writing
Handles templates, outlines, and progress tracking
"""
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from scripts.utils import get_project_root, load_config, save_json, get_timestamp

class ResearchAssistant:
    def __init__(self):
        self.project_root = get_project_root()
        self.config = load_config("mba-standards.json")
        self.writing_style = load_config("writing-style.yaml")
        self.thesis_outline = self._load_outline()
        
    def _load_outline(self) -> Dict[str, Any]:
        """Load thesis outline if exists."""
        outline_file = self.project_root / "writing" / "thesis_outline.json"
        if outline_file.exists():
            with open(outline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self._create_default_outline()
    
    def _create_default_outline(self) -> Dict[str, Any]:
        """Create default thesis outline based on MBA standards."""
        return {
            "title": "Agile Prozessautomatisierung und Wissensmanagement durch KI-Agenten",
            "chapters": [
                {
                    "number": 1,
                    "title": "Einleitung",
                    "sections": ["Problemstellung", "Zielsetzung", "Forschungsfragen", "Aufbau der Arbeit"]
                },
                {
                    "number": 2,
                    "title": "Theoretische Grundlagen",
                    "sections": ["KI-Agenten", "SAP BTP", "Wissensmanagement", "Finanzsektor"]
                },
                {
                    "number": 3,
                    "title": "Methodik",
                    "sections": ["Forschungsdesign", "Datenerhebung", "Datenanalyse"]
                },
                {
                    "number": 4,
                    "title": "Empirische Untersuchung",
                    "sections": ["Fallstudien", "Experteninterviews", "Prototyp"]
                },
                {
                    "number": 5,
                    "title": "Diskussion",
                    "sections": ["Ergebnisse", "Implikationen", "Limitationen"]
                },
                {
                    "number": 6,
                    "title": "Fazit",
                    "sections": ["Zusammenfassung", "Handlungsempfehlungen", "Ausblick"]
                }
            ]
        }
    
    def create_template(self, chapter: str, section: str) -> str:
        """Create a writing template for a specific section."""
        template = f"""# {chapter} - {section}

## Einleitung des Abschnitts
[Kurze Einführung in das Thema dieses Abschnitts - 2-3 Sätze]

## Hauptteil
### Unterpunkt 1
[Detaillierte Ausführung mit Quellenangaben]

### Unterpunkt 2
[Weitere Aspekte mit wissenschaftlicher Fundierung]

### Unterpunkt 3
[Zusätzliche Erkenntnisse und Analysen]

## Zusammenfassung
[Kernaussagen dieses Abschnitts - 2-3 Sätze]

## Überleitung
[Verbindung zum nächsten Abschnitt - 1-2 Sätze]

---
**Hinweise:**
- Verwenden Sie durchgehend wissenschaftlichen Schreibstil
- Alle Aussagen müssen mit Quellen belegt werden
- Nutzen Sie Fachterminologie konsistent
- Beachten Sie die Vorgaben aus config/writing-style.yaml
"""
        
        # Save template
        template_path = self.project_root / "writing" / "templates" / f"{chapter}_{section}.md"
        template_path.parent.mkdir(parents=True, exist_ok=True)
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        return str(template_path)
    
    def check_progress(self) -> Dict[str, Any]:
        """Check thesis writing progress."""
        progress = {
            "total_chapters": len(self.thesis_outline["chapters"]),
            "completed_chapters": 0,
            "completed_sections": 0,
            "total_sections": 0,
            "deadlines": self.config.get("deadlines", {}),
            "current_status": []
        }
        
        # Check existing files
        for chapter in self.thesis_outline["chapters"]:
            chapter_complete = True
            for section in chapter["sections"]:
                progress["total_sections"] += 1
                # Check if draft exists
                draft_file = self.project_root / "writing" / "chapters" / f"{chapter['title']}_{section}.md"
                if draft_file.exists():
                    progress["completed_sections"] += 1
                else:
                    chapter_complete = False
                    
                progress["current_status"].append({
                    "chapter": chapter["title"],
                    "section": section,
                    "completed": draft_file.exists()
                })
            
            if chapter_complete:
                progress["completed_chapters"] += 1
        
        # Calculate percentage
        progress["completion_percentage"] = (progress["completed_sections"] / progress["total_sections"] * 100) if progress["total_sections"] > 0 else 0
        
        return progress
    
    def generate_summary(self) -> str:
        """Generate a summary of research progress."""
        progress = self.check_progress()
        
        summary = f"""# Forschungsfortschritt - {datetime.now().strftime('%Y-%m-%d')}

## Überblick
- Fertigstellung: {progress['completion_percentage']:.1f}%
- Kapitel: {progress['completed_chapters']}/{progress['total_chapters']}
- Abschnitte: {progress['completed_sections']}/{progress['total_sections']}

## Deadlines
- Proposal: {progress['deadlines'].get('proposal', 'TBD')}
- Erster Entwurf: {progress['deadlines'].get('first_draft', 'TBD')}
- Finale Abgabe: {progress['deadlines'].get('final_submission', 'TBD')}
- Verteidigung: {progress['deadlines'].get('defense', 'TBD')}

## Status nach Kapiteln
"""
        
        current_chapter = None
        for item in progress["current_status"]:
            if item["chapter"] != current_chapter:
                current_chapter = item["chapter"]
                summary += f"\n### {current_chapter}\n"
            status = "✓" if item["completed"] else "○"
            summary += f"- {status} {item['section']}\n"
        
        # Save summary
        summary_path = self.project_root / "output" / f"research_summary_{get_timestamp()}.md"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="Research assistant for thesis writing")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Template command
    template_parser = subparsers.add_parser("template", help="Create writing template")
    template_parser.add_argument("--chapter", required=True, help="Chapter name")
    template_parser.add_argument("--section", required=True, help="Section name")
    
    # Progress command
    progress_parser = subparsers.add_parser("progress", help="Check writing progress")
    progress_parser.add_argument("--update", help="Update progress note")
    
    # Outline command
    outline_parser = subparsers.add_parser("outline", help="Generate thesis outline")
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Generate progress summary")
    
    args = parser.parse_args()
    
    assistant = ResearchAssistant()
    
    if args.command == "template":
        path = assistant.create_template(args.chapter, args.section)
        print(f"Template created: {path}")
    
    elif args.command == "progress":
        progress = assistant.check_progress()
        print(f"Thesis completion: {progress['completion_percentage']:.1f}%")
        print(f"Chapters: {progress['completed_chapters']}/{progress['total_chapters']}")
        print(f"Sections: {progress['completed_sections']}/{progress['total_sections']}")
        
        if args.update:
            # Add note to memory system
            from memory_system import get_memory
            memory = get_memory()
            memory.add_note(f"Progress update: {args.update}")
            print(f"Progress note added: {args.update}")
    
    elif args.command == "outline":
        outline = assistant.thesis_outline
        print(json.dumps(outline, indent=2, ensure_ascii=False))
        
    elif args.command == "summary":
        summary = assistant.generate_summary()
        print(summary)

if __name__ == "__main__":
    main()