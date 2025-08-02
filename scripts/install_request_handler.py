#!/usr/bin/env python3
"""
Installation script for the intelligent request handler
Sets up dependencies and configuration
"""

import subprocess
import sys
from pathlib import Path


def install_requirements():
    """Install required packages"""
    requirements_file = Path(__file__).parent.parent / "requirements_request_handler.txt"
    
    if requirements_file.exists():
        print("Installing request handler requirements...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "-r", str(requirements_file)
        ])
        print("✅ Requirements installed successfully")
    else:
        print("❌ Requirements file not found")
        return False
    
    return True


def create_directories():
    """Create necessary directories"""
    project_root = Path(__file__).parent.parent
    
    directories = [
        project_root / ".request_handler",
        project_root / ".request_handler" / "sessions",
        project_root / "config",
        project_root / "research" / "search-results"
    ]
    
    print("Creating directories...")
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")
    
    return True


def test_installation():
    """Test the installation"""
    print("\nTesting installation...")
    
    try:
        # Test imports
        import aiohttp
        import aiofiles
        import yaml
        print("✅ Core dependencies imported successfully")
        
        # Test optional imports
        try:
            import bs4
            print("✅ BeautifulSoup4 available")
        except ImportError:
            print("⚠️  BeautifulSoup4 not available (optional)")
        
        # Test request handler import
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.request_handler import IntelligentRequestHandler
        print("✅ Request handler imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def main():
    """Main installation function"""
    print("🚀 Installing Intelligent Request Handler")
    print("=" * 50)
    
    success = True
    
    # Install requirements
    if not install_requirements():
        success = False
    
    # Create directories
    if not create_directories():
        success = False
    
    # Test installation
    if not test_installation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Installation completed successfully!")
        print("\nNext steps:")
        print("1. Configure proxies in config/request_handler_config.yaml")
        print("2. Test with: python scripts/test_request_handler.py")
        print("3. Use enhanced search: python scripts/enhanced_literature_search.py")
    else:
        print("❌ Installation failed. Please check the errors above.")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)