#!/usr/bin/env python3
"""
Reference management module
Handles bibliography, citations, and Citavi integration
"""
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from scripts.utils import get_project_root, load_json, save_json

class ReferenceManager:
    def __init__(self):
        self.project_root = get_project_root()
        self.references = self._load_references()
        self.citavi_path = self._get_citavi_path()
        
    def _load_references(self) -> List[Dict[str, Any]]:
        """Load existing references from validated literature."""
        ref_file = self.project_root / "research" / "validated-literature.json"
        if ref_file.exists():
            return load_json(ref_file)
        return []
    
    def _get_citavi_path(self) -> str:
        """Get Citavi project path from config."""
        config_file = self.project_root / "config" / "api_keys.yaml"
        if config_file.exists():
            import yaml
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                return config.get("citavi_path", "")
        return ""
    
    def import_references(self, source_file: str) -> int:
        """Import references from search results."""
        source_path = Path(source_file)
        if not source_path.exists():
            source_path = self.project_root / "research" / "search-results" / source_file
        
        if source_path.exists():
            data = load_json(source_path)
            new_refs = data.get("results", [])
            
            # Add to existing references (avoid duplicates)
            existing_dois = {ref.get("doi") for ref in self.references if ref.get("doi")}
            
            added = 0
            for ref in new_refs:
                if ref.get("doi") not in existing_dois:
                    self.references.append(ref)
                    added += 1
            
            # Save updated references
            save_json(self.references, self.project_root / "research" / "validated-literature.json")
            return added
        return 0
    
    def export_citavi(self, papers: List[str] = None) -> str:
        """Export references in Citavi-compatible format."""
        # Filter papers if specified
        refs_to_export = self.references
        if papers:
            # Filter by author names or titles
            refs_to_export = [
                ref for ref in self.references
                if any(paper.lower() in str(ref).lower() for paper in papers)
            ]
        
        # Create RIS format export
        ris_content = []
        for ref in refs_to_export:
            ris_content.append("TY  - JOUR")  # Journal article
            
            # Authors
            for author in ref.get("authors", []):
                ris_content.append(f"AU  - {author}")
            
            # Title and other fields
            ris_content.append(f"TI  - {ref.get('title', '')}")
            ris_content.append(f"JO  - {ref.get('journal', '')}")
            ris_content.append(f"PY  - {ref.get('year', '')}")
            
            if ref.get("doi"):
                ris_content.append(f"DO  - {ref.get('doi')}")
            
            if ref.get("abstract"):
                ris_content.append(f"AB  - {ref.get('abstract', '')}")
            
            ris_content.append("ER  - ")
            ris_content.append("")
        
        # Save RIS file
        output_file = self.project_root / "output" / "references_export.ris"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(ris_content))
        
        return str(output_file)
    
    def generate_bibliography(self) -> str:
        """Generate formatted bibliography in APA style."""
        bibliography = []
        
        for ref in sorted(self.references, key=lambda x: (x.get("authors", [""])[0], x.get("year", ""))):
            # Format: Authors (Year). Title. Journal.
            authors = ref.get("authors", [])
            if len(authors) > 3:
                author_str = f"{authors[0]} et al."
            else:
                author_str = ", ".join(authors)
            
            citation = f"{author_str} ({ref.get('year', 'n.d.')}). {ref.get('title', 'Untitled')}."
            
            if ref.get("journal"):
                citation += f" {ref.get('journal')}."
            
            if ref.get("doi"):
                citation += f" https://doi.org/{ref.get('doi')}"
            
            bibliography.append(citation)
        
        # Save bibliography
        output_file = self.project_root / "output" / "bibliography.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(bibliography))
        
        return "\n\n".join(bibliography)
    
    def find_citation(self, query: str) -> List[Dict[str, Any]]:
        """Find references matching a query."""
        matches = []
        query_lower = query.lower()
        
        for ref in self.references:
            ref_str = json.dumps(ref).lower()
            if query_lower in ref_str:
                matches.append(ref)
        
        return matches

def main():
    parser = argparse.ArgumentParser(description="Manage academic references")
    parser.add_argument("--import", dest="import_file", help="Import references from file")
    parser.add_argument("--export", dest="export_format", choices=["citavi", "bibtex"], help="Export format")
    parser.add_argument("--papers", nargs="+", help="Specific papers to export")
    parser.add_argument("--bibliography", action="store_true", help="Generate bibliography")
    parser.add_argument("--find", help="Find references matching query")
    
    args = parser.parse_args()
    
    manager = ReferenceManager()
    
    if args.import_file:
        added = manager.import_references(args.import_file)
        print(f"Imported {added} new references")
    
    if args.export_format == "citavi":
        output = manager.export_citavi(args.papers)
        print(f"Exported to: {output}")
    
    if args.bibliography:
        bibliography = manager.generate_bibliography()
        print("Bibliography generated:")
        print(bibliography[:500] + "..." if len(bibliography) > 500 else bibliography)
    
    if args.find:
        matches = manager.find_citation(args.find)
        print(f"Found {len(matches)} matching references:")
        for ref in matches[:5]:
            print(f"- {ref.get('title', 'Untitled')} ({ref.get('year', 'n.d.')})")

if __name__ == "__main__":
    main()