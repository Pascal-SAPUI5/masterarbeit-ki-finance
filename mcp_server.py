#!/usr/bin/env python3
"""
MCP Server für Masterarbeit KI Finance
======================================

Stellt die Funktionalität des Projekts als MCP Server zur Verfügung,
damit Claude Code alle Aufgaben automatisiert erledigen kann.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Importiere die Projekt-Module
sys.path.insert(0, str(Path(__file__).parent))

from scripts.utils import get_project_root, load_config, ensure_directories
from scripts.search_literature import LiteratureSearcher
from scripts.research_assistant import ResearchAssistant
from scripts.manage_references import ReferenceManager
from scripts.citation_quality_control import CitationQualityControl
from memory_system import get_memory
from mcp_server_rag_extension import MCPRAGExtension
import yaml


class MasterarbeitMCPServer:
    """MCP Server für das Masterarbeit-Projekt."""
    
    def __init__(self):
        self.project_root = get_project_root()
        self.config = load_config()
        ensure_directories()
        
        # Initialisiere Komponenten
        self.literature_searcher = LiteratureSearcher()
        self.research_assistant = ResearchAssistant()
        self.reference_manager = ReferenceManager()
        self.citation_qc = CitationQualityControl()
        
        # Memory System
        self.memory = get_memory()
        
        # Lade Kontext und Regeln
        self.context = self.memory.context
        self.rules = self.memory.rules
        
        # RAG Extension
        self.rag_extension = MCPRAGExtension()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Verarbeitet eingehende MCP-Anfragen."""
        method = request.get("method", "")
        params = request.get("params", {})
        
        try:
            if method == "tools/list":
                return await self.list_tools()
            
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_args = params.get("arguments", {})
                return await self.call_tool(tool_name, tool_args)
            
            elif method == "resources/list":
                return await self.list_resources()
            
            elif method == "resources/read":
                uri = params.get("uri", "")
                return await self.read_resource(uri)
            
            elif method == "prompts/list":
                return await self.list_prompts()
            
            elif method == "prompts/get":
                name = params.get("name", "")
                return await self.get_prompt(name)
            
            else:
                return {"error": f"Unbekannte Methode: {method}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    async def list_tools(self) -> Dict[str, Any]:
        """Listet alle verfügbaren Tools auf."""
        tools = [
            {
                "name": "search_literature",
                "description": "Sucht nach wissenschaftlicher Literatur in Q1-Journals",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "keywords": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Suchbegriffe"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 50,
                            "description": "Maximale Anzahl Ergebnisse"
                        }
                    }
                }
            },
            {
                "name": "manage_references",
                "description": "Verwaltet Literaturverweise (Import/Export, Formatierung)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["import", "export", "stats", "format"],
                            "description": "Aktion"
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Dateipfad für Import/Export"
                        },
                        "format": {
                            "type": "string",
                            "enum": ["apa", "bibtex", "ris"],
                            "default": "apa"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "create_writing_template",
                "description": "Erstellt eine Schreibvorlage für einen Abschnitt",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chapter": {
                            "type": "string",
                            "description": "Kapitelname"
                        },
                        "section": {
                            "type": "string",
                            "description": "Abschnittsname"
                        }
                    },
                    "required": ["chapter", "section"]
                }
            },
            {
                "name": "check_progress",
                "description": "Überprüft den Fortschritt der Masterarbeit",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "generate_outline",
                "description": "Generiert eine Thesis-Gliederung",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "generate_summary",
                "description": "Generiert eine Forschungszusammenfassung",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "claude_writing_assistant",
                "description": "KI-gestützter Schreibassistent mit Claude API",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text zum Überarbeiten"
                        },
                        "task": {
                            "type": "string",
                            "enum": ["improve", "expand", "summarize", "translate"],
                            "description": "Aufgabentyp"
                        },
                        "context": {
                            "type": "string",
                            "description": "Zusätzlicher Kontext"
                        }
                    },
                    "required": ["text", "task"]
                }
            },
            {
                "name": "backup_project",
                "description": "Erstellt ein Backup des gesamten Projekts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_outputs": {
                            "type": "boolean",
                            "default": True,
                            "description": "Output-Dateien einschließen"
                        }
                    }
                }
            },
            {
                "name": "scrape_q1_journals",
                "description": "Web-Scraping für Q1-Journal-Listen",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": ["finance", "information_systems", "ai", "all"],
                            "default": "all",
                            "description": "Journal-Kategorie"
                        }
                    }
                }
            },
            {
                "name": "verify_citations",
                "description": "Verifiziert und generiert korrekte wissenschaftliche Zitationen mit Qualitätskontrolle",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "Text mit [Research Needed] Markierungen"
                        },
                        "text_file": {
                            "type": "string",
                            "description": "Pfad zur Textdatei"
                        },
                        "verify_all": {
                            "type": "boolean",
                            "default": False,
                            "description": "Alle Quellen verifizieren"
                        }
                    }
                }
            },
            {
                "name": "memory_checkpoint",
                "description": "Erstellt oder stellt einen Projekt-Checkpoint wieder her",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "restore", "list"],
                            "description": "Aktion"
                        },
                        "name": {
                            "type": "string",
                            "description": "Checkpoint-Name"
                        },
                        "description": {
                            "type": "string",
                            "description": "Beschreibung des Checkpoints"
                        }
                    },
                    "required": ["action"]
                }
            },
            {
                "name": "add_note",
                "description": "Fügt eine wichtige Notiz zum Memory System hinzu",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "note": {
                            "type": "string",
                            "description": "Notiz-Text"
                        },
                        "category": {
                            "type": "string",
                            "enum": ["decision", "finding", "todo", "reminder", "other"],
                            "default": "other",
                            "description": "Notiz-Kategorie"
                        }
                    },
                    "required": ["note"]
                }
            },
            {
                "name": "get_context",
                "description": "Zeigt aktuellen Projekt-Kontext und Regeln an",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_rules": {
                            "type": "boolean",
                            "default": True,
                            "description": "Regeln einschließen"
                        },
                        "include_progress": {
                            "type": "boolean",
                            "default": True,
                            "description": "Fortschritt einschließen"
                        }
                    }
                }
            },
            {
                "name": "update_progress",
                "description": "Aktualisiert den Fortschritt der Masterarbeit",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "chapter": {
                            "type": "string",
                            "description": "Kapitelname"
                        },
                        "section": {
                            "type": "string",
                            "description": "Abschnittsname"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["not_started", "in_progress", "review", "completed"],
                            "description": "Status"
                        },
                        "word_count": {
                            "type": "integer",
                            "description": "Aktuelle Wortzahl"
                        },
                        "quality_score": {
                            "type": "object",
                            "properties": {
                                "aufbau_und_form": {"type": "integer", "minimum": 0, "maximum": 20},
                                "forschungsfrage_und_literatur": {"type": "integer", "minimum": 0, "maximum": 30},
                                "qualitaet_methodische_durchfuehrung": {"type": "integer", "minimum": 0, "maximum": 40},
                                "innovationsgrad_relevanz": {"type": "integer", "minimum": 0, "maximum": 10}
                            },
                            "description": "MBA-Bewertungskriterien Scores"
                        }
                    }
                }
            },
            {
                "name": "check_mba_compliance",
                "description": "Überprüft Einhaltung der MBA-Standards",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "check_type": {
                            "type": "string",
                            "enum": ["literature_quality", "evaluation_criteria", "formal_requirements", "all"],
                            "default": "all",
                            "description": "Art der Überprüfung"
                        },
                        "generate_report": {
                            "type": "boolean",
                            "default": True,
                            "description": "Detaillierten Report generieren"
                        }
                    }
                }
            }
        ]
        
        # RAG-Tools hinzufügen
        tools.extend(self.rag_extension.get_additional_tools())
        
        return {"tools": tools}
    
    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Führt ein Tool aus."""
        
        if tool_name == "search_literature":
            keywords = args.get("keywords", self.literature_searcher.config.get('keywords', {}).get('primary', []))
            max_results = args.get("max_results", 50)
            
            results = []
            for keyword in keywords:
                results.extend(self.literature_searcher.search_google_scholar(keyword, max_results))
                results.extend(self.literature_searcher.search_crossref(keyword, max_results))
            
            # Validiere und speichere
            validated = []
            for result in results:
                is_valid, reason = self.literature_searcher.validate_source(result)
                if is_valid:
                    validated.append(result)
            
            self.literature_searcher.results = results
            self.literature_searcher.validated_results = validated
            self.literature_searcher.save_results()
            
            return {
                "total_found": len(results),
                "validated": len(validated),
                "message": f"Gefunden: {len(results)} Publikationen, {len(validated)} validiert"
            }
        
        elif tool_name == "manage_references":
            action = args.get("action")
            
            if action == "stats":
                stats = self._get_reference_stats()
                return {"stats": stats}
            
            elif action == "export":
                format_type = args.get("format", "apa")
                file_path = args.get("file_path", f"output/bibliography.{format_type}")
                
                output_path = self.project_root / file_path
                if format_type == "ris":
                    self.reference_manager.export_ris(output_path)
                else:
                    self.reference_manager.export_bibliography(output_path, format_type)
                
                return {"message": f"Exportiert nach {output_path}"}
        
        elif tool_name == "create_writing_template":
            chapter = args.get("chapter")
            section = args.get("section")
            
            template = self.research_assistant.create_writing_template(chapter, section)
            
            # Speichere Template
            safe_filename = f"{chapter}_{section}".replace(' ', '_').replace('/', '_')
            output_file = self.project_root / "writing" / "templates" / f"{safe_filename}.md"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(template)
            
            return {
                "template": template,
                "saved_to": str(output_file)
            }
        
        elif tool_name == "check_progress":
            progress = self.research_assistant.check_progress()
            return progress
        
        elif tool_name == "generate_outline":
            outline = self.research_assistant.generate_outline()
            
            # Speichere Gliederung
            output_file = self.project_root / "writing" / "thesis_outline.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(outline, f, indent=2, ensure_ascii=False)
            
            return outline
        
        elif tool_name == "generate_summary":
            summary = self.research_assistant.generate_summary()
            
            # Speichere Zusammenfassung
            output_file = self.project_root / "output" / f"research_summary_{datetime.now().strftime('%Y%m%d')}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            return {
                "summary": summary,
                "saved_to": str(output_file)
            }
        
        elif tool_name == "claude_writing_assistant":
            # Hier würde die Claude API Integration erfolgen
            text = args.get("text")
            task = args.get("task")
            context = args.get("context", "")
            
            return {
                "message": "Claude Writing Assistant noch nicht implementiert",
                "text": text,
                "task": task
            }
        
        elif tool_name == "backup_project":
            include_outputs = args.get("include_outputs", True)
            backup_path = await self._create_backup(include_outputs)
            
            return {
                "message": f"Backup erstellt: {backup_path}",
                "path": str(backup_path)
            }
        
        elif tool_name == "scrape_q1_journals":
            category = args.get("category", "all")
            journals = await self._scrape_q1_journals(category)
            
            return {
                "journals": journals,
                "count": len(journals)
            }
        
        elif tool_name == "verify_citations":
            # Text analysieren
            text = args.get("text", "")
            text_file = args.get("text_file", "")
            verify_all = args.get("verify_all", False)
            
            if verify_all:
                # Verifiziere alle Quellen
                validated_file = self.project_root / "research" / "validated-literature.json"
                if validated_file.exists():
                    with open(validated_file, 'r', encoding='utf-8') as f:
                        sources = json.load(f)
                    
                    verified = []
                    issues = []
                    
                    for source in sources:
                        result = self.citation_qc.verify_source(source)
                        if result["verified"]:
                            verified.append(result)
                        else:
                            issues.append(result)
                    
                    return {
                        "verified_count": len(verified),
                        "issues_count": len(issues),
                        "total": len(sources),
                        "message": f"Verifiziert: {len(verified)}/{len(sources)} Quellen"
                    }
            
            elif text_file:
                # Analysiere Textdatei
                file_path = self.project_root / text_file
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
            
            if text:
                # Analysiere Text
                analysis = self.citation_qc.analyze_text_citations(text)
                report_path = self.citation_qc.generate_quality_report(analysis)
                
                # Erstelle formatierten Text mit Zitaten
                formatted_text = text
                for topic, data in analysis['suggestions'].items():
                    if data['sources']:
                        # Erstelle Zitations-Vorschläge
                        citations = []
                        for source in data['sources'][:3]:  # Top 3 Quellen
                            if source.get('verified'):
                                citations.append(source.get('citation_german', ''))
                        
                        if citations:
                            replacement = f"{citations[0]}"
                            formatted_text = formatted_text.replace(
                                f"[Research Needed: {topic}]",
                                replacement
                            )
                
                return {
                    "analysis": analysis,
                    "report_path": str(report_path),
                    "formatted_text": formatted_text,
                    "message": f"Analyse abgeschlossen: {analysis['research_needed_count']} Stellen analysiert"
                }
            
            return {"error": "Bitte geben Sie Text oder text_file an"}
        
        elif tool_name == "memory_checkpoint":
            action = args.get("action")
            
            if action == "create":
                name = args.get("name", f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                description = args.get("description", "")
                checkpoint_path = self.memory.create_checkpoint(name, description)
                return {
                    "message": f"Checkpoint erstellt: {name}",
                    "path": str(checkpoint_path)
                }
            
            elif action == "restore":
                name = args.get("name")
                if not name:
                    return {"error": "Checkpoint-Name erforderlich"}
                
                success = self.memory.restore_checkpoint(name)
                if success:
                    return {"message": f"Checkpoint '{name}' wiederhergestellt"}
                else:
                    return {"error": f"Checkpoint '{name}' nicht gefunden"}
            
            elif action == "list":
                checkpoints = self.memory.list_checkpoints()
                return {
                    "checkpoints": checkpoints,
                    "count": len(checkpoints)
                }
            
            else:
                return {"error": f"Unbekannte Aktion: {action}"}
        
        elif tool_name == "add_note":
            note = args.get("note")
            category = args.get("category", "other")
            
            self.memory.add_note(note, category)
            return {"message": "Notiz hinzugefügt"}
        
        elif tool_name == "get_context":
            include_rules = args.get("include_rules", True)
            include_progress = args.get("include_progress", True)
            
            context = {
                "project_info": self.memory.context.get("project_info", {}),
                "current_phase": self.memory.context.get("current_phase", ""),
                "session_count": len(self.memory.session_history),
                "notes_count": len(self.memory.context.get("notes", []))
            }
            
            if include_rules:
                context["active_rules"] = self.memory.rules
            
            if include_progress:
                progress = self.research_assistant.check_progress()
                context["progress"] = progress
            
            # MBA-Standards Integration
            mba_standards = load_config()["mba_standards"]
            context["evaluation_criteria"] = mba_standards.get("evaluation_criteria", {})
            context["current_quality_scores"] = self.memory.context.get("quality_scores", {})
            
            return context
        
        elif tool_name == "update_progress":
            chapter = args.get("chapter")
            section = args.get("section")
            status = args.get("status")
            word_count = args.get("word_count")
            quality_score = args.get("quality_score", {})
            
            # Update im Memory System
            progress_update = {
                "timestamp": datetime.now().isoformat(),
                "chapter": chapter,
                "section": section,
                "status": status,
                "word_count": word_count,
                "quality_score": quality_score
            }
            
            self.memory.update_progress(progress_update)
            
            # MBA-Compliance Check
            if quality_score:
                total_score = sum(quality_score.values())
                max_score = 100
                percentage = (total_score / max_score) * 100
                
                grade = "nicht_ausreichend"
                if percentage >= 90:
                    grade = "sehr_gut"
                elif percentage >= 80:
                    grade = "gut"
                elif percentage >= 70:
                    grade = "befriedigend"
                elif percentage >= 60:
                    grade = "ausreichend"
                
                return {
                    "message": "Fortschritt aktualisiert",
                    "current_grade": grade,
                    "percentage": f"{percentage:.1f}%",
                    "quality_scores": quality_score
                }
            
            return {"message": "Fortschritt aktualisiert"}
        
        elif tool_name == "check_mba_compliance":
            check_type = args.get("check_type", "all")
            generate_report = args.get("generate_report", True)
            
            mba_standards = load_config()["mba_standards"]
            compliance_results = {}
            
            if check_type in ["literature_quality", "all"]:
                # Prüfe Literaturqualität
                validated_lit = self.project_root / "research" / "validated-literature.json"
                if validated_lit.exists():
                    with open(validated_lit, 'r', encoding='utf-8') as f:
                        sources = json.load(f)
                    
                    lit_analysis = self._analyze_literature_quality(sources, mba_standards)
                    compliance_results["literature_quality"] = lit_analysis
            
            if check_type in ["evaluation_criteria", "all"]:
                # Prüfe Bewertungskriterien
                current_scores = self.memory.context.get("quality_scores", {})
                eval_analysis = self._analyze_evaluation_criteria(current_scores, mba_standards)
                compliance_results["evaluation_criteria"] = eval_analysis
            
            if check_type in ["formal_requirements", "all"]:
                # Prüfe formale Anforderungen
                formal_analysis = self._check_formal_requirements(mba_standards)
                compliance_results["formal_requirements"] = formal_analysis
            
            if generate_report:
                report_path = self._generate_mba_compliance_report(compliance_results)
                return {
                    "compliance_results": compliance_results,
                    "report_path": str(report_path),
                    "overall_status": self._calculate_overall_compliance(compliance_results)
                }
            
            return {"compliance_results": compliance_results}
        
        else:
            # Prüfe ob es ein RAG-Tool ist
            rag_tools = [tool['name'] for tool in self.rag_extension.get_additional_tools()]
            if tool_name in rag_tools:
                return await self.rag_extension.handle_tool(tool_name, args)
            else:
                return {"error": f"Unbekanntes Tool: {tool_name}"}
    
    async def list_resources(self) -> Dict[str, Any]:
        """Listet verfügbare Ressourcen auf."""
        resources = [
            {
                "uri": "file://config/research-criteria.yaml",
                "name": "Forschungskriterien",
                "description": "Qualitätskriterien für Literatursuche",
                "mimeType": "application/x-yaml"
            },
            {
                "uri": "file://config/writing-style.yaml",
                "name": "Schreibstil-Richtlinien",
                "description": "Akademische Schreibrichtlinien",
                "mimeType": "application/x-yaml"
            },
            {
                "uri": "file://config/mba-standards.json",
                "name": "MBA Standards",
                "description": "MBA Programm Anforderungen",
                "mimeType": "application/json"
            },
            {
                "uri": "file://research/validated-literature.json",
                "name": "Validierte Literatur",
                "description": "Geprüfte Q1-Journal Artikel",
                "mimeType": "application/json"
            },
            {
                "uri": "progress://current",
                "name": "Aktueller Fortschritt",
                "description": "Echtzeit-Fortschrittsübersicht",
                "mimeType": "application/json"
            }
        ]
        
        return {"resources": resources}
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Liest eine Ressource."""
        if uri.startswith("file://"):
            file_path = uri.replace("file://", "")
            full_path = self.project_root / file_path
            
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    if full_path.suffix == '.json':
                        content = json.load(f)
                    else:
                        content = f.read()
                
                return {
                    "contents": [{
                        "uri": uri,
                        "mimeType": "application/json" if full_path.suffix == '.json' else "text/plain",
                        "text": json.dumps(content, indent=2) if isinstance(content, dict) else content
                    }]
                }
        
        elif uri == "progress://current":
            progress = self.research_assistant.check_progress()
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(progress, indent=2)
                }]
            }
        
        return {"error": f"Ressource nicht gefunden: {uri}"}
    
    async def list_prompts(self) -> Dict[str, Any]:
        """Listet verfügbare Prompts auf."""
        prompts = [
            {
                "name": "thesis_introduction",
                "description": "Prompt für Einleitung der Masterarbeit",
                "arguments": [
                    {
                        "name": "topic",
                        "description": "Hauptthema der Arbeit",
                        "required": True
                    }
                ]
            },
            {
                "name": "literature_review",
                "description": "Prompt für Literaturübersicht",
                "arguments": [
                    {
                        "name": "sources",
                        "description": "Anzahl der Quellen",
                        "required": False
                    }
                ]
            },
            {
                "name": "methodology",
                "description": "Prompt für Methodikteil",
                "arguments": []
            }
        ]
        
        return {"prompts": prompts}
    
    async def get_prompt(self, name: str) -> Dict[str, Any]:
        """Holt einen spezifischen Prompt."""
        prompts = {
            "thesis_introduction": {
                "name": "thesis_introduction",
                "description": "Prompt für Einleitung der Masterarbeit",
                "messages": [
                    {
                        "role": "system",
                        "content": "Du bist ein Experte für akademisches Schreiben auf Master-Niveau."
                    },
                    {
                        "role": "user",
                        "content": "Schreibe eine Einleitung für eine Masterarbeit zum Thema: {{topic}}\n\nDie Einleitung sollte folgende Elemente enthalten:\n1. Hinführung zum Thema\n2. Problemstellung\n3. Zielsetzung\n4. Forschungsfragen\n5. Aufbau der Arbeit\n\nUmfang: ca. 3-4 Seiten"
                    }
                ]
            },
            "literature_review": {
                "name": "literature_review",
                "description": "Prompt für Literaturübersicht",
                "messages": [
                    {
                        "role": "system",
                        "content": "Du bist ein Experte für systematische Literaturanalyse."
                    },
                    {
                        "role": "user",
                        "content": "Erstelle eine strukturierte Literaturübersicht basierend auf {{sources:50}} Q1-Journal-Artikeln.\n\nStrukturiere nach:\n1. Thematischen Clustern\n2. Chronologischer Entwicklung\n3. Methodischen Ansätzen\n4. Identifizierten Forschungslücken"
                    }
                ]
            },
            "methodology": {
                "name": "methodology",
                "description": "Prompt für Methodikteil",
                "messages": [
                    {
                        "role": "system",
                        "content": "Du bist ein Experte für Forschungsmethodik."
                    },
                    {
                        "role": "user",
                        "content": "Beschreibe die Methodik für eine Masterarbeit über KI-Agenten im Finanzsektor.\n\nBerücksichtige:\n1. Forschungsdesign (qualitativ/quantitativ)\n2. Datenerhebung\n3. Analysemethoden\n4. Gütekriterien\n5. Ethische Überlegungen"
                    }
                ]
            }
        }
        
        if name in prompts:
            return prompts[name]
        
        return {"error": f"Prompt nicht gefunden: {name}"}
    
    def _get_reference_stats(self) -> Dict[str, Any]:
        """Sammelt Statistiken über Referenzen."""
        refs = self.reference_manager.references
        
        if not refs:
            return {"total": 0, "message": "Keine Referenzen vorhanden"}
        
        # Statistiken berechnen
        total = len(refs)
        years = {}
        venues = {}
        impact_factors = []
        
        for ref in refs:
            # Jahr
            year = ref.get('year', 'Unknown')
            years[year] = years.get(year, 0) + 1
            
            # Venue
            venue = ref.get('venue', 'Unknown')
            if venue:
                venues[venue] = venues.get(venue, 0) + 1
            
            # Impact Factor
            if ref.get('impact_factor', 0) > 0:
                impact_factors.append(ref['impact_factor'])
        
        avg_impact = sum(impact_factors) / len(impact_factors) if impact_factors else 0
        
        return {
            "total": total,
            "average_impact_factor": round(avg_impact, 2),
            "year_distribution": dict(sorted(years.items(), reverse=True)),
            "top_venues": dict(sorted(venues.items(), key=lambda x: x[1], reverse=True)[:5])
        }
    
    async def _create_backup(self, include_outputs: bool) -> Path:
        """Erstellt ein Projekt-Backup."""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"masterarbeit_backup_{timestamp}"
        backup_path = self.project_root / "backups" / backup_name
        
        # Erstelle Backup-Verzeichnis
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Kopiere wichtige Verzeichnisse
        dirs_to_backup = ["config", "research", "writing", "scripts"]
        if include_outputs:
            dirs_to_backup.append("output")
        
        for dir_name in dirs_to_backup:
            src = self.project_root / dir_name
            if src.exists():
                dst = backup_path / dir_name
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        
        # Erstelle Backup-Info
        info = {
            "timestamp": datetime.now().isoformat(),
            "included_outputs": include_outputs,
            "directories": dirs_to_backup
        }
        
        with open(backup_path / "backup_info.json", 'w') as f:
            json.dump(info, f, indent=2)
        
        return backup_path
    
    async def _scrape_q1_journals(self, category: str) -> List[Dict[str, str]]:
        """Scraped Q1-Journal-Listen (Platzhalter)."""
        # Dies wäre eine echte Web-Scraping-Implementierung
        q1_journals = {
            "finance": [
                {"name": "Journal of Finance", "impact_factor": 7.2},
                {"name": "Review of Financial Studies", "impact_factor": 6.8},
                {"name": "Journal of Financial Economics", "impact_factor": 6.1}
            ],
            "information_systems": [
                {"name": "MIS Quarterly", "impact_factor": 7.3},
                {"name": "Information Systems Research", "impact_factor": 5.2},
                {"name": "Journal of Management Information Systems", "impact_factor": 4.8}
            ],
            "ai": [
                {"name": "Expert Systems with Applications", "impact_factor": 6.9},
                {"name": "Decision Support Systems", "impact_factor": 4.5},
                {"name": "International Journal of Information Management", "impact_factor": 8.2}
            ]
        }
        
        if category == "all":
            journals = []
            for cat_journals in q1_journals.values():
                journals.extend(cat_journals)
            return journals
        
        return q1_journals.get(category, [])
    
    def _analyze_literature_quality(self, sources: List[Dict], mba_standards: Dict) -> Dict[str, Any]:
        """Analysiert Literaturqualität nach MBA-Standards."""
        total_sources = len(sources)
        if total_sources == 0:
            return {"error": "Keine Quellen gefunden"}
        
        # Aktualität
        current_year = datetime.now().year
        recent_sources = sum(1 for s in sources if s.get('year', 0) >= 2020)
        very_recent = sum(1 for s in sources if s.get('year', 0) >= 2022)
        
        # Q1-Anteil
        q1_sources = sum(1 for s in sources if s.get('is_q1', False))
        
        # Internationalität
        regions = {"US": 0, "EU": 0, "Other": 0}
        for source in sources:
            # Simplified region detection based on venue
            venue = source.get('venue', '').lower()
            if any(us in venue for us in ['american', 'us', 'ieee', 'acm']):
                regions["US"] += 1
            elif any(eu in venue for eu in ['european', 'springer', 'elsevier']):
                regions["EU"] += 1
            else:
                regions["Other"] += 1
        
        # DOI-Verfügbarkeit
        doi_available = sum(1 for s in sources if s.get('doi'))
        
        # Impact Factor Durchschnitt
        impact_factors = [s.get('impact_factor', 0) for s in sources if s.get('impact_factor', 0) > 0]
        avg_impact = sum(impact_factors) / len(impact_factors) if impact_factors else 0
        
        # Bewertung nach MBA-Standards
        quality_standards = mba_standards.get("literature_quality_standards", {})
        
        score = 0
        max_score = 10
        
        # Bewertungslogik
        recent_percentage = (recent_sources / total_sources) * 100
        if recent_percentage >= 90:
            score += 2
        elif recent_percentage >= 70:
            score += 1.5
        elif recent_percentage >= 50:
            score += 1
        
        q1_percentage = (q1_sources / total_sources) * 100
        if q1_percentage >= 80:
            score += 3
        elif q1_percentage >= 60:
            score += 2.5
        elif q1_percentage >= 40:
            score += 2
        
        doi_percentage = (doi_available / total_sources) * 100
        if doi_percentage == 100:
            score += 2
        elif doi_percentage >= 90:
            score += 1.5
        elif doi_percentage >= 80:
            score += 1
        
        if avg_impact >= 6:
            score += 3
        elif avg_impact >= 4:
            score += 2
        elif avg_impact >= 3:
            score += 1
        
        return {
            "total_sources": total_sources,
            "aktualitaet": f"{recent_percentage:.1f}% von 2020+, {(very_recent/total_sources*100):.1f}% von 2022+",
            "q1_anteil": f"{q1_percentage:.1f}%",
            "internationalitaet": f"{regions['US']/total_sources*100:.1f}% US | {regions['EU']/total_sources*100:.1f}% EU | {regions['Other']/total_sources*100:.1f}% Other",
            "doi_verfuegbarkeit": f"{doi_percentage:.1f}%",
            "impact_factor_durchschnitt": f"{avg_impact:.2f}",
            "mba_score": f"{score}/{max_score}",
            "grade": self._get_literature_grade(score)
        }
    
    def _get_literature_grade(self, score: float) -> str:
        """Bestimmt Note basierend auf Score."""
        if score >= 9:
            return "sehr_gut"
        elif score >= 7:
            return "gut"
        elif score >= 5:
            return "befriedigend"
        elif score >= 3:
            return "ausreichend"
        else:
            return "nicht_ausreichend"
    
    def _analyze_evaluation_criteria(self, current_scores: Dict, mba_standards: Dict) -> Dict[str, Any]:
        """Analysiert aktuelle Bewertung gegen MBA-Kriterien."""
        eval_criteria = mba_standards.get("evaluation_criteria", {})
        analysis = {}
        
        for criterion, details in eval_criteria.items():
            max_points = details.get("total_points", 0)
            current_points = current_scores.get(criterion, 0)
            percentage = (current_points / max_points * 100) if max_points > 0 else 0
            
            analysis[criterion] = {
                "current_points": current_points,
                "max_points": max_points,
                "percentage": f"{percentage:.1f}%",
                "missing_points": max_points - current_points
            }
        
        total_current = sum(current_scores.values())
        total_max = 100
        overall_percentage = (total_current / total_max) * 100
        
        return {
            "criteria_analysis": analysis,
            "total_score": f"{total_current}/{total_max}",
            "overall_percentage": f"{overall_percentage:.1f}%",
            "current_grade": self._calculate_grade(overall_percentage)
        }
    
    def _calculate_grade(self, percentage: float) -> str:
        """Berechnet Note basierend auf Prozentsatz."""
        if percentage >= 90:
            return "sehr_gut (1.0-1.3)"
        elif percentage >= 80:
            return "gut (1.7-2.3)"
        elif percentage >= 70:
            return "befriedigend (2.7-3.3)"
        elif percentage >= 60:
            return "ausreichend (3.7-4.0)"
        else:
            return "nicht_ausreichend (5.0)"
    
    def _check_formal_requirements(self, mba_standards: Dict) -> Dict[str, Any]:
        """Prüft formale Anforderungen."""
        requirements = mba_standards.get("thesis_requirements", {})
        
        # Check current thesis stats
        thesis_file = self.project_root / "output" / "thesis.docx"
        word_count = 0
        page_count = 0
        
        if thesis_file.exists():
            # Here would be actual word/page counting logic
            # For now, use placeholder values
            word_count = self.memory.context.get("current_word_count", 0)
            page_count = word_count // 250  # Rough estimate
        
        return {
            "word_count": {
                "current": word_count,
                "minimum": requirements.get("word_count", {}).get("minimum", 15000),
                "maximum": requirements.get("word_count", {}).get("maximum", 20000),
                "status": "OK" if requirements.get("word_count", {}).get("minimum", 0) <= word_count <= requirements.get("word_count", {}).get("maximum", 99999) else "FEHLT"
            },
            "page_count": {
                "current": page_count,
                "minimum": requirements.get("pages", {}).get("minimum", 60),
                "maximum": requirements.get("pages", {}).get("maximum", 80),
                "status": "OK" if requirements.get("pages", {}).get("minimum", 0) <= page_count <= requirements.get("pages", {}).get("maximum", 999) else "FEHLT"
            },
            "language": requirements.get("language", "German"),
            "submission_format": requirements.get("submission_format", {})
        }
    
    def _generate_mba_compliance_report(self, compliance_results: Dict) -> Path:
        """Generiert MBA-Compliance-Report."""
        report_path = self.project_root / "output" / f"mba_compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_content = "# MBA Compliance Report\n\n"
        report_content += f"Generiert am: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        for section, results in compliance_results.items():
            report_content += f"## {section.replace('_', ' ').title()}\n\n"
            report_content += self._format_results_for_report(results)
            report_content += "\n\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_path
    
    def _format_results_for_report(self, results: Dict) -> str:
        """Formatiert Ergebnisse für Report."""
        formatted = ""
        for key, value in results.items():
            if isinstance(value, dict):
                formatted += f"### {key.replace('_', ' ').title()}\n"
                for sub_key, sub_value in value.items():
                    formatted += f"- **{sub_key}**: {sub_value}\n"
            else:
                formatted += f"- **{key}**: {value}\n"
        return formatted
    
    def _calculate_overall_compliance(self, compliance_results: Dict) -> str:
        """Berechnet Gesamt-Compliance-Status."""
        # Simplified overall calculation
        has_issues = False
        
        for section, results in compliance_results.items():
            if isinstance(results, dict):
                if results.get("error") or results.get("status") == "FEHLT":
                    has_issues = True
                if "grade" in results and "nicht_ausreichend" in str(results.get("grade", "")):
                    has_issues = True
        
        return "WARNUNG: Verbesserungen erforderlich" if has_issues else "OK: Alle Standards erfüllt"


async def main():
    """Hauptfunktion für den MCP Server."""
    server = MasterarbeitMCPServer()
    
    # Lese Anfragen von stdin
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            response = await server.handle_request(request)
            
            # Sende Antwort an stdout
            print(json.dumps(response))
            sys.stdout.flush()
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "type": "server_error"
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())