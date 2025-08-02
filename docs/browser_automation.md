# Browser Automation for Academic Literature Search

## Overview

This module provides robust browser automation for academic literature searches, specifically designed to handle the challenges of automated Google Scholar access with anti-detection measures and CAPTCHA handling.

## Features

### 🚀 Core Capabilities
- **Headless Chrome Automation**: Selenium-based browser automation with Chrome/Chromium
- **User-Agent Rotation**: Randomized, realistic user agents for each session
- **Request Delay Randomization**: Configurable delays (5-15 seconds) between requests
- **CAPTCHA Detection**: Advanced detection with screenshot capture and OCR analysis
- **Anti-Detection Measures**: Browser fingerprint masking and human-like behavior
- **Session Management**: Comprehensive tracking and statistics

### 🛡️ Anti-Detection Features
- Webdriver property masking
- Browser fingerprint randomization
- Realistic user agents (Chrome, Firefox, Edge, Safari)
- Standard window sizes and language preferences
- Disabled automation indicators
- Human-like request patterns

### 🔍 CAPTCHA Handling
- **Detection Methods**:
  - iframe-based CAPTCHAs (reCAPTCHA, hCAPTCHA)
  - Text-based indicators
  - HTML element analysis
  - Rate limiting detection
- **Response Actions**:
  - Screenshot capture for analysis
  - OCR text extraction
  - Session statistics tracking
  - Graceful fallback handling

## Installation

### 1. System Dependencies

Run the automated setup script:
```bash
./scripts/setup_browser_automation.sh
```

Or install manually:

#### Ubuntu/Debian:
```bash
# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install google-chrome-stable

# Install dependencies
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

#### macOS:
```bash
# Install Chrome
brew install --cask google-chrome

# Install dependencies  
brew install tesseract
```

### 2. Python Dependencies

```bash
pip install selenium webdriver-manager Pillow pytesseract
```

## Usage

### Basic Usage

```python
from scripts.browser_automation import BrowserAutomation, BrowserConfig

# Configure browser
config = BrowserConfig(
    headless=True,
    request_delay_range=(5, 15),
    captcha_detection=True
)

# Create browser instance
browser = BrowserAutomation(config)

try:
    # Start session
    browser.start_session()
    
    # Search Google Scholar
    results = browser.search_google_scholar("AI agents in finance", max_results=20)
    
    print(f"Found {len(results)} papers")
    for paper in results:
        print(f"- {paper['title']}")
        print(f"  Citations: {paper.get('citations', 0)}")
        print(f"  Quality: {paper.get('quartile', 'N/A')}")

finally:
    # Always clean up
    browser.end_session()
```

### Scholarly Integration

Replace the standard `scholarly` library with our browser automation:

```python
from scripts.browser_automation import ScholarlyBrowserIntegration

# Drop-in replacement for scholarly
with ScholarlyBrowserIntegration() as scholar:
    results = scholar.search_pubs("machine learning finance", max_results=50)
    
    for paper in results:
        print(f"Title: {paper['title']}")
        print(f"Authors: {', '.join(paper.get('authors', []))}")
        print(f"Year: {paper.get('year', 'N/A')}")
```

### Integration with Literature Search

The browser automation is automatically integrated with the main literature search system:

```python
from scripts.search_literature import LiteratureSearcher

searcher = LiteratureSearcher()

# Will use browser automation automatically for Google Scholar
results = searcher.search(
    query="AI agents financial services",
    databases=["Google Scholar", "Crossref"],
    years="2020-2025",
    quality="q1"
)
```

## Configuration

### BrowserConfig Options

```python
@dataclass
class BrowserConfig:
    headless: bool = True                    # Run in headless mode
    window_size: Tuple[int, int] = (1920, 1080)  # Browser window size
    page_load_timeout: int = 30             # Page load timeout (seconds)
    implicit_wait: int = 10                 # Implicit wait time (seconds)
    request_delay_range: Tuple[int, int] = (5, 15)  # Delay between requests
    max_retries: int = 3                    # Maximum retry attempts
    user_agents: List[str] = None           # Custom user agent list
    proxy_enabled: bool = False             # Enable proxy support
    proxy_list: List[str] = None           # List of proxy servers
    captcha_detection: bool = True          # Enable CAPTCHA detection
```

### User Agents

The system includes realistic user agents for:
- Chrome on Windows/macOS/Linux
- Firefox on Windows/macOS
- Edge on Windows
- Academic/Research specific agents

### Request Delays

Configurable randomized delays help avoid rate limiting:
- Default: 5-15 seconds between requests
- Customizable range for different use cases
- Intelligent timing based on previous requests

## CAPTCHA Detection

### Detection Capabilities

The system detects various CAPTCHA types:

1. **iframe-based**: reCAPTCHA, hCAPTCHA
2. **Element-based**: HTML elements with CAPTCHA classes/IDs
3. **Text-based**: Page content analysis for CAPTCHA indicators
4. **Rate limiting**: Detection of access restrictions

### Response Actions

When a CAPTCHA is detected:

1. **Screenshot Capture**: Automatic screenshot for analysis
2. **OCR Analysis**: Text extraction using Tesseract OCR
3. **Session Logging**: Record detection for statistics
4. **Graceful Handling**: Return appropriate error status

### CAPTCHA Analysis

```python
from scripts.browser_automation import CaptchaDetector

