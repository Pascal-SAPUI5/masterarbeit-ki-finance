#!/usr/bin/env python3
"""
Enhanced Google Scholar search with CAPTCHA bypass capabilities
Designed for Docker container deployment with anti-detection measures
"""

import json
import time
import random
import logging
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
import requests
from urllib.parse import quote_plus
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RateLimitConfig:
    """Rate limiting configuration to avoid CAPTCHA triggers"""
    
    def __init__(self):
        self.min_delay = 2.0  # Minimum delay between requests
        self.max_delay = 8.0  # Maximum delay between requests
        self.long_delay = 30.0  # Delay after potential CAPTCHA detection
        self.requests_per_minute = 8  # Conservative rate limit
        self.daily_limit = 500  # Daily search limit
        self.retry_attempts = 3
        self.backoff_multiplier = 2.0
        
    def get_delay(self) -> float:
        """Get randomized delay to appear more human-like"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def get_long_delay(self) -> float:
        """Get longer delay after potential detection"""
        return random.uniform(self.long_delay, self.long_delay * 2)

class CaptchaBypassSearcher:
    """Enhanced Google Scholar searcher with CAPTCHA bypass capabilities"""
    
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.ua = UserAgent()
        self.driver = None
        self.session_start = datetime.now()
        self.request_count = 0
        self.last_request_time = None
        self.results = []
        
        # Proxy rotation (add your proxy list here)
        self.proxies = [
            # Add your proxy servers here if available
            # {'http': 'http://proxy1:port', 'https': 'https://proxy1:port'},
        ]
        self.current_proxy_index = 0
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup undetected Chrome driver with anti-detection measures"""
        try:
            options = Options()
            
            # Basic options for Docker/headless operation
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            # Anti-detection options
            options.add_argument(f'--user-agent={self.ua.random}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Additional stealth options
            options.add_argument('--disable-plugins-discovery')
            options.add_argument('--disable-extensions-file-access-check')
            options.add_argument('--disable-extensions-http-throttling')
            options.add_argument('--disable-extensions-except')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            
            # Create undetected Chrome driver
            driver = uc.Chrome(options=options)
            
            # Execute stealth script to hide automation indicators
            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)
            
            # Set additional navigator properties
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": self.ua.random
            })
            
            logger.info("Chrome driver initialized with anti-detection measures")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            # Fallback to regular Chrome driver
            return self._setup_fallback_driver()
    
    def _setup_fallback_driver(self) -> webdriver.Chrome:
        """Fallback driver setup if undetected-chromedriver fails"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--user-agent={self.ua.random}')
        
        return webdriver.Chrome(options=options)
    
    def _is_captcha_present(self) -> bool:
        """Detect if CAPTCHA is present on the page"""
        captcha_indicators = [
            'please show you\'re not a robot',
            'unusual traffic',
            'verify you are human',
            'solving this puzzle',
            'captcha-container',
            'g-recaptcha',
            'recaptcha',
            'blocked by google',
            'suspicious activity'
        ]
        
        # More specific indicators that are less likely to cause false positives
        high_confidence_indicators = [
            'captcha',
            'recaptcha',
            'please show you\'re not a robot',
            'verify you are human'
        ]
        
        page_source = self.driver.page_source.lower()
        
        # Check for high-confidence indicators first
        for indicator in high_confidence_indicators:
            if indicator in page_source:
                # Additional validation to reduce false positives
                if 'search-results' not in page_source and 'scholar' not in page_source:
                    logger.warning(f"CAPTCHA detected: {indicator}")
                    return True
        
        # Check for other indicators only if not on a normal search results page
        if 'search-results' not in page_source:
            for indicator in captcha_indicators:
                if indicator in page_source:
                    logger.warning(f"CAPTCHA detected: {indicator}")
                    return True
        
        # Check for CAPTCHA elements
        try:
            captcha_elements = self.driver.find_elements(By.XPATH, "//*[contains(@class, 'captcha') or contains(@id, 'captcha') or contains(@class, 'recaptcha')]")
            if captcha_elements:
                logger.warning("CAPTCHA element found in DOM")
                return True
        except:
            pass
        
        return False
    
    def _handle_captcha(self) -> bool:
        """Handle CAPTCHA detection"""
        logger.warning("CAPTCHA detected - implementing bypass strategy")
        
        # Strategy 1: Wait and retry with new session
        self.driver.quit()
        time.sleep(self.config.get_long_delay())
        
        # Rotate proxy if available
        self._rotate_proxy()
        
        # Create new driver with different fingerprint
        self.driver = self._setup_driver()
        
        logger.info("New session created after CAPTCHA detection")
        return True
    
    def _rotate_proxy(self):
        """Rotate to next proxy in the list"""
        if self.proxies:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            logger.info(f"Rotated to proxy {self.current_proxy_index}")
    
    def _respect_rate_limits(self):
        """Implement intelligent rate limiting"""
        current_time = datetime.now()
        
        if self.last_request_time:
            time_since_last = (current_time - self.last_request_time).total_seconds()
            min_delay = 60.0 / self.config.requests_per_minute
            
            if time_since_last < min_delay:
                sleep_time = min_delay - time_since_last + random.uniform(0.5, 2.0)
                logger.info(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self.last_request_time = datetime.now()
        self.request_count += 1
    
    def search_google_scholar(self, query: str, max_results: int = 50, years: str = "2020-2025") -> List[Dict[str, Any]]:
        """Enhanced Google Scholar search with CAPTCHA bypass"""
        
        if not self.driver:
            self.driver = self._setup_driver()
        
        results = []
        start_year, end_year = years.split("-") if "-" in years else (years, years)
        
        try:
            # Construct search URL
            search_query = f'{query} after:{start_year} before:{end_year}'
            encoded_query = quote_plus(search_query)
            base_url = f"https://scholar.google.com/scholar?q={encoded_query}&hl=en"
            
            logger.info(f"Searching Google Scholar: {search_query}")
            
            page = 0
            max_pages = min(5, (max_results // 10) + 1)  # Limit pages to avoid detection
            
            while page < max_pages and len(results) < max_results:
                # Respect rate limits
                self._respect_rate_limits()
                
                # Construct URL for current page
                if page == 0:
                    url = base_url
                else:
                    url = f"{base_url}&start={page * 10}"
                
                logger.info(f"Fetching page {page + 1}: {url}")
                
                # Navigate to page
                self.driver.get(url)
                
                # Wait for page to load
                time.sleep(random.uniform(2, 5))
                
                # Check for CAPTCHA
                if self._is_captcha_present():
                    if not self._handle_captcha():
                        logger.error("Failed to handle CAPTCHA")
                        break
                    continue  # Retry current page
                
                # Parse results from current page
                page_results = self._parse_scholar_page()
                
                if not page_results:
                    logger.warning("No results found on current page")
                    break
                
                results.extend(page_results)
                logger.info(f"Found {len(page_results)} results on page {page + 1}")
                
                page += 1
                
                # Random delay between pages
                time.sleep(self.config.get_delay())
            
            logger.info(f"Total results found: {len(results)}")
            return results[:max_results]
            
        except Exception as e:
            logger.error(f"Error during Google Scholar search: {e}")
            return results
        
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def _parse_scholar_page(self) -> List[Dict[str, Any]]:
        """Parse results from a Google Scholar page"""
        results = []
        
        try:
            # Wait for results to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-lid]"))
            )
            
            # Find all result entries
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-lid]")
            
            for element in result_elements:
                try:
                    result = self._parse_result_element(element)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"Error parsing result element: {e}")
                    continue
            
        except TimeoutException:
            logger.warning("Timeout waiting for results to load")
        except Exception as e:
            logger.error(f"Error parsing page: {e}")
        
        return results
    
    def _parse_result_element(self, element) -> Optional[Dict[str, Any]]:
        """Parse individual result element"""
        try:
            # Extract title
            title_element = element.find_element(By.CSS_SELECTOR, "h3 a")
            title = title_element.text if title_element else ""
            url = title_element.get_attribute("href") if title_element else ""
            
            # Extract authors and journal info
            authors_element = element.find_elements(By.CSS_SELECTOR, ".gs_a")
            authors_text = authors_element[0].text if authors_element else ""
            
            # Parse authors and year
            authors, year, journal = self._parse_authors_info(authors_text)
            
            # Extract citations
            citations = 0
            citation_elements = element.find_elements(By.CSS_SELECTOR, ".gs_fl a")
            for cite_elem in citation_elements:
                text = cite_elem.text
                if "Cited by" in text:
                    citations = int(text.replace("Cited by ", ""))
                    break
            
            # Extract snippet/abstract
            snippet_elements = element.find_elements(By.CSS_SELECTOR, ".gs_rs")
            abstract = snippet_elements[0].text if snippet_elements else ""
            
            # Estimate quality metrics
            quartile, impact_factor = self._estimate_quality(journal, citations)
            
            result = {
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": abstract,
                "citations": citations,
                "url": url,
                "quartile": quartile,
                "impact_factor": impact_factor,
                "database": "Google Scholar (Enhanced)"
            }
            
            return result
            
        except Exception as e:
            logger.warning(f"Error parsing result element: {e}")
            return None
    
    def _parse_authors_info(self, authors_text: str) -> tuple:
        """Parse authors, year, and journal from author info string"""
        authors = []
        year = ""
        journal = ""
        
        try:
            # Split by dashes and commas to extract components
            parts = authors_text.split(" - ")
            
            if len(parts) >= 1:
                # First part usually contains authors
                author_part = parts[0]
                authors = [name.strip() for name in author_part.split(",")]
            
            if len(parts) >= 2:
                # Second part usually contains journal and year
                pub_info = parts[1]
                
                # Extract year (usually 4 digits)
                import re
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', pub_info)
                if year_match:
                    year = year_match.group(1)
                
                # Journal is the remaining text
                journal = re.sub(r'\b(20\d{2}|19\d{2})\b', '', pub_info).strip(" ,-")
        
        except Exception as e:
            logger.warning(f"Error parsing author info: {e}")
        
        return authors, year, journal
    
    def _estimate_quality(self, journal: str, citations: int) -> tuple:
        """Estimate journal quartile and impact factor"""
        # High-impact journals
        high_impact_keywords = [
            "Nature", "Science", "Cell", "PNAS", "IEEE", "ACM",
            "Journal of Finance", "Review of Financial Studies",
            "Financial Management", "Artificial Intelligence"
        ]
        
        journal_lower = journal.lower()
        
        # Quality estimation based on citations and journal
        if citations > 100 or any(keyword.lower() in journal_lower for keyword in high_impact_keywords[:4]):
            return "Q1", 5.0
        elif citations > 50 or any(keyword.lower() in journal_lower for keyword in high_impact_keywords[4:]):
            return "Q1", 3.5
        elif citations > 20:
            return "Q2", 2.0
        elif citations > 5:
            return "Q3", 1.0
        else:
            return "Q4", 0.5
    
    def save_results(self, results: List[Dict[str, Any]], output_file: Path):
        """Save search results to file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_results": len(results),
                    "results": results
                }, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Enhanced Google Scholar search with CAPTCHA bypass")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--max-results", type=int, default=50, help="Maximum results to fetch")
    parser.add_argument("--years", default="2020-2025", help="Year range")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon service")
    
    args = parser.parse_args()
    
    # Setup rate limiting configuration
    config = RateLimitConfig()
    
    # Create searcher
    searcher = CaptchaBypassSearcher(config)
    
    try:
        if args.daemon:
            logger.info("Starting in daemon mode - ready to process search requests")
            # TODO: Implement daemon mode with API endpoints
            time.sleep(3600)  # Keep alive for testing
        else:
            # Perform search
            results = searcher.search_google_scholar(
                query=args.query,
                max_results=args.max_results,
                years=args.years
            )
            
            # Save results
            if args.output:
                output_file = Path(args.output)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = Path(f"scholar_results_{timestamp}.json")
            
            searcher.save_results(results, output_file)
            
            # Print summary
            print(f"Search completed: {len(results)} results found")
            for i, result in enumerate(results[:5], 1):
                print(f"\n{i}. {result['title']}")
                print(f"   Authors: {', '.join(result['authors'])}")
                print(f"   Year: {result['year']}, Journal: {result['journal']}")
                print(f"   Citations: {result['citations']}, Quality: {result['quartile']}")
    
    except KeyboardInterrupt:
        logger.info("Search interrupted by user")
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())