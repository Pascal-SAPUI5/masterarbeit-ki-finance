#!/bin/bash
# Setup script for browser automation dependencies

set -e

echo "🚀 Setting up Browser Automation for Literature Search"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -qq

# Install Chrome dependencies
echo "🌐 Installing Chrome dependencies..."
sudo apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libu2f-udev \
    libvulkan1

# Install Google Chrome
if ! command_exists google-chrome; then
    echo "🔧 Installing Google Chrome..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get update -qq
    sudo apt-get install -y google-chrome-stable
    echo "✅ Google Chrome installed successfully"
else
    echo "✅ Google Chrome already installed"
fi

# Install ChromeDriver
echo "🔧 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1-3)
echo "Chrome version: $CHROME_VERSION"

# Download ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION")
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

wget -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip"
unzip -q chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip

echo "✅ ChromeDriver installed successfully"

# Install Tesseract OCR for CAPTCHA detection
echo "🔍 Installing Tesseract OCR..."
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
echo "✅ Tesseract OCR installed successfully"

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install selenium webdriver-manager Pillow pytesseract

echo ""
echo "🎉 Browser Automation Setup Complete!"
echo "======================================"
echo ""
echo "✅ Google Chrome: $(google-chrome --version)"
echo "✅ ChromeDriver: $(chromedriver --version | head -1)"
echo "✅ Tesseract: $(tesseract --version | head -1)"
echo ""
echo "🧪 To test the setup, run:"
echo "   python scripts/browser_automation.py --query 'AI agents in finance' --max-results 5"
echo ""
echo "📝 Features enabled:"
echo "   • Headless Chrome browsing"
echo "   • User-agent rotation"
echo "   • Request delay randomization (5-15 seconds)"
echo "   • CAPTCHA detection with screenshots"
echo "   • OCR text extraction from CAPTCHAs"
echo "   • Session statistics tracking"
echo ""
echo "🔒 Anti-detection measures:"
echo "   • Randomized user agents"
echo "   • Browser fingerprint masking"
echo "   • Human-like request patterns"
echo "   • Automatic proxy support (when available)"
echo ""