#!/usr/bin/env python3
"""
Enhanced Literature Search with Intelligent Request Handling
Integrates the new request handler with existing search functionality
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import yaml

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.request_handler import IntelligentRequestHandler, RateLimitStrategy, ProxyConfig
from scripts.search_literature import LiteratureSearcher
from scripts.utils import get_project_root, load_config, save_json, get_timestamp

logger = logging.getLogger(__name__)


class EnhancedLiteratureSearcher(LiteratureSearcher):
    """
    Enhanced literature searcher with intelligent request handling
    """
    
    def __init__(self, use_intelligent_requests: bool = True):
        super().__init__()
        self.use_intelligent_requests = use_intelligent_requests
        self.request_handler: Optional[IntelligentRequestHandler] = None
        
        if use_intelligent_requests:
            self._setup_request_handler()
    
    def _setup_request_handler(self):
        """Setup the intelligent request handler"""
        try:
            # Load configuration
            config_path = self.project_root / "config" / "request_handler_config.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
            else:
                config = {}
            
            # Setup proxies if configured
            proxies = []
            if config.get('proxy_rotation', {}).get('enabled', False):
                proxy_configs = config.get('proxies', [])
                for proxy_config in proxy_configs:
                    proxies.append(ProxyConfig(
                        host=proxy_config['host'],
                        port=proxy_config['port'],
                        protocol=proxy_config.get('protocol', 'http'),
                        username=proxy_config.get('username'),
                        password=proxy_config.get('password')
                    ))
            
            # Create request handler
            self.request_handler = IntelligentRequestHandler(
                strategy=RateLimitStrategy.CONSERVATIVE,  # Use conservative strategy for academic searches
                proxies=proxies
            )
            
            logger.info("Intelligent request handler initialized")
            
        except Exception as e:
            logger.error(f"Failed to setup request handler: {e}")
            self.use_intelligent_requests = False
    
    async def _make_intelligent_request(self, url: str, session_id: str = 'scholar', **kwargs):
        """Make a request using the intelligent handler"""
        if not self.request_handler:
            raise RuntimeError("Request handler not initialized")
            
        status, response, content = await self.request_handler.make_request(
            url=url,
            session_id=session_id,
            **kwargs
        )
        
        return status, response, content
    
    async def search_google_scholar_intelligent(self, query: str, years: str = "2020-2025", max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search Google Scholar using intelligent request handling
        """
        if not self.use_intelligent_requests or not self.request_handler:
            logger.warning("Falling back to regular Google Scholar search")
            return self._search_google_scholar(query, years)
        
        try:
            results = []
            start_year, end_year = years.split("-") if "-" in years else (years, years)
            
            # Build search URL
            base_url = "https://scholar.google.com/scholar"
            year_query = f'{query} after:{start_year} before:{end_year}'
            
            # Parameters for Google Scholar
            params = {
                'q': year_query,
                'hl': 'en',
                'as_sdt': '0,5',  # Include patents and citations
                'num': min(max_results, 20)  # Google Scholar limits results per page
            }
            
            logger.info(f"Intelligent Google Scholar search: {year_query}")
            
            # Make intelligent request
            status, response, content = await self._make_intelligent_request(
                url=base_url,
                params=params,
                session_id='google_scholar'
            )
            
            if status.value == 'success' and content:
                # Parse results from HTML content
                results = await self._parse_scholar_results(content, start_year, end_year)
                logger.info(f"Found {len(results)} results from Google Scholar")
            else:
                logger.warning(f"Google Scholar request failed with status: {status.value}")
                
            # Get and log statistics
            stats = self.request_handler.get_stats()
            logger.info(f"Request stats - Success rate: {stats['success_rate']:.2%}, Current delay: {stats['current_delay']:.1f}s")
            
            return results
            
        except Exception as e:
            logger.error(f"Intelligent Google Scholar search error: {e}")
            return []
    
    async def _parse_scholar_results(self, html_content: str, start_year: str, end_year: str) -> List[Dict[str, Any]]:
        """
        Parse Google Scholar HTML results
        Note: This is a simplified parser. For production use, consider using BeautifulSoup
        """
        results = []
        
        try:
            # Import BeautifulSoup for HTML parsing
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find result divs (Google Scholar structure)
            result_divs = soup.find_all('div', {'class': 'gs_r gs_or gs_scl'})
            
            for div in result_divs:
                try:
                    # Extract title
                    title_tag = div.find('h3', {'class': 'gs_rt'})
                    title = title_tag.get_text() if title_tag else ""
                    
                    # Extract authors and publication info
                    info_tag = div.find('div', {'class': 'gs_a'})
                    info_text = info_tag.get_text() if info_tag else ""
                    
                    # Parse authors and year from info text
                    authors = []
                    year = ""
                    if info_text:
                        parts = info_text.split(' - ')
                        if len(parts) > 0:
                            # First part usually contains authors
                            author_part = parts[0]
                            authors = [a.strip() for a in author_part.split(',')]
                        
                        # Try to extract year
                        import re
                        year_match = re.search(r'\b(20\d{2})\b', info_text)
                        if year_match:
                            year = year_match.group(1)
                    
                    # Skip if year is outside range
                    if year:
                        try:
                            year_int = int(year)
                            if year_int < int(start_year) or year_int > int(end_year):
                                continue
                        except ValueError:
                            continue
                    
                    # Extract abstract/snippet
                    abstract_tag = div.find('span', {'class': 'gs_rs'})
                    abstract = abstract_tag.get_text() if abstract_tag else ""
                    
                    # Extract citation count
                    citations = 0
                    cite_tag = div.find('a', string=lambda text: text and 'Cited by' in text)
                    if cite_tag:
                        cite_text = cite_tag.get_text()
                        import re
                        cite_match = re.search(r'Cited by (\d+)', cite_text)
                        if cite_match:
                            citations = int(cite_match.group(1))
                    
                    # Extract URL
                    url = ""
                    link_tag = title_tag.find('a') if title_tag else None
                    if link_tag and link_tag.get('href'):
                        url = link_tag.get('href')
                    
                    result = {
                        "title": title.strip(),
                        "authors": authors,
                        "year": year,
                        "journal": "",  # Not easily extractable from Scholar
                        "abstract": abstract.strip(),
                        "citations": citations,
                        "url": url,
                        "database": "Google Scholar (Intelligent)"
                    }
                    
                    # Estimate quality based on citations
                    if citations > 100:
                        result["quartile"] = "Q1"
                        result["impact_factor"] = 5.0
                    elif citations > 50:
                        result["quartile"] = "Q1"
                        result["impact_factor"] = 3.5
                    elif citations > 20:
                        result["quartile"] = "Q2"
                        result["impact_factor"] = 2.0
                    else:
                        result["quartile"] = "Q3"
                        result["impact_factor"] = 1.0
                    
                    results.append(result)
                    
                except Exception as e:
                    logger.warning(f"Error parsing individual result: {e}")
                    continue
            
        except ImportError:
            logger.error("BeautifulSoup not available. Install with: pip install beautifulsoup4")
        except Exception as e:
            logger.error(f"Error parsing Scholar results: {e}")
        
        return results
    
    async def search_with_intelligent_handling(
        self, 
        query: str, 
        databases: List[str] = None,
        years: str = "2020-2025", 
        quality: str = "q1",
        max_results_per_db: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Enhanced search method using intelligent request handling
        """
        results = []
        
        # Default databases if not specified
        if not databases:
            databases = ["Google Scholar", "Crossref", "arXiv"]
        
        # Search databases with intelligent handling
        for database in databases:
            logger.info(f"Searching {database} with intelligent handling...")
            
            try:
                if database == "Google Scholar" and self.use_intelligent_requests:
                    db_results = await self.search_google_scholar_intelligent(
                        query, years, max_results_per_db
                    )
                else:
                    # Fall back to regular methods for other databases
                    if database == "Crossref":
                        db_results = self._search_crossref(query, years)
                    elif database == "arXiv":
                        db_results = self._search_arxiv(query, years)
                    else:
                        continue
                
                results.extend(db_results)
                logger.info(f"Found {len(db_results)} results from {database}")
                
            except Exception as e:
                logger.error(f"Error searching {database}: {e}")
        
        # Filter by quality as before
        if quality and quality.lower() != "all":
            if quality.lower() == "q1":
                results = [r for r in results if 
                          r.get("quartile") == "Q1" or 
                          r.get("impact_factor", 0) > 3.0 or
                          r.get("citations", 0) > 50]
            elif quality.lower() == "q2":
                results = [r for r in results if 
                          r.get("quartile") in ["Q1", "Q2"] or 
                          r.get("impact_factor", 0) > 2.0 or
                          r.get("citations", 0) > 20]
        
        # Save results with timestamp
        timestamp = get_timestamp()
        output_file = self.project_root / "research" / "search-results" / f"intelligent_search_{timestamp}.json"
        save_json({
            "query": query,
            "databases": databases,
            "years": years,
            "quality": quality,
            "timestamp": timestamp,
            "intelligent_handling": self.use_intelligent_requests,
            "results": results
        }, output_file)
        
        return results
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.request_handler:
            await self.request_handler.cleanup()


async def main():
    """Test the enhanced literature searcher"""
    searcher = EnhancedLiteratureSearcher(use_intelligent_requests=True)
    
    try:
        # Test query
        query = "artificial intelligence in financial services"
        print(f"Testing enhanced search for: {query}")
        
        results = await searcher.search_with_intelligent_handling(
            query=query,
            databases=["Google Scholar"],
            years="2020-2025",
            quality="q1",
            max_results_per_db=10
        )
        
        print(f"\nFound {len(results)} results:")
        for i, paper in enumerate(results[:3], 1):
            print(f"\n{i}. {paper['title']}")
            print(f"   Authors: {', '.join(paper['authors'][:3])}{'...' if len(paper['authors']) > 3 else ''}")
            print(f"   Year: {paper['year']}, Citations: {paper.get('citations', 'N/A')}")
            print(f"   Quality: {paper.get('quartile', 'N/A')}")
        
        # Print request statistics
        if searcher.request_handler:
            stats = searcher.request_handler.get_stats()
            print(f"\nRequest Statistics:")
            print(f"  Total requests: {stats['total_requests']}")
            print(f"  Success rate: {stats['success_rate']:.2%}")
            print(f"  Current delay: {stats['current_delay']:.1f}s")
            print(f"  Average response time: {stats['average_response_time']:.2f}s")
        
    finally:
        await searcher.cleanup()


if __name__ == "__main__":
    asyncio.run(main())