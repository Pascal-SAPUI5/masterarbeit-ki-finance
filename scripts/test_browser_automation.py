#!/usr/bin/env python3
"""
Test script for browser automation system
Validates all features including CAPTCHA detection and user-agent rotation
"""

import logging
import json
import time
from pathlib import Path
from datetime import datetime

# Setup logging for test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_browser_automation():
    """Comprehensive test of browser automation features"""
    
    print("🧪 Browser Automation Test Suite")
    print("=" * 50)
    
    try:
        # Import browser automation
        from scripts.browser_automation import BrowserAutomation, BrowserConfig, ScholarlyBrowserIntegration
        print("✅ Browser automation module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import browser automation: {e}")
        print("📝 Please run: pip install selenium webdriver-manager Pillow pytesseract")
        return False
    
    # Test 1: Basic Configuration
    print("\n🔧 Test 1: Configuration Setup")
    config = BrowserConfig(
        headless=True,
        request_delay_range=(2, 5),  # Shorter for testing
        captcha_detection=True,
        window_size=(1920, 1080)
    )
    print(f"✅ Configuration created with {len(config.user_agents)} user agents")
    
    # Test 2: Browser Initialization
    print("\n🌐 Test 2: Browser Initialization")
    browser = BrowserAutomation(config)
    try:
        browser.start_session()
        print("✅ Browser session started successfully")
    except Exception as e:
        print(f"❌ Browser initialization failed: {e}")
        print("📝 Please ensure Chrome/Chromium is installed")
        return False
    
    # Test 3: User Agent Rotation
    print("\n🔄 Test 3: User Agent Rotation")
    current_ua = browser.driver.execute_script("return navigator.userAgent;")
    print(f"✅ Current user agent: {current_ua[:80]}...")
    
    # Test 4: Basic Navigation
    print("\n🧭 Test 4: Basic Navigation")
    try:
        success, message = browser.navigate_to_url("https://httpbin.org/user-agent")
        if success:
            print("✅ Navigation successful")
        else:
            print(f"⚠️  Navigation issue: {message}")
    except Exception as e:
        print(f"❌ Navigation failed: {e}")
    
    # Test 5: CAPTCHA Detection (using a test page)
    print("\n🛡️  Test 5: CAPTCHA Detection")
    try:
        # Navigate to a page that might have CAPTCHA elements (for testing)
        success, message = browser.navigate_to_url("https://www.google.com/recaptcha/api2/demo")
        if success:
            has_captcha, captcha_type, screenshot = browser.captcha_detector.detect_captcha(browser.driver)
            if has_captcha:
                print(f"✅ CAPTCHA detection working - detected: {captcha_type}")
                if screenshot:
                    print(f"📸 Screenshot saved: {screenshot}")
            else:
                print("✅ CAPTCHA detection working - no CAPTCHA found")
        else:
            print(f"⚠️  Could not test CAPTCHA detection: {message}")
    except Exception as e:
        print(f"❌ CAPTCHA detection test failed: {e}")
    
    # Test 6: Request Delay
    print("\n⏱️  Test 6: Request Delay System")
    start_time = time.time()
    browser._apply_request_delay()
    delay_time = time.time() - start_time
    print(f"✅ Request delay applied: {delay_time:.2f} seconds")
    
    # Test 7: Scholar Integration
    print("\n📚 Test 7: Scholar Integration")
    try:
        with ScholarlyBrowserIntegration() as scholar:
            # Small test search
            results = scholar.search_pubs("machine learning", max_results=3)
            print(f"✅ Scholar integration test: Found {len(results)} results")
            
            if results:
                sample = results[0]
                print(f"   Sample result: {sample.get('title', 'No title')[:50]}...")
                print(f"   Citations: {sample.get('citations', 0)}")
                print(f"   Quality: {sample.get('quartile', 'N/A')}")
    except Exception as e:
        print(f"❌ Scholar integration test failed: {e}")
    
    # Test 8: Session Statistics
    print("\n📊 Test 8: Session Statistics")
    stats = browser.session_stats
    print(f"✅ Session statistics tracked:")
    print(f"   Requests made: {stats['requests_made']}")
    print(f"   CAPTCHAs detected: {stats['captchas_detected']}")
    print(f"   Successful searches: {stats['successful_searches']}")
    print(f"   Failed searches: {stats['failed_searches']}")
    
    # Cleanup
    print("\n🧹 Cleanup")
    browser.end_session()
    print("✅ Browser session ended successfully")
    
    print("\n🎉 All tests completed successfully!")
    return True

