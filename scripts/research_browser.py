#!/usr/bin/env python3
"""
Research Browser Integration
============================

This module provides browser-based research capabilities for the master thesis
AI finance project, specifically designed for Docker container environments.
"""

import os
import time
import json
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse
import logging

from browser_config import DockerBrowserConfig, BrowserContextManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


class ResearchBrowser:
    """Browser-based research automation for academic sources."""
    
    def __init__(self, 
                 config: Optional[DockerBrowserConfig] = None,
                 output_dir: str = "/app/research"):
        """
        Initialize research browser.
        
        Args:
            config: Browser configuration (optional)
            output_dir: Directory for research outputs
        """
        self.config = config or DockerBrowserConfig()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Research domains configuration
        self.research_domains = {
            'arxiv': {
                'base_url': 'https://arxiv.org',
                'search_path': '/search/?query={}&searchtype=all',
                'paper_selector': '.arxiv-result',
                'title_selector': '.list-title',
                'authors_selector': '.list-authors',
                'abstract_selector': '.list-abstract'
            },
            'scholar': {
                'base_url': 'https://scholar.google.com',
                'search_path': '/scholar?q={}',
                'paper_selector': '.scholar-result',
                'title_selector': '.gs_rt',
                'authors_selector': '.gs_a',
                'abstract_selector': '.gs_rs'
            },
            'ieee': {
                'base_url': 'https://ieeexplore.ieee.org',
                'search_path': '/search/searchresult.jsp?newsearch=true&queryText={}',
                'paper_selector': '.List-results-items',
                'title_selector': '.ng-binding',
                'authors_selector': '.author',
                'abstract_selector': '.abstract'
            }
        }
    
    def search_papers(self, 
                     query: str, 
                     domains: List[str] = ['arxiv'],
                     max_results: int = 10) -> Dict[str, List[Dict]]:
        """
        Search for academic papers across multiple domains.
        
        Args:
            query: Search query
            domains: List of domains to search
            max_results: Maximum results per domain
            
        Returns:
            Dictionary with domain as key, list of papers as value
        """
        results = {}
        
        with BrowserContextManager(self.config) as driver:
            for domain in domains:
                if domain not in self.research_domains:
                    self.logger.warning(f"Unknown domain: {domain}")
                    continue
                    
                try:
                    domain_results = self._search_domain(
                        driver, domain, query, max_results
                    )
                    results[domain] = domain_results
                    
                    # Save intermediate results
                    self._save_results(domain, query, domain_results)
                    
                    # Delay between domains to be respectful
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error searching {domain}: {e}")
                    results[domain] = []
        
        return results
    
    def _search_domain(self, 
                      driver, 
                      domain: str, 
                      query: str, 
                      max_results: int) -> List[Dict]:
        """Search a specific domain for papers."""
        domain_config = self.research_domains[domain]
        
        # Load cookies for domain
        domain_name = urlparse(domain_config['base_url']).netloc
        self.config.load_cookies(driver, domain_name)
        
        # Construct search URL
        search_url = urljoin(
            domain_config['base_url'],
            domain_config['search_path'].format(query.replace(' ', '+'))
        )
        
        self.logger.info(f"Searching {domain}: {search_url}")
        
        try:
            driver.get(search_url)
            
            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
            )
            
            # Extract papers based on domain-specific selectors
            papers = self._extract_papers(driver, domain_config, max_results)
            
            # Save cookies after successful interaction
            self.config.save_cookies(driver, domain_name)
            
            return papers
            
        except TimeoutException:
            self.logger.error(f"Timeout loading {domain} search results")\n            return []\n        except Exception as e:\n            self.logger.error(f"Error extracting papers from {domain}: {e}")\n            return []\n    \n    def _extract_papers(self, \n                       driver, \n                       domain_config: Dict, \n                       max_results: int) -> List[Dict]:\n        """Extract paper information from search results."""\n        papers = []\n        \n        try:\n            # Find all paper elements\n            paper_elements = driver.find_elements(\n                By.CSS_SELECTOR, \n                domain_config['paper_selector']\n            )[:max_results]\n            \n            for element in paper_elements:\n                try:\n                    paper = self._extract_paper_info(element, domain_config)\n                    if paper:\n                        papers.append(paper)\n                except Exception as e:\n                    self.logger.debug(f"Error extracting paper: {e}")\n                    continue\n                    \n        except Exception as e:\n            self.logger.error(f"Error finding paper elements: {e}")\n            \n        return papers\n    \n    def _extract_paper_info(self, element, domain_config: Dict) -> Optional[Dict]:\n        """Extract information from a single paper element."""\n        try:\n            paper = {}\n            \n            # Extract title\n            try:\n                title_elem = element.find_element(\n                    By.CSS_SELECTOR, domain_config['title_selector']\n                )\n                paper['title'] = title_elem.text.strip()\n            except:\n                paper['title'] = \"Title not found\"\n            \n            # Extract authors\n            try:\n                authors_elem = element.find_element(\n                    By.CSS_SELECTOR, domain_config['authors_selector']\n                )\n                paper['authors'] = authors_elem.text.strip()\n            except:\n                paper['authors'] = \"Authors not found\"\n            \n            # Extract abstract\n            try:\n                abstract_elem = element.find_element(\n                    By.CSS_SELECTOR, domain_config['abstract_selector']\n                )\n                paper['abstract'] = abstract_elem.text.strip()\n            except:\n                paper['abstract'] = \"Abstract not found\"\n            \n            # Extract URL if available\n            try:\n                link_elem = element.find_element(By.TAG_NAME, 'a')\n                paper['url'] = link_elem.get_attribute('href')\n            except:\n                paper['url'] = None\n            \n            # Add extraction timestamp\n            paper['extracted_at'] = time.time()\n            \n            return paper if paper.get('title') != \"Title not found\" else None\n            \n        except Exception as e:\n            self.logger.debug(f\"Error extracting paper info: {e}\")\n            return None\n    \n    def download_paper(self, paper_url: str, output_path: Optional[str] = None) -> Optional[str]:\n        \"\"\"Download a paper PDF if available.\"\"\"\n        if not output_path:\n            filename = f\"paper_{int(time.time())}.pdf\"\n            output_path = self.output_dir / \"papers\" / filename\n            output_path.parent.mkdir(parents=True, exist_ok=True)\n        \n        try:\n            with BrowserContextManager(self.config) as driver:\n                driver.get(paper_url)\n                \n                # Look for PDF download link\n                pdf_selectors = [\n                    'a[href$=\".pdf\"]',\n                    '.download-pdf',\n                    '.pdf-download',\n                    '[data-action=\"download\"]'\n                ]\n                \n                pdf_url = None\n                for selector in pdf_selectors:\n                    try:\n                        pdf_elem = driver.find_element(By.CSS_SELECTOR, selector)\n                        pdf_url = pdf_elem.get_attribute('href')\n                        if pdf_url:\n                            break\n                    except:\n                        continue\n                \n                if not pdf_url:\n                    # Try direct URL manipulation for common patterns\n                    if 'arxiv.org' in paper_url:\n                        pdf_url = paper_url.replace('/abs/', '/pdf/') + '.pdf'\n                    else:\n                        self.logger.warning(f\"Could not find PDF link for {paper_url}\")\n                        return None\n                \n                # Download PDF\n                response = requests.get(pdf_url, stream=True)\n                response.raise_for_status()\n                \n                with open(output_path, 'wb') as f:\n                    for chunk in response.iter_content(chunk_size=8192):\n                        f.write(chunk)\n                \n                self.logger.info(f\"Downloaded paper to {output_path}\")\n                return str(output_path)\n                \n        except Exception as e:\n            self.logger.error(f\"Error downloading paper: {e}\")\n            return None\n    \n    def _save_results(self, domain: str, query: str, results: List[Dict]):\n        \"\"\"Save search results to JSON file.\"\"\"\n        timestamp = int(time.time())\n        filename = f\"{domain}_search_{timestamp}.json\"\n        output_file = self.output_dir / \"search-results\" / filename\n        output_file.parent.mkdir(parents=True, exist_ok=True)\n        \n        data = {\n            'domain': domain,\n            'query': query,\n            'timestamp': timestamp,\n            'results_count': len(results),\n            'results': results\n        }\n        \n        with open(output_file, 'w', encoding='utf-8') as f:\n            json.dump(data, f, indent=2, ensure_ascii=False)\n        \n        self.logger.info(f\"Saved {len(results)} results to {output_file}\")\n    \n    def get_paper_details(self, paper_url: str) -> Optional[Dict]:\n        \"\"\"Get detailed information about a specific paper.\"\"\"\n        try:\n            with BrowserContextManager(self.config) as driver:\n                driver.get(paper_url)\n                \n                # Wait for page to load\n                WebDriverWait(driver, 10).until(\n                    EC.presence_of_element_located((By.TAG_NAME, \"body\"))\n                )\n                \n                details = {\n                    'url': paper_url,\n                    'title': self._safe_extract(driver, 'title', 'h1, .title, .article-title'),\n                    'authors': self._safe_extract(driver, 'authors', '.authors, .author-list, .metadata-authors'),\n                    'abstract': self._safe_extract(driver, 'abstract', '.abstract, .summary, [data-testid=\"abstract\"]'),\n                    'publication_date': self._safe_extract(driver, 'date', '.publication-date, .submitted-date, .date'),\n                    'journal': self._safe_extract(driver, 'journal', '.journal, .venue, .publication-venue'),\n                    'doi': self._safe_extract(driver, 'doi', '[data-doi], .doi'),\n                    'keywords': self._safe_extract(driver, 'keywords', '.keywords, .tags, .subjects'),\n                    'extracted_at': time.time()\n                }\n                \n                return details\n                \n        except Exception as e:\n            self.logger.error(f\"Error getting paper details: {e}\")\n            return None\n    \n    def _safe_extract(self, driver, field_name: str, selectors: str) -> str:\n        \"\"\"Safely extract text from elements using multiple selectors.\"\"\"\n        for selector in selectors.split(', '):\n            try:\n                element = driver.find_element(By.CSS_SELECTOR, selector.strip())\n                text = element.text.strip()\n                if text:\n                    return text\n            except:\n                continue\n        return f\"{field_name.title()} not found\"\n\n\ndef test_research_browser():\n    \"\"\"Test research browser functionality.\"\"\"\n    print(\"🔍 Testing research browser...\")\n    \n    browser = ResearchBrowser()\n    \n    # Test search\n    results = browser.search_papers(\n        query=\"artificial intelligence finance\",\n        domains=['arxiv'],\n        max_results=3\n    )\n    \n    print(f\"📊 Found {sum(len(papers) for papers in results.values())} papers\")\n    \n    for domain, papers in results.items():\n        print(f\"\\n{domain.upper()} Results:\")\n        for i, paper in enumerate(papers[:2], 1):\n            print(f\"  {i}. {paper.get('title', 'No title')[:80]}...\")\n            print(f\"     Authors: {paper.get('authors', 'No authors')[:60]}...\")\n    \n    return len(results) > 0\n\n\nif __name__ == \"__main__\":\n    test_research_browser()