detector = CaptchaDetector(config)

# Detect CAPTCHA on current page
has_captcha, captcha_type, screenshot_path = detector.detect_captcha(driver)

if has_captcha:
    # Analyze the CAPTCHA image
    analysis = detector.analyze_captcha_image(screenshot_path)
    print(f"CAPTCHA detected: {captcha_type}")
    print(f"Screenshot: {screenshot_path}")
    print(f"OCR Text: {analysis.get('extracted_text', 'N/A')}")
```

## Session Management

### Statistics Tracking

The system tracks comprehensive session statistics:

```python
browser.session_stats = {
    "requests_made": 0,
    "captchas_detected": 0, 
    "rate_limits_hit": 0,
    "successful_searches": 0,
    "failed_searches": 0,
    "start_time": "2025-01-01T12:00:00",
    "end_time": "2025-01-01T12:30:00",
    "duration_minutes": 30.0
}
```

### Output Files

The system generates several output files:

- `output/captcha_screenshots/`: CAPTCHA screenshots
- `output/captcha_detections.json`: CAPTCHA detection log
- `output/browser_session_stats.json`: Session statistics
- `output/browser_automation_test_report.json`: Test results

## Testing

### Quick Test

```bash
python scripts/test_browser_automation.py
```

### Manual Testing

```bash
# Test with visible browser (for debugging)
python scripts/browser_automation.py --query "AI agents finance" --max-results 5

# Test headless mode
python scripts/browser_automation.py --query "machine learning" --headless --max-results 10
```

### Test Suite Features

The test suite validates:
- Browser initialization
- User agent rotation
- Navigation capabilities
- CAPTCHA detection
- Request delay system
- Scholar integration
- Session statistics
- Anti-detection features

## Performance Considerations

### Resource Usage
- **Memory**: ~100-200MB per browser session
- **CPU**: Moderate during page loading and parsing
- **Network**: Optimized with image blocking and minimal CSS

### Optimization Features
- Disabled images for faster loading
- Minimal JavaScript execution
- Efficient element selection
- Smart retry mechanisms

## Troubleshooting

### Common Issues

1. **Chrome/ChromeDriver Version Mismatch**
   ```bash
   # Update ChromeDriver
   pip install --upgrade webdriver-manager
   ```

2. **Permission Errors**
   ```bash
   sudo chmod +x /usr/local/bin/chromedriver
   ```

3. **Display Issues (Headless)**
   ```bash
   export DISPLAY=:99
   Xvfb :99 -screen 0 1920x1080x24 &
   ```

4. **Tesseract OCR Not Found**
   ```bash
   sudo apt-get install tesseract-ocr tesseract-ocr-eng
   ```

### Debug Mode

Enable debug mode for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

config = BrowserConfig(headless=False)  # Visible browser
browser = BrowserAutomation(config)
```

## Security Considerations

### Data Privacy
- No personal data storage
- Temporary file cleanup
- Session isolation

### Rate Limiting Compliance
- Respectful request patterns
- Configurable delays
- Automatic backoff on detection

### Legal Compliance
- Respects robots.txt (when applicable)
- Educational/research use only
- Terms of service awareness

## Integration Examples

### With Existing Scripts

```python
# Modify existing literature search
from scripts.search_literature import LiteratureSearcher

searcher = LiteratureSearcher()

# Browser automation is now used automatically for Google Scholar
results = searcher._search_google_scholar("AI finance", "2020-2025")
```

### Custom Searches

```python
from scripts.browser_automation import BrowserAutomation, BrowserConfig

config = BrowserConfig(
    headless=True,
    request_delay_range=(10, 20),  # More conservative delays
    captcha_detection=True
)

browser = BrowserAutomation(config)

try:
    browser.start_session()
    
    # Multiple searches in one session
    queries = ["AI agents", "machine learning finance", "automated trading"]
    
    all_results = []
    for query in queries:
        results = browser.search_google_scholar(query, max_results=15)
        all_results.extend(results)
        
        # Check session stats
        print(f"CAPTCHAs detected: {browser.session_stats['captchas_detected']}")
        
finally:
    browser.end_session()
```

## Future Enhancements

### Planned Features
- **Proxy Rotation**: Support for proxy server rotation
- **Cookie Management**: Session persistence across searches
- **Multi-Browser Support**: Firefox and Safari support
- **ML-Based Detection**: Machine learning for better CAPTCHA detection
- **Distributed Searching**: Multiple browser instances

### API Extensions
- REST API for browser automation services
- Queue-based search processing
- Real-time monitoring dashboard
- Advanced analytics and reporting

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the test suite to validate setup
3. Review session statistics and logs
4. Consult the main project documentation

---

*This browser automation system is designed for academic research and educational purposes. Please ensure compliance with website terms of service and applicable laws.*