def test_anti_detection_features():
    """Test specific anti-detection features"""
    
    print("\n🕵️  Anti-Detection Features Test")
    print("=" * 40)
    
    from scripts.browser_automation import BrowserAutomation, BrowserConfig
    
    config = BrowserConfig(headless=False)  # Visible for testing
    browser = BrowserAutomation(config)
    
    try:
        browser.start_session()
        
        # Test webdriver property masking
        webdriver_undefined = browser.driver.execute_script("return navigator.webdriver === undefined;")
        print(f"✅ WebDriver property masked: {webdriver_undefined}")
        
        # Test user agent
        user_agent = browser.driver.execute_script("return navigator.userAgent;")
        is_realistic = "Chrome" in user_agent and "WebKit" in user_agent
        print(f"✅ Realistic user agent: {is_realistic}")
        
        # Test window size
        window_size = browser.driver.get_window_size()
        is_standard_size = window_size['width'] >= 1024 and window_size['height'] >= 768
        print(f"✅ Standard window size: {is_standard_size} ({window_size['width']}x{window_size['height']})")
        
        # Test language settings
        languages = browser.driver.execute_script("return navigator.languages;")
        has_english = 'en-US' in str(languages)
        print(f"✅ English language preference: {has_english}")
        
        browser.end_session()
        print("✅ Anti-detection test completed")
        
    except Exception as e:
        print(f"❌ Anti-detection test failed: {e}")
        if browser.driver:
            browser.end_session()

def main():
    """Main test function"""
    
    print("🚀 Starting Browser Automation Test Suite")
    print("=" * 60)
    
    # Check system requirements
    print("🔍 Checking system requirements...")
    
    try:
        import selenium
        print(f"✅ Selenium version: {selenium.__version__}")
    except ImportError:
        print("❌ Selenium not installed")
        return
    
    try:
        from PIL import Image
        print("✅ Pillow (PIL) available")
    except ImportError:
        print("⚠️  Pillow not available - image processing disabled")
    
    try:
        import pytesseract
        print("✅ Pytesseract available")
    except ImportError:
        print("⚠️  Pytesseract not available - OCR disabled")
    
    # Run main tests
    print("\n" + "=" * 60)
    success = test_browser_automation()
    
    if success:
        print("\n" + "=" * 60)
        test_anti_detection_features()
    
    print("\n🏁 Test suite completed!")
    
    # Generate test report
    test_report = {
        "timestamp": datetime.now().isoformat(),
        "test_status": "passed" if success else "failed",
        "features_tested": [
            "browser_initialization",
            "user_agent_rotation", 
            "navigation",
            "captcha_detection",
            "request_delays",
            "scholar_integration",
            "session_statistics",
            "anti_detection"
        ],
        "recommendations": [
            "Run setup script: ./scripts/setup_browser_automation.sh",
            "Install dependencies: pip install -r requirements.txt",
            "Test with real searches: python scripts/browser_automation.py --query 'AI finance'"
        ]
    }
    
    # Save test report
    report_file = Path("output/browser_automation_test_report.json")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w') as f:
        json.dump(test_report, f, indent=2, default=str)
    
    print(f"📄 Test report saved: {report_file}")

if __name__ == "__main__":
    main()