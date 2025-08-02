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
            self.logger.error(f"Timeout loading {domain} search results")
            return []
        except Exception as e:
            self.logger.error(f"Error extracting papers from {domain}: {e}")
            return []
    
    def _extract_papers(self, 
                       driver, 
                       domain_config: Dict, 
                       max_results: int) -> List[Dict]:
        """Extract paper information from search results."""
        papers = []
        
        try:
            # Find all paper elements
            paper_elements = driver.find_elements(
                By.CSS_SELECTOR, 
                domain_config['paper_selector']
            )[:max_results]
            
            for element in paper_elements:
                try:
                    paper = self._extract_paper_info(element, domain_config)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    self.logger.debug(f"Error extracting paper: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"Error finding paper elements: {e}")
            
        return papers
    
    def _extract_paper_info(self, element, domain_config: Dict) -> Optional[Dict]:
        """Extract information from a single paper element."""
        try:
            paper = {}
            
            # Extract title
            try:
                title_elem = element.find_element(
                    By.CSS_SELECTOR, domain_config['title_selector']
                )
                paper['title'] = title_elem.text.strip()
            except:
                paper['title'] = "Title not found"
            
            # Extract authors
            try:
                authors_elem = element.find_element(
                    By.CSS_SELECTOR, domain_config['authors_selector']
                )
                paper['authors'] = authors_elem.text.strip()
            except:
                paper['authors'] = "Authors not found"
            
            # Extract abstract
            try:
                abstract_elem = element.find_element(
                    By.CSS_SELECTOR, domain_config['abstract_selector']
                )
                paper['abstract'] = abstract_elem.text.strip()
            except:
                paper['abstract'] = "Abstract not found"
            
            # Extract URL if available
            try:
                link_elem = element.find_element(By.TAG_NAME, 'a')
                paper['url'] = link_elem.get_attribute('href')
            except:
                paper['url'] = None
            
            # Add extraction timestamp
            paper['extracted_at'] = time.time()
            
            return paper if paper.get('title') != "Title not found" else None
            
        except Exception as e:
            self.logger.debug(f"Error extracting paper info: {e}")
            return None
    
    def download_paper(self, paper_url: str, output_path: Optional[str] = None) -> Optional[str]:
        """Download a paper PDF if available."""
        if not output_path:
            filename = f"paper_{int(time.time())}.pdf"
            output_path = self.output_dir / "papers" / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with BrowserContextManager(self.config) as driver:
                driver.get(paper_url)
                
                # Look for PDF download link
                pdf_selectors = [
                    'a[href$=".pdf"]',
                    '.download-pdf',
                    '.pdf-download',
                    '[data-action="download"]'
                ]
                
                pdf_url = None
                for selector in pdf_selectors:
                    try:
                        pdf_elem = driver.find_element(By.CSS_SELECTOR, selector)
                        pdf_url = pdf_elem.get_attribute('href')
                        if pdf_url:
                            break
                    except:
                        continue
                
                if not pdf_url:
                    # Try direct URL manipulation for common patterns
                    if 'arxiv.org' in paper_url:
                        pdf_url = paper_url.replace('/abs/', '/pdf/') + '.pdf'
                    else:
                        self.logger.warning(f"Could not find PDF link for {paper_url}")
                        return None
                
                # Download PDF
                response = requests.get(pdf_url, stream=True)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.logger.info(f"Downloaded paper to {output_path}")
                return str(output_path)
                
        except Exception as e:
            self.logger.error(f"Error downloading paper: {e}")
            return None
    
    def _save_results(self, domain: str, query: str, results: List[Dict]):
        """Save search results to JSON file."""
        timestamp = int(time.time())
        filename = f"{domain}_search_{timestamp}.json"
        output_file = self.output_dir / "search-results" / filename
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'domain': domain,
            'query': query,
            'timestamp': timestamp,
            'results_count': len(results),
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved {len(results)} results to {output_file}")
    
    def get_paper_details(self, paper_url: str) -> Optional[Dict]:
        """Get detailed information about a specific paper."""
        try:
            with BrowserContextManager(self.config) as driver:
                driver.get(paper_url)
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                details = {
                    'url': paper_url,
                    'title': self._safe_extract(driver, 'title', 'h1, .title, .article-title'),
                    'authors': self._safe_extract(driver, 'authors', '.authors, .author-list, .metadata-authors'),
                    'abstract': self._safe_extract(driver, 'abstract', '.abstract, .summary, [data-testid="abstract"]'),
                    'publication_date': self._safe_extract(driver, 'date', '.publication-date, .submitted-date, .date'),
                    'journal': self._safe_extract(driver, 'journal', '.journal, .venue, .publication-venue'),
                    'doi': self._safe_extract(driver, 'doi', '[data-doi], .doi'),
                    'keywords': self._safe_extract(driver, 'keywords', '.keywords, .tags, .subjects'),
                    'extracted_at': time.time()
                }
                
                return details
                
        except Exception as e:
            self.logger.error(f"Error getting paper details: {e}")
            return None
    
    def _safe_extract(self, driver, field_name: str, selectors: str) -> str:
        """Safely extract text from elements using multiple selectors."""
        for selector in selectors.split(', '):
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector.strip())
                text = element.text.strip()
                if text:
                    return text
            except:
                continue
        return f"{field_name.title()} not found"


def test_research_browser():
    """Test research browser functionality."""
    print("🔍 Testing research browser...")
    
    browser = ResearchBrowser()
    
    # Test search
    results = browser.search_papers(
        query="artificial intelligence finance",
        domains=['arxiv'],
        max_results=3
    )
    
    print(f"📊 Found {sum(len(papers) for papers in results.values())} papers")
    
    for domain, papers in results.items():
        print(f"\n{domain.upper()} Results:")
        for i, paper in enumerate(papers[:2], 1):
            print(f"  {i}. {paper.get('title', 'No title')[:80]}...")
            print(f"     Authors: {paper.get('authors', 'No authors')[:60]}...")
    
    return len(results) > 0


if __name__ == "__main__":
    test_research_browser()