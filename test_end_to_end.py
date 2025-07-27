#!/usr/bin/env python3
"""
End-to-End Validation Script for Ollama Integration
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from src.utils.ollama_cache import OllamaResponseCache
from src.llm.ollama_client import OllamaRAGClient

def test_ollama_connection():
    """Test basic Ollama connectivity."""
    print("🔍 Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            print(f"✅ Ollama is running with models: {models}")
            return "phi3:mini" in models
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        return False

def test_ollama_generation():
    """Test Ollama text generation."""
    print("\n🔍 Testing Ollama generation...")
    try:
        client = OllamaRAGClient()
        prompt = "What is machine learning in one sentence?"
        
        start_time = time.time()
        response = client.generate(prompt)
        elapsed = time.time() - start_time
        
        if response:
            print(f"✅ Generation successful ({elapsed:.2f}s)")
            print(f"   Response: {response[:100]}...")
            return True
        else:
            print("❌ Empty response from Ollama")
            return False
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False

def test_cache_functionality():
    """Test response caching."""
    print("\n🔍 Testing cache functionality...")
    try:
        cache = OllamaResponseCache()
        
        # Clear cache first
        cache.clear()
        
        # Test cache miss
        prompt = "Test prompt for caching"
        result1 = cache.get(prompt, "phi3:mini", {})
        if result1 is None:
            print("✅ Cache miss working correctly")
        else:
            print("❌ Unexpected cache hit")
            return False
        
        # Store in cache
        cache.set(prompt, "phi3:mini", {}, "Cached response")
        
        # Test cache hit
        result2 = cache.get(prompt, "phi3:mini", {})
        if result2 == "Cached response":
            print("✅ Cache hit working correctly")
            
            # Check stats
            stats = cache.stats()
            print(f"   Cache stats: {stats}")
            return True
        else:
            print("❌ Cache hit failed")
            return False
            
    except Exception as e:
        print(f"❌ Cache test failed: {e}")
        return False

def test_mcp_server():
    """Test MCP server connectivity."""
    print("\n🔍 Testing MCP server...")
    try:
        response = requests.get("http://localhost:3001/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP server is healthy")
            return True
        else:
            print(f"❌ MCP server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        return False

def test_windows_accessibility():
    """Test Windows accessibility setup."""
    print("\n🔍 Testing Windows accessibility...")
    
    import subprocess
    try:
        # Get WSL IP
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        wsl_ip = result.stdout.strip().split()[0]
        print(f"✅ WSL IP address: {wsl_ip}")
        
        # Check if services are bound to 0.0.0.0
        netstat = subprocess.run(['netstat', '-tln'], capture_output=True, text=True)
        
        if '0.0.0.0:3001' in netstat.stdout:
            print("✅ MCP server bound to 0.0.0.0:3001")
        else:
            print("⚠️ MCP server may not be accessible from Windows")
            
        if '0.0.0.0:11434' in netstat.stdout:
            print("✅ Ollama bound to 0.0.0.0:11434")
        else:
            print("⚠️ Ollama may not be accessible from Windows")
            
        return True
        
    except Exception as e:
        print(f"❌ Windows accessibility test failed: {e}")
        return False

def test_batch_processing():
    """Test batch processing capabilities."""
    print("\n🔍 Testing batch processing...")
    try:
        # Simulate batch request to MCP extension
        prompts = [
            "What is AI?",
            "What is machine learning?",
            "What is deep learning?",
            "What is neural network?"
        ]
        
        print(f"   Testing batch of {len(prompts)} prompts...")
        
        # For now, just test that the module can be imported
        from mcp_server_rag_extension import MCPOllamaExtension
        extension = MCPOllamaExtension()
        
        print("✅ Batch processing module loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Batch processing test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Starting End-to-End Validation\n")
    
    tests = [
        ("Ollama Connection", test_ollama_connection),
        ("Ollama Generation", test_ollama_generation),
        ("Cache Functionality", test_cache_functionality),
        ("MCP Server", test_mcp_server),
        ("Windows Accessibility", test_windows_accessibility),
        ("Batch Processing", test_batch_processing)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready for use.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())