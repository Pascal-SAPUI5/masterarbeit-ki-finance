#!/usr/bin/env python3
"""
Browser Automation Module for Academic Literature Searches
Implements Selenium with headless Chrome, user-agent rotation, request delays, and CAPTCHA detection
"""

import json
import time
import logging
import random
import requests
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import os
import sys
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import tempfile
import base64
from io import BytesIO

# Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available. Install with: pip install selenium")

# Image processing for CAPTCHA detection
try:
    from PIL import Image
    import pytesseract
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False
    logging.warning("Image processing not available. Install with: pip install Pillow pytesseract")

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils import get_project_root, load_config, save_json, get_timestamp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BrowserConfig:
    """Configuration for browser automation"""
    headless: bool = True
    window_size: Tuple[int, int] = (1920, 1080)
    page_load_timeout: int = 30
    implicit_wait: int = 10
    request_delay_range: Tuple[int, int] = (5, 15)
    max_retries: int = 3
    user_agents: List[str] = None
    proxy_enabled: bool = False
    proxy_list: List[str] = None
    captcha_detection: bool = True
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                # Chrome on Windows
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                # Chrome on macOS  
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                # Firefox on Windows
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                # Firefox on macOS
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
                # Edge on Windows
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
                # Academic/Research specific
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Academic/1.0",
            ]

