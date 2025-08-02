#!/usr/bin/env python3
"""
Docker Browser Test Suite
=========================

Comprehensive testing for browser automation in Docker containers.
Tests Chrome/Chromium installation, Selenium integration, and research capabilities.
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Add scripts directory to path for imports
sys.path.append('/app/scripts')

try:
    from browser_config import DockerBrowserConfig, BrowserContextManager, test_browser_setup
    from research_browser import ResearchBrowser, test_research_browser
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("Running basic tests without advanced features...")


class DockerBrowserTestSuite:
    """Comprehensive test suite for Docker browser setup."""
    
    def __init__(self):
        self.results = {}
        self.errors = []
        
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all browser tests and return results."""
        print("🧪 Starting Docker Browser Test Suite")
        print("=" * 50)
        
        tests = [
            ("Environment Check", self.test_environment),
            ("System Dependencies", self.test_system_dependencies),
            ("Python Dependencies", self.test_python_dependencies),
            ("Virtual Display", self.test_virtual_display),
            ("Chrome Installation", self.test_chrome_installation),
            ("ChromeDriver", self.test_chromedriver),
            ("Selenium Basic", self.test_selenium_basic),
            ("Browser Configuration", self.test_browser_config),
            ("Cookie Management", self.test_cookie_management),
            ("Research Browser", self.test_research_functionality)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🔧 Running: {test_name}")
            try:
                result = test_func()
                self.results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"   {status}")
            except Exception as e:
                self.results[test_name] = False
                self.errors.append(f"{test_name}: {str(e)}")
                print(f"   ❌ ERROR: {e}")
        
        self.print_summary()
        return self.results
    
    def test_environment(self) -> bool:
        """Test Docker environment variables."""
        required_vars = {
            'DISPLAY': ':99',
            'CHROME_BIN': '/usr/bin/chromium'
        }
        
        for var, expected in required_vars.items():
            actual = os.getenv(var)
            if not actual:
                print(f"   ⚠️  Missing environment variable: {var}")
                return False
            if expected and actual != expected:
                print(f"   ⚠️  {var}={actual}, expected {expected}")
        
        return True
    
    def test_system_dependencies(self) -> bool:
        """Test system-level dependencies."""
        dependencies = [
            ('/usr/bin/chromium', 'Chromium browser'),
            ('/usr/bin/chromedriver', 'ChromeDriver'),
            ('/usr/bin/Xvfb', 'Virtual display server')
        ]
        
        missing = []
        for path, name in dependencies:
            if not os.path.exists(path):
                missing.append(f"{name} at {path}")
                print(f"   ❌ Missing: {name} at {path}")
        
        if missing:
            return False
        
        # Test chromium version
        try:
            result = subprocess.run(
                ['/usr/bin/chromium', '--version'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"   📦 {result.stdout.strip()}")
            else:
                print(f"   ⚠️  Chromium version check failed")
                return False
        except Exception as e:
            print(f"   ⚠️  Chromium version check error: {e}")
            return False
        
        return True
    
    def test_python_dependencies(self) -> bool:
        """Test Python package dependencies."""
        required_packages = [
            'selenium',
            'browser_cookie3',
            'requests'
        ]
        
        missing = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing.append(package)
                print(f"   ❌ Missing: {package}")
        
        return len(missing) == 0
    
    def test_virtual_display(self) -> bool:
        """Test virtual display functionality."""
        try:
            # Check if DISPLAY is set
            display = os.getenv('DISPLAY')
            if not display:
                print("   ❌ DISPLAY environment variable not set")
                return False
            
            # Try to start Xvfb if not running
            result = subprocess.run(
                ['pgrep', 'Xvfb'],
                capture_output=True, text=True
            )
            
            if result.returncode != 0:
                print("   🔄 Starting Xvfb...")
                subprocess.Popen(
                    ['Xvfb', ':99', '-screen', '0', '1024x768x24'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                time.sleep(3)
            
            # Verify Xvfb is running
            result = subprocess.run(
                ['pgrep', 'Xvfb'],
                capture_output=True, text=True
            )
            
            if result.returncode == 0:
                print(f"   ✅ Xvfb running (PID: {result.stdout.strip()})")
                return True
            else:
                print("   ❌ Xvfb not running")
                return False
                
        except Exception as e:
            print(f"   ❌ Virtual display test failed: {e}")
            return False
    
    def test_chrome_installation(self) -> bool:
        """Test Chrome/Chromium installation."""
        try:
            chrome_bin = os.getenv('CHROME_BIN', '/usr/bin/chromium')
            
            # Test chrome executable with --no-sandbox for root user
            result = subprocess.run(
                [chrome_bin, '--headless', '--no-sandbox', '--disable-gpu', '--dump-dom', 'data:text/html,<html><body>Test</body></html>'],
                capture_output=True, text=True, timeout=15
            )
            
            if result.returncode == 0 and 'Test' in result.stdout:
                print("   ✅ Chrome can render HTML")
                return True
            else:
                print(f"   ❌ Chrome test failed (exit code: {result.returncode})")
                if result.stderr:
                    print(f"   Error: {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ❌ Chrome test timed out")
            return False
        except Exception as e:
            print(f"   ❌ Chrome test error: {e}")
            return False
    
    def test_chromedriver(self) -> bool:
        """Test ChromeDriver functionality."""
        try:
            result = subprocess.run(
                ['/usr/bin/chromedriver', '--version'],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                print(f"   📦 {result.stdout.strip()}")
                return True
            else:
                print(f"   ❌ ChromeDriver version check failed")
                return False
                
        except Exception as e:
            print(f"   ❌ ChromeDriver test error: {e}")
            return False
    
    def test_selenium_basic(self) -> bool:
        """Test basic Selenium functionality."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            
            chrome_bin = os.getenv('CHROME_BIN', '/usr/bin/chromium')
            options.binary_location = chrome_bin
            
            service = Service('/usr/bin/chromedriver')
            
            driver = webdriver.Chrome(service=service, options=options)
            
            # Test navigation
            driver.get('data:text/html,<html><body><h1>Selenium Test</h1></body></html>')
            title = driver.title
            page_source = driver.page_source
            
            driver.quit()
            
            if 'Selenium Test' in page_source:
                print("   ✅ Selenium can control browser and extract content")
                return True
            else:
                print("   ❌ Selenium content extraction failed")
                return False
                
        except Exception as e:
            print(f"   ❌ Selenium test error: {e}")
            return False
    
    def test_browser_config(self) -> bool:
        """Test browser configuration module."""
        try:
            # Test basic import and initialization
            config = DockerBrowserConfig()
            
            # Test directory creation
            if not config.user_data_dir.exists():
                print("   ❌ User data directory not created")
                return False
            
            if not config.cookies_dir.exists():
                print("   ❌ Cookies directory not created")
                return False
            
            # Test Chrome options
            options = config.chrome_options
            arguments = [arg for arg in options.arguments]
            
            required_args = ['--no-sandbox', '--disable-dev-shm-usage', '--headless=new']
            missing_args = [arg for arg in required_args if arg not in arguments]
            
            if missing_args:
                print(f"   ❌ Missing Chrome arguments: {missing_args}")
                return False
            
            print("   ✅ Browser configuration valid")
            return True
            
        except Exception as e:
            print(f"   ❌ Browser config test error: {e}")
            return False
    
    def test_cookie_management(self) -> bool:
        """Test cookie save/load functionality."""
        try:
            config = DockerBrowserConfig()
            
            with BrowserContextManager(config) as driver:
                # Navigate to a real domain to avoid cookie domain issues
                driver.get('https://httpbin.org/html')
                
                # Add a test cookie with proper domain
                driver.add_cookie({
                    'name': 'test_cookie',
                    'value': 'test_value',
                    'domain': '.httpbin.org'
                })
                
                # Get cookies
                cookies = driver.get_cookies()
                
                if not cookies:
                    print("   ❌ No cookies found")
                    return False
                
                # Test cookie file operations
                test_domain = 'test.example.com'
                config.save_cookies(driver, test_domain)
                
                cookie_file = config.cookies_dir / f"{test_domain}_cookies.json"
                if not cookie_file.exists():
                    print("   ❌ Cookie file not created")
                    return False
                
                print("   ✅ Cookie management working")
                return True
                
        except Exception as e:
            print(f"   ❌ Cookie management test error: {e}")
            return False
    
    def test_research_functionality(self) -> bool:
        """Test research browser functionality."""
        try:
            # Test research browser initialization
            browser = ResearchBrowser()
            
            # Test basic configuration
            if not browser.config:
                print("   ❌ Research browser config not initialized")
                return False
            
            if not browser.output_dir.exists():
                print("   ❌ Research output directory not created")
                return False
            
            # Test domain configuration
            if 'arxiv' not in browser.research_domains:
                print("   ❌ ArXiv domain configuration missing")
                return False
            
            print("   ✅ Research browser configuration valid")
            
            # Optional: Test actual search (commented out to avoid external requests)
            # results = browser.search_papers("test query", domains=['arxiv'], max_results=1)
            # return len(results.get('arxiv', [])) >= 0
            
            return True
            
        except Exception as e:
            print(f"   ❌ Research functionality test error: {e}")
            return False
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.results.values() if result)
        total = len(self.results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed} ✅")
        print(f"Failed: {total - passed} ❌")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        print("\n🔧 DETAILED RESULTS:")
        for test_name, result in self.results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        # Docker-specific recommendations
        if passed < total:
            print("\n🔧 TROUBLESHOOTING TIPS:")
            print("  - Ensure Docker container has sufficient memory (2GB+)")
            print("  - Check that --shm-size=2g is set in docker run")
            print("  - Verify /dev/shm is mounted correctly")
            print("  - Ensure DISPLAY variable is set to :99")
            print("  - Try rebuilding Docker image with --no-cache")
    
    def generate_report(self) -> str:
        """Generate a detailed test report."""
        report = {
            'timestamp': time.time(),
            'environment': {
                'display': os.getenv('DISPLAY'),
                'chrome_bin': os.getenv('CHROME_BIN'),
                'container': os.path.exists('/.dockerenv')
            },
            'results': self.results,
            'errors': self.errors,
            'summary': {
                'total_tests': len(self.results),
                'passed': sum(1 for r in self.results.values() if r),
                'failed': sum(1 for r in self.results.values() if not r)
            }
        }
        
        return json.dumps(report, indent=2)


def main():
    """Main test runner."""
    print("🐳 Docker Browser Test Suite")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"🖥️  Display: {os.getenv('DISPLAY', 'Not set')}")
    print(f"🌐 Chrome Binary: {os.getenv('CHROME_BIN', 'Not set')}")
    
    suite = DockerBrowserTestSuite()
    results = suite.run_all_tests()
    
    # Save test report
    report_file = Path('/app/output/browser_test_report.json')
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write(suite.generate_report())
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    success_rate = sum(1 for r in results.values() if r) / len(results)
    exit_code = 0 if success_rate >= 0.8 else 1
    
    print(f"\n🎯 Exit Code: {exit_code} ({'Success' if exit_code == 0 else 'Failure'})")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()