#!/usr/bin/env python3
"""
Literature search module for academic research
Integrates with Scopus, Web of Science, and other databases
"""
import json
import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import requests
import logging
from dotenv import load_dotenv
from scripts.utils import get_project_root, load_config, save_json, get_timestamp

# Load environment variables
load_dotenv()

class LiteratureSearcher:
    def __init__(self):
        self.project_root = get_project_root()
        self.config = load_config("research-criteria.yaml")
        self.api_keys = self._load_api_keys()
        
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment variables and config file."""
        keys = {}
        
        # Load from environment variables first (takes precedence)
        env_keys = {
            "proquest": {
                "institution_url": os.getenv("PROQUEST_INSTITUTION_URL"),
                "username": os.getenv("PROQUEST_USERNAME"),
                "password": os.getenv("PROQUEST_PASSWORD"),
                "api_key": os.getenv("PROQUEST_API_KEY")
            },
            "scopus_api_key": os.getenv("SCOPUS_API_KEY"),
            "wos_api_key": os.getenv("WOS_API_KEY"),
            "crossref_email": os.getenv("CROSSREF_EMAIL"),
            "citavi_path": os.getenv("CITAVI_PROJECT_PATH")
        }
        
        # Remove None values
        keys = {k: v for k, v in env_keys.items() if v is not None}
        
        # Load from config file as fallback
        api_file = self.project_root / "config" / "api_keys.yaml"
        if api_file.exists():
            import yaml
            with open(api_file, 'r') as f:
                file_keys = yaml.safe_load(f)
                # Merge, but env vars take precedence
                for k, v in file_keys.items():
                    if k not in keys:
                        keys[k] = v
        
        return keys
    
    def search(self, query: str, databases: List[str] = None, 
              years: str = "2020-2025", quality: str = "q1") -> List[Dict[str, Any]]:
        """
        Search for literature across multiple databases.
        
        Args:
            query: Search query string
            databases: List of databases to search
            years: Year range (e.g., "2020-2025")
            quality: Quality filter (q1, q2, etc.)
        
        Returns:
            List of found papers with metadata
        """
        results = []
        
        # Default databases if not specified
        if not databases:
            databases = ["Google Scholar", "Crossref", "arXiv"]
        
        # Search free databases (no API keys needed)
        if "Google Scholar" in databases:
            results.extend(self._search_google_scholar(query, years))
        if "Crossref" in databases:
            results.extend(self._search_crossref(query, years))
        if "arXiv" in databases:
            results.extend(self._search_arxiv(query, years))
            
        # Search API-based databases if keys available
        if self.api_keys:
            if "scopus_api_key" in self.api_keys and "Scopus" in databases:
                results.extend(self._search_scopus(query, years))
            if "wos_api_key" in self.api_keys and "Web of Science" in databases:
                results.extend(self._search_wos(query, years))
        
        # Filter by quality
        if quality == "q1":
            results = [r for r in results if r.get("quartile") == "Q1" or r.get("impact_factor", 0) > 3.0]
        
        # Save results
        timestamp = get_timestamp()
        output_file = self.project_root / "research" / "search-results" / f"search_results_{timestamp}.json"
        save_json({
            "query": query,
            "databases": databases,
            "years": years,
            "quality": quality,
            "timestamp": timestamp,
            "results": results
        }, output_file)
        
        return results
    
    def _get_mock_results(self, query: str, years: str) -> List[Dict[str, Any]]:
        """Return mock results for testing."""
        if "PRISMA" in query:
            return [
                {
                    "title": "The PRISMA 2020 statement: an updated guideline for reporting systematic reviews",
                    "authors": ["Page, M. J.", "McKenzie, J. E.", "Bossuyt, P. M."],
                    "year": "2021",
                    "journal": "BMJ",
                    "doi": "10.1136/bmj.n71",
                    "quartile": "Q1",
                    "impact_factor": 39.89,
                    "abstract": "The PRISMA 2020 statement provides updated reporting guidance for systematic reviews..."
                },
                {
                    "title": "PRISMA 2020 explanation and elaboration: updated guidance and exemplars",
                    "authors": ["Page, M. J.", "Moher, D.", "Bossuyt, P. M."],
                    "year": "2021",
                    "journal": "BMJ",
                    "doi": "10.1136/bmj.n160",
                    "quartile": "Q1",
                    "impact_factor": 39.89,
                    "abstract": "This document provides detailed explanation and elaboration of the PRISMA 2020 items..."
                }
            ]
        elif "AI agents" in query.lower():
            return [
                {
                    "title": "AI Agents in Financial Services: A Systematic Review",
                    "authors": ["Smith, J.", "Johnson, A.", "Williams, K."],
                    "year": "2023",
                    "journal": "Journal of Financial Technology",
                    "quartile": "Q1",
                    "impact_factor": 5.2,
                    "abstract": "This paper presents a systematic review of AI agent applications in finance..."
                }
            ]
        return []
    
    def _search_scopus(self, query: str, years: str) -> List[Dict[str, Any]]:
        """Search Scopus database (requires API key)."""
        # TODO: Implement Scopus API integration
        return []
    
    def _search_wos(self, query: str, years: str) -> List[Dict[str, Any]]:
        """Search Web of Science (requires API key)."""
        # TODO: Implement WoS API integration
        return []
    
    def _search_google_scholar(self, query: str, years: str) -> List[Dict[str, Any]]:
        """Search Google Scholar using scholarly package."""
        try:
            from scholarly import scholarly
            
            results = []
            start_year, end_year = years.split("-") if "-" in years else (years, years)
            
            # Add year filter to query
            year_query = f'{query} after:{start_year} before:{end_year}'
            
            # Search and limit results
            search_query = scholarly.search_pubs(year_query)
            
            for i, article in enumerate(search_query):
                if i >= 20:  # Limit to 20 results
                    break
                    
                try:
                    # Extract publication info
                    bib = article.get('bib', {})
                    
                    # Extract year
                    pub_year = str(bib.get('pub_year', ''))
                    if not pub_year or pub_year == 'NA':
                        continue
                    try:
                        year_int = int(pub_year)
                        if year_int < int(start_year) or year_int > int(end_year):
                            continue
                    except ValueError:
                        continue
                    
                    # Extract authors
                    authors = bib.get('author', '')
                    if isinstance(authors, list):
                        author_list = authors
                    elif isinstance(authors, str):
                        author_list = authors.split(' and ')
                    else:
                        author_list = []
                    
                    result = {
                        "title": bib.get('title', ''),
                        "authors": author_list,
                        "year": pub_year,
                        "journal": bib.get('venue', ''),
                        "abstract": bib.get('abstract', ''),
                        "citations": article.get('num_citations', 0),
                        "url": article.get('pub_url', ''),
                        "eprint_url": article.get('eprint_url', ''),
                        "database": "Google Scholar"
                    }
                    
                    # Estimate quality based on citations and venue
                    if result["citations"] > 50:
                        result["quartile"] = "Q1"
                    elif result["citations"] > 20:
                        result["quartile"] = "Q2"
                    else:
                        result["quartile"] = "Q3"
                    
                    results.append(result)
                    
                except Exception as e:
                    logging.warning(f"Error parsing Google Scholar result: {e}")
                    continue
                    
            return results
            
        except Exception as e:
            logging.error(f"Google Scholar search error: {e}")
            return []
    
    def _search_crossref(self, query: str, years: str) -> List[Dict[str, Any]]:
        """Search Crossref (free API, no key required but email recommended)."""
        try:
            import requests
            
            results = []
            start_year, end_year = years.split("-") if "-" in years else (years, years)
            
            # Crossref API endpoint
            base_url = "https://api.crossref.org/works"
            
            # Set user agent with email if provided
            headers = {
                "User-Agent": f"Masterarbeit-Research/1.0 (mailto:{os.getenv('CROSSREF_EMAIL', 'research@example.com')})"
            }
            
            params = {
                "query": query,
                "filter": f"from-pub-date:{start_year},until-pub-date:{end_year}",
                "rows": 20,
                "select": "DOI,title,author,published-print,container-title,abstract,is-referenced-by-count,type,subject"
            }
            
            response = requests.get(base_url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('message', {}).get('items', []):
                    # Extract authors
                    authors = []
                    for author in item.get('author', []):
                        name = f"{author.get('family', '')}, {author.get('given', '')}"
                        authors.append(name.strip(', '))
                    
                    # Extract year
                    date_parts = item.get('published-print', {}).get('date-parts', [[]])[0]
                    year = str(date_parts[0]) if date_parts else ""
                    
                    result = {
                        "title": item.get('title', [''])[0],
                        "authors": authors,
                        "year": year,
                        "journal": item.get('container-title', [''])[0],
                        "doi": item.get('DOI', ''),
                        "abstract": item.get('abstract', ''),
                        "citations": item.get('is-referenced-by-count', 0),
                        "type": item.get('type', ''),
                        "subjects": item.get('subject', []),
                        "database": "Crossref"
                    }
                    
                    # Quality assessment based on citations
                    if result["citations"] > 100:
                        result["quartile"] = "Q1"
                    elif result["citations"] > 50:
                        result["quartile"] = "Q2"
                    else:
                        result["quartile"] = "Q3"
                    
                    results.append(result)
                    
            return results
            
        except Exception as e:
            logging.error(f"Crossref search error: {e}")
            return []
    
    def _search_arxiv(self, query: str, years: str) -> List[Dict[str, Any]]:
        """Search arXiv for computer science and AI papers."""
        try:
            import arxiv
            
            results = []
            start_year, end_year = years.split("-") if "-" in years else (years, years)
            
            # Search arXiv
            search = arxiv.Search(
                query=query,
                max_results=20,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            for paper in search.results():
                # Filter by year
                pub_year = paper.published.year
                if pub_year < int(start_year) or pub_year > int(end_year):
                    continue
                
                result = {
                    "title": paper.title,
                    "authors": [author.name for author in paper.authors],
                    "year": str(pub_year),
                    "journal": "arXiv",
                    "abstract": paper.summary,
                    "arxiv_id": paper.entry_id,
                    "pdf_url": paper.pdf_url,
                    "categories": paper.categories,
                    "database": "arXiv",
                    "quartile": "Preprint"  # arXiv papers are not peer-reviewed
                }
                
                results.append(result)
                
            return results
            
        except Exception as e:
            logging.error(f"arXiv search error: {e}")
            return []
    
    

def main():
    parser = argparse.ArgumentParser(description="Search academic literature")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--databases", nargs="+", help="Databases to search")
    parser.add_argument("--years", default="2020-2025", help="Year range")
    parser.add_argument("--quality", default="q1", help="Quality filter (q1, q2, etc.)")
    
    args = parser.parse_args()
    
    searcher = LiteratureSearcher()
    results = searcher.search(
        query=args.query,
        databases=args.databases,
        years=args.years,
        quality=args.quality
    )
    
    print(f"Found {len(results)} papers matching criteria")
    for i, paper in enumerate(results[:5], 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Authors: {', '.join(paper['authors'])}")
        print(f"   Year: {paper['year']}, Journal: {paper['journal']}")
        print(f"   Quality: {paper.get('quartile', 'N/A')}, IF: {paper.get('impact_factor', 'N/A')}")

if __name__ == "__main__":
    main()