class CaptchaDetector:
    """CAPTCHA detection and handling"""
    
    def __init__(self, config: BrowserConfig):
        self.config = config
        self.captcha_indicators = [
            # Common CAPTCHA elements
            "captcha", "recaptcha", "hcaptcha", "g-recaptcha",
            # Text indicators
            "verify you are human", "prove you're not a robot", 
            "security check", "anti-robot verification",
            # Image-based
            "select all images", "click on", "verify by selecting",
            # Challenge elements
            "challenge", "verification", "robot check"
        ]
        
    def detect_captcha(self, driver) -> Tuple[bool, str, Optional[str]]:
        """
        Detect if CAPTCHA is present on current page
        
        Returns:
            Tuple of (has_captcha, captcha_type, screenshot_path)
        """
        try:
            # Check for common CAPTCHA iframes
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                src = iframe.get_attribute("src") or ""
                if any(indicator in src.lower() for indicator in ["captcha", "recaptcha", "hcaptcha"]):
                    screenshot_path = self._save_screenshot(driver, "captcha_iframe")
                    return True, "iframe_captcha", screenshot_path
            
            # Check page source for CAPTCHA indicators
            page_source = driver.page_source.lower()
            for indicator in self.captcha_indicators:
                if indicator in page_source:
                    screenshot_path = self._save_screenshot(driver, f"captcha_{indicator.replace(' ', '_')}")
                    return True, f"text_indicator_{indicator}", screenshot_path
            
            # Check for specific CAPTCHA elements
            captcha_elements = [
                (By.CLASS_NAME, "g-recaptcha"),
                (By.CLASS_NAME, "h-captcha"),
                (By.ID, "captcha"),
                (By.ID, "recaptcha"),
                (By.XPATH, "//div[contains(@class, 'captcha')]"),
                (By.XPATH, "//img[contains(@alt, 'captcha')]"),
                (By.XPATH, "//input[contains(@name, 'captcha')]"),
            ]
            
            for by, selector in captcha_elements:
                try:
                    elements = driver.find_elements(by, selector)
                    if elements:
                        screenshot_path = self._save_screenshot(driver, f"captcha_element_{selector}")
                        return True, f"element_captcha_{selector}", screenshot_path
                except Exception:
                    continue
            
            # Check for rate limiting indicators
            rate_limit_indicators = [
                "too many requests", "rate limit", "blocked", "access denied",
                "temporary block", "suspicious activity", "try again later"
            ]
            
            for indicator in rate_limit_indicators:
                if indicator in page_source:
                    screenshot_path = self._save_screenshot(driver, f"rate_limit_{indicator.replace(' ', '_')}")
                    return True, f"rate_limit_{indicator}", screenshot_path
            
            return False, "none", None
            
        except Exception as e:
            logger.error(f"Error detecting CAPTCHA: {e}")
            return False, "detection_error", None
    
    def _save_screenshot(self, driver, prefix: str) -> str:
        """Save screenshot for CAPTCHA analysis"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{prefix}_{timestamp}.png"
            screenshots_dir = get_project_root() / "output" / "captcha_screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            screenshot_path = screenshots_dir / filename
            driver.save_screenshot(str(screenshot_path))
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return None
    
    def analyze_captcha_image(self, screenshot_path: str) -> Dict[str, Any]:
        """Analyze CAPTCHA image using OCR"""
        if not IMAGE_PROCESSING_AVAILABLE:
            return {"error": "Image processing not available"}
        
        try:
            # Load and analyze image
            image = Image.open(screenshot_path)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            # Basic analysis
            analysis = {
                "image_size": image.size,
                "extracted_text": text.strip(),
                "text_length": len(text.strip()),
                "possible_captcha_text": bool(text.strip() and len(text.strip()) > 3),
                "screenshot_path": screenshot_path
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing CAPTCHA image: {e}")
            return {"error": str(e)}

class BrowserAutomation:
    """Main browser automation class with anti-detection features"""
    
    def __init__(self, config: Optional[BrowserConfig] = None):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium")
            
        self.config = config or BrowserConfig()
        self.driver = None
        self.captcha_detector = CaptchaDetector(self.config)
        self.request_count = 0
        self.last_request_time = 0
        
        # Session tracking
        self.session_stats = {
            "requests_made": 0,
            "captchas_detected": 0,
            "rate_limits_hit": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "start_time": datetime.now().isoformat()
        }
        
    def _setup_driver(self) -> webdriver.Chrome:
        """Setup Chrome driver with anti-detection options"""
        options = Options()
        
        # Headless mode
        if self.config.headless:
            options.add_argument("--headless=new")
        
        # Window size
        options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        
        # Anti-detection arguments
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-images")  # Faster loading
        options.add_argument("--disable-javascript")  # Disable for basic scraping
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        
        # Avoid detection
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agent = random.choice(self.config.user_agents)
        options.add_argument(f"--user-agent={user_agent}")
        logger.info(f"Using User-Agent: {user_agent[:50]}...")
        
        # Language and timezone
        options.add_argument("--lang=en-US")
        options.add_experimental_option('prefs', {
            'intl.accept_languages': 'en-US,en;q=0.9',
            'profile.default_content_setting_values.notifications': 2,
            'profile.managed_default_content_settings.images': 2  # Block images
        })
        
        try:
            # Try to create driver
            driver = webdriver.Chrome(options=options)
            
            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set timeouts
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            
            logger.info("Chrome driver initialized successfully")
            return driver
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome driver: {e}")
            raise
    
    def start_session(self):
        """Start browser session"""
        if self.driver is None:
            self.driver = self._setup_driver()
            logger.info("Browser session started")
    
    def end_session(self):
        """End browser session and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                logger.info("Browser session ended successfully")
            except Exception as e:
                logger.error(f"Error ending browser session: {e}")
        
        # Save session statistics
        self._save_session_stats()
    
    def _apply_request_delay(self):
        """Apply randomized delay between requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        min_delay, max_delay = self.config.request_delay_range
        required_delay = random.uniform(min_delay, max_delay)
        
        if elapsed < required_delay:
            sleep_time = required_delay - elapsed
            logger.info(f"Applying request delay: {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
        self.session_stats["requests_made"] += 1
    
    def navigate_to_url(self, url: str, check_captcha: bool = True) -> Tuple[bool, str]:
        """
        Navigate to URL with CAPTCHA detection
        
        Returns:
            Tuple of (success, message)
        """
        if not self.driver:
            self.start_session()
        
        try:
            self._apply_request_delay()
            
            logger.info(f"Navigating to: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Check for CAPTCHA if enabled
            if check_captcha and self.config.captcha_detection:
                has_captcha, captcha_type, screenshot_path = self.captcha_detector.detect_captcha(self.driver)
                
                if has_captcha:
                    self.session_stats["captchas_detected"] += 1
                    
                    # Store CAPTCHA information
                    captcha_info = {
                        "timestamp": datetime.now().isoformat(),
                        "url": url,
                        "captcha_type": captcha_type,
                        "screenshot_path": screenshot_path
                    }
                    
                    self._store_captcha_info(captcha_info)
                    
                    logger.warning(f"CAPTCHA detected on {url}: {captcha_type}")
                    return False, f"CAPTCHA detected: {captcha_type}"
            
            logger.info(f"Successfully navigated to: {url}")
            return True, "Success"
            
        except TimeoutException:
            logger.error(f"Timeout loading: {url}")
            return False, "Page load timeout"
        except WebDriverException as e:
            logger.error(f"WebDriver error: {e}")
            return False, f"WebDriver error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False, f"Unexpected error: {str(e)}"
    
    def search_google_scholar(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search Google Scholar with browser automation
        
        Args:
            query: Search query
            max_results: Maximum number of results to retrieve
            
        Returns:
            List of paper dictionaries
        """
        results = []
        
        try:
            # Navigate to Google Scholar
            scholar_url = "https://scholar.google.com"
            success, message = self.navigate_to_url(scholar_url)
            
            if not success:
                self.session_stats["failed_searches"] += 1
                return results
            
            # Find search box and enter query
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "q"))
                )
                search_box.clear()
                search_box.send_keys(query)
                search_box.send_keys(Keys.RETURN)
                
                logger.info(f"Submitted search query: {query}")
                
            except TimeoutException:
                logger.error("Could not find search box")
                self.session_stats["failed_searches"] += 1
                return results
            
            # Wait for results to load
            time.sleep(3)
            
            # Check for CAPTCHA after search
            has_captcha, captcha_type, screenshot_path = self.captcha_detector.detect_captcha(self.driver)
            if has_captcha:
                logger.warning(f"CAPTCHA detected after search: {captcha_type}")
                self.session_stats["captchas_detected"] += 1
                self.session_stats["failed_searches"] += 1
                return results
            
            # Extract search results
            results = self._extract_scholar_results(max_results)
            
            if results:
                self.session_stats["successful_searches"] += 1
                logger.info(f"Successfully extracted {len(results)} results")
            else:
                self.session_stats["failed_searches"] += 1
                logger.warning("No results extracted")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Google Scholar: {e}")
            self.session_stats["failed_searches"] += 1
            return results
    
    def _extract_scholar_results(self, max_results: int) -> List[Dict[str, Any]]:
        """Extract results from Google Scholar search results page"""
        results = []
        
        try:
            # Find result containers
            result_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-lid]")
            
            for i, element in enumerate(result_elements[:max_results]):
                try:
                    result = {}
                    
                    # Extract title
                    try:
                        title_elem = element.find_element(By.CSS_SELECTOR, "h3 a")
                        result["title"] = title_elem.text.strip()
                        result["url"] = title_elem.get_attribute("href")
                    except NoSuchElementException:
                        continue
                    
                    # Extract authors and publication info
                    try:
                        meta_elem = element.find_element(By.CSS_SELECTOR, ".gs_a")
                        meta_text = meta_elem.text.strip()
                        result["meta"] = meta_text
                        
                        # Try to parse authors and year
                        if " - " in meta_text:
                            parts = meta_text.split(" - ")
                            result["authors"] = [parts[0].strip()]
                            if len(parts) > 1:
                                # Look for year in publication info
                                pub_info = parts[1]
                                import re
                                year_match = re.search(r'\b(19|20)\d{2}\b', pub_info)
                                if year_match:
                                    result["year"] = year_match.group()
                                result["journal"] = pub_info
                    except NoSuchElementException:
                        pass
                    
                    # Extract abstract/snippet
                    try:
                        abstract_elem = element.find_element(By.CSS_SELECTOR, ".gs_rs")
                        result["abstract"] = abstract_elem.text.strip()
                    except NoSuchElementException:
                        result["abstract"] = ""
                    
                    # Extract citation count
                    try:
                        citation_elem = element.find_element(By.CSS_SELECTOR, ".gs_fl a")
                        citation_text = citation_elem.text
                        if "Cited by" in citation_text:
                            import re
                            citation_match = re.search(r'Cited by (\d+)', citation_text)
                            if citation_match:
                                result["citations"] = int(citation_match.group(1))
                    except (NoSuchElementException, ValueError):
                        result["citations"] = 0
                    
                    # Add metadata
                    result["database"] = "Google Scholar (Browser)"
                    result["extraction_timestamp"] = datetime.now().isoformat()
                    
                    # Estimate quality based on citations
                    citations = result.get("citations", 0)
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
                    logger.warning(f"Error extracting result {i}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error extracting Scholar results: {e}")
            return results
    
    def _store_captcha_info(self, captcha_info: Dict[str, Any]):
        """Store CAPTCHA detection information"""
        try:
            captcha_log_file = get_project_root() / "output" / "captcha_detections.json"
            
            # Load existing data
            if captcha_log_file.exists():
                with open(captcha_log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"detections": []}
            
            # Add new detection
            data["detections"].append(captcha_info)
            
            # Save updated data
            with open(captcha_log_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"CAPTCHA info stored: {captcha_log_file}")
            
        except Exception as e:
            logger.error(f"Error storing CAPTCHA info: {e}")
    
    def _save_session_stats(self):
        """Save session statistics"""
        try:
            self.session_stats["end_time"] = datetime.now().isoformat()
            self.session_stats["duration_minutes"] = (
                datetime.now() - datetime.fromisoformat(self.session_stats["start_time"])
            ).total_seconds() / 60
            
            stats_file = get_project_root() / "output" / "browser_session_stats.json"
            
            # Load existing stats
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    all_stats = json.load(f)
            else:
                all_stats = {"sessions": []}
            
            # Add current session
            all_stats["sessions"].append(self.session_stats)
            
            # Save updated stats
            with open(stats_file, 'w') as f:
                json.dump(all_stats, f, indent=2, default=str)
            
            logger.info(f"Session stats saved: {stats_file}")
            
        except Exception as e:
            logger.error(f"Error saving session stats: {e}")

