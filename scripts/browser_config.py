#!/usr/bin/env python3
"""
Browser Configuration for Docker Container
==========================================

This module provides utilities for configuring and managing Chrome/Chromium
browser instances within Docker containers, with support for:
- Headless operation with Xvfb
- Cookie persistence
- Container-optimized browser options
- Selenium WebDriver configuration
"""

import os
import time
import json
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import browser_cookie3


class DockerBrowserConfig:
    """Browser configuration optimized for Docker containers."""
    
    def __init__(self, 
                 user_data_dir: str = "/app/browser_data",
                 cookies_dir: str = "/app/cookies",
                 headless: bool = True):
        """
        Initialize browser configuration.
        
        Args:
            user_data_dir: Directory for browser user data
            cookies_dir: Directory for cookie storage
            headless: Whether to run in headless mode
        """
        self.user_data_dir = Path(user_data_dir)
        self.cookies_dir = Path(cookies_dir)
        self.headless = headless
        
        # Create directories
        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        
        # Browser configuration
        self.chrome_options = self._configure_chrome_options()
        
    def _configure_chrome_options(self) -> Options:
        """Configure Chrome options for container environment."""
        options = Options()
        
        # Container-specific options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        
        # Headless configuration
        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")
        
        # User data directory
        options.add_argument(f"--user-data-dir={self.user_data_dir}")
        
        # Performance optimizations
        options.add_argument("--memory-pressure-off")
        options.add_argument("--max_old_space_size=4096")
        options.add_argument("--disable-background-networking")
        
        # Security and privacy
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-sync")
        
        # Set binary location
        chrome_bin = os.getenv("CHROME_BIN", "/usr/bin/chromium-browser")
        if os.path.exists(chrome_bin):
            options.binary_location = chrome_bin
            
        return options
    
    def create_driver(self, 
                     implicit_wait: int = 10,
                     page_load_timeout: int = 30) -> webdriver.Chrome:
        """
        Create a configured Chrome WebDriver instance.
        
        Args:
            implicit_wait: Implicit wait timeout in seconds
            page_load_timeout: Page load timeout in seconds
            
        Returns:
            Configured Chrome WebDriver instance
        """
        try:
            # Use system chromedriver
            service = Service("/usr/bin/chromedriver")
            
            driver = webdriver.Chrome(
                service=service,
                options=self.chrome_options
            )
            
            # Configure timeouts
            driver.implicitly_wait(implicit_wait)
            driver.set_page_load_timeout(page_load_timeout)
            
            return driver
            
        except Exception as e:
            print(f"Failed to create Chrome driver: {e}")
            raise
    
    def save_cookies(self, driver: webdriver.Chrome, domain: str) -> None:
        """
        Save cookies for a specific domain.
        
        Args:
            driver: WebDriver instance
            domain: Domain to save cookies for
        """
        try:
            cookies = driver.get_cookies()
            cookie_file = self.cookies_dir / f"{domain}_cookies.json"
            
            with open(cookie_file, 'w') as f:
                json.dump(cookies, f, indent=2)
                
            print(f"Saved {len(cookies)} cookies for {domain}")
            
        except Exception as e:
            print(f"Failed to save cookies for {domain}: {e}")
    
    def load_cookies(self, driver: webdriver.Chrome, domain: str) -> bool:
        """
        Load cookies for a specific domain.
        
        Args:
            driver: WebDriver instance
            domain: Domain to load cookies for
            
        Returns:
            True if cookies were loaded successfully
        """
        try:
            cookie_file = self.cookies_dir / f"{domain}_cookies.json"
            
            if not cookie_file.exists():
                print(f"No cookies found for {domain}")
                return False
                
            with open(cookie_file, 'r') as f:
                cookies = json.load(f)
            
            # Navigate to domain first
            driver.get(f"https://{domain}")
            
            # Add each cookie
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Failed to add cookie: {e}")
                    continue
            
            print(f"Loaded {len(cookies)} cookies for {domain}")
            return True
            
        except Exception as e:
            print(f"Failed to load cookies for {domain}: {e}")
            return False
    
    def extract_system_cookies(self, domain: str) -> List[Dict]:
        """
        Extract cookies from system browsers.
        
        Args:
            domain: Domain to extract cookies for
            
        Returns:
            List of cookie dictionaries
        """
        cookies = []
        
        try:
            # Try Chrome cookies
            chrome_cookies = browser_cookie3.chrome(domain_name=domain)
            for cookie in chrome_cookies:
                cookies.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'secure': cookie.secure,
                    'httpOnly': cookie.rest.get('HttpOnly', False)
                })
        except Exception as e:
            print(f"Failed to extract Chrome cookies: {e}")
        
        try:
            # Try Firefox cookies
            firefox_cookies = browser_cookie3.firefox(domain_name=domain)
            for cookie in firefox_cookies:
                # Avoid duplicates
                if not any(c['name'] == cookie.name for c in cookies):
                    cookies.append({
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                        'secure': cookie.secure,
                        'httpOnly': cookie.rest.get('HttpOnly', False)
                    })
        except Exception as e:
            print(f"Failed to extract Firefox cookies: {e}")
        
        return cookies
    
    def start_virtual_display(self) -> None:
        """Start virtual display if not already running."""
        if os.getenv("DISPLAY") != ":99":
            os.system("Xvfb :99 -screen 0 1024x768x24 &")
            os.environ["DISPLAY"] = ":99"
            time.sleep(2)  # Wait for display to start
    
    def check_browser_health(self) -> bool:
        """
        Check if browser can be created and is working.
        
        Returns:
            True if browser is healthy
        """
        try:
            driver = self.create_driver()
            driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
            title = driver.title
            driver.quit()
            return True
        except Exception as e:
            print(f"Browser health check failed: {e}")
            return False


class BrowserContextManager:
    """Context manager for browser instances."""
    
    def __init__(self, config: DockerBrowserConfig):
        self.config = config
        self.driver = None
    
    def __enter__(self) -> webdriver.Chrome:
        """Create and return browser driver."""
        self.driver = self.config.create_driver()
        return self.driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up browser driver."""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"Error closing browser: {e}")


def create_browser_config(**kwargs) -> DockerBrowserConfig:
    """
    Factory function to create browser configuration.
    
    Returns:
        Configured DockerBrowserConfig instance
    """
    return DockerBrowserConfig(**kwargs)


def test_browser_setup():
    """Test browser setup and configuration."""
    print("🔧 Testing browser setup...")
    
    config = create_browser_config()
    
    # Start virtual display
    config.start_virtual_display()
    
    # Health check
    if config.check_browser_health():
        print("✅ Browser setup successful!")
    else:
        print("❌ Browser setup failed!")
        return False
    
    # Test with context manager
    try:
        with BrowserContextManager(config) as driver:
            driver.get("https://example.com")
            print(f"📄 Page title: {driver.title}")
            
            # Save cookies
            config.save_cookies(driver, "example.com")
            
        print("✅ Browser context test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Browser context test failed: {e}")
        return False


if __name__ == "__main__":
    test_browser_setup()