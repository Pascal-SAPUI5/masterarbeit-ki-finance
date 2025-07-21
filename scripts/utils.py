"""
Utility functions for the research project
"""
import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    # Go up from scripts/ to project root
    return current.parent.parent

def load_config(config_name: str = "research-criteria.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    root = get_project_root()
    config_path = root / "config" / config_name
    
    if not config_path.exists():
        # Try alternative configs
        alternatives = ["rag_config.yaml", "mba-standards.json", "writing-style.yaml"]
        for alt in alternatives:
            alt_path = root / "config" / alt
            if alt_path.exists():
                config_path = alt_path
                break
    
    if config_path.suffix == ".yaml":
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    elif config_path.suffix == ".json":
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

def ensure_directories():
    """Ensure all required directories exist."""
    root = get_project_root()
    dirs = [
        "research/q1-sources",
        "research/search-results",
        "research/quality_reports",
        "writing/templates",
        "writing/chapters",
        "writing/drafts",
        "output",
        "backups",
        "indexes",
        ".claude_memory"
    ]
    
    for dir_path in dirs:
        (root / dir_path).mkdir(parents=True, exist_ok=True)

def save_json(data: Any, filepath: Path):
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath: Path) -> Any:
    """Load data from JSON file."""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_timestamp() -> str:
    """Get current timestamp string."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def format_citation_apa(author: str, year: str, title: str, journal: str = "") -> str:
    """Format a basic APA citation."""
    if journal:
        return f"{author} ({year}). {title}. {journal}."
    return f"{author} ({year}). {title}."