class ScholarlyBrowserIntegration:
    """Integration layer to replace scholarly with browser automation"""
    
    def __init__(self):
        self.browser = BrowserAutomation()
        
    def search_pubs(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search publications using browser automation
        Compatible with scholarly API
        """
        try:
            self.browser.start_session()
            results = self.browser.search_google_scholar(query, max_results)
            return results
        finally:
            self.browser.end_session()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.browser:
            self.browser.end_session()

def main():
    """Test the browser automation system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test browser automation for literature search")
    parser.add_argument("--query", default="AI agents in finance", help="Search query")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum results")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    
    # Configure browser
    config = BrowserConfig(
        headless=args.headless,
        request_delay_range=(3, 8),  # Shorter delays for testing
        captcha_detection=True
    )
    
    # Test browser automation
    browser = BrowserAutomation(config)
    
    try:
        browser.start_session()
        
        print(f"Searching for: {args.query}")
        results = browser.search_google_scholar(args.query, args.max_results)
        
        print(f"\nFound {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result.get('title', 'No title')}")
            print(f"   Authors: {', '.join(result.get('authors', []))}")
            print(f"   Year: {result.get('year', 'N/A')}")
            print(f"   Citations: {result.get('citations', 0)}")
            print(f"   Quality: {result.get('quartile', 'N/A')}")
        
        # Display session stats
        print(f"\nSession Statistics:")
        print(f"Requests made: {browser.session_stats['requests_made']}")
        print(f"CAPTCHAs detected: {browser.session_stats['captchas_detected']}")
        print(f"Successful searches: {browser.session_stats['successful_searches']}")
        print(f"Failed searches: {browser.session_stats['failed_searches']}")
        
    finally:
        browser.end_session()

if __name__ == "__main__":
    main()