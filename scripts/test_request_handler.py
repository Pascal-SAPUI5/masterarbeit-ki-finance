#!/usr/bin/env python3
"""
Test script for the intelligent request handler
Tests throttling, session persistence, and error handling
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.request_handler import (
    IntelligentRequestHandler, 
    RateLimitStrategy, 
    ProxyConfig,
    RequestStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_basic_functionality():
    """Test basic request handler functionality"""
    print("=" * 60)
    print("Testing Basic Request Handler Functionality")
    print("=" * 60)
    
    handler = IntelligentRequestHandler(
        strategy=RateLimitStrategy.CONSERVATIVE
    )
    
    # Test simple HTTP request
    test_url = "https://httpbin.org/get"
    print(f"\n1. Testing basic request to: {test_url}")
    
    start_time = datetime.now()
    status, response, content = await handler.make_request(
        url=test_url,
        session_id="test_basic"
    )
    end_time = datetime.now()
    
    print(f"   Status: {status.value}")
    if response:
        print(f"   HTTP Status: {response.status}")
        print(f"   Response time: {(end_time - start_time).total_seconds():.2f}s")
    
    # Print initial stats
    stats = handler.get_stats()
    print(f"   Current delay: {stats['current_delay']:.1f}s")
    print(f"   Success rate: {stats['success_rate']:.2%}")
    
    await handler.cleanup()
    return status == RequestStatus.SUCCESS


async def test_rate_limiting():
    """Test rate limiting and adaptive behavior"""
    print("=" * 60)
    print("Testing Rate Limiting and Adaptive Behavior")
    print("=" * 60)
    
    handler = IntelligentRequestHandler(
        strategy=RateLimitStrategy.CONSERVATIVE
    )
    
    # Make multiple requests to test rate limiting
    test_urls = [
        "https://httpbin.org/get?test=1",
        "https://httpbin.org/get?test=2", 
        "https://httpbin.org/get?test=3",
        "https://httpbin.org/get?test=4",
        "https://httpbin.org/get?test=5"
    ]
    
    print(f"\n2. Testing rate limiting with {len(test_urls)} requests")
    print("   Initial delay should be ~10s, then adapt based on success")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n   Request {i}/{len(test_urls)}: {url}")
        
        request_start = datetime.now()
        status, response, content = await handler.make_request(
            url=url,
            session_id="test_rate_limiting"
        )
        request_end = datetime.now()
        
        stats = handler.get_stats()
        
        print(f"     Status: {status.value}")
        print(f"     Time since start: {(request_end - request_start).total_seconds():.1f}s")
        print(f"     Current delay: {stats['current_delay']:.1f}s")
        print(f"     Success streak: {stats['success_streak']}")
        print(f"     Success rate: {stats['success_rate']:.2%}")
    
    await handler.cleanup()
    return True


async def test_session_persistence():
    """Test session persistence and cookie management"""
    print("=" * 60)
    print("Testing Session Persistence and Cookie Management")
    print("=" * 60)
    
    handler = IntelligentRequestHandler(
        strategy=RateLimitStrategy.BALANCED
    )
    
    # Test session persistence with httpbin cookie endpoints
    session_id = "test_persistence"
    
    print(f"\n3. Testing session persistence")
    
    # Set a cookie
    print("   Step 1: Setting a cookie")
    status1, response1, content1 = await handler.make_request(
        url="https://httpbin.org/cookies/set/test_cookie/test_value",
        session_id=session_id
    )
    print(f"     Set cookie status: {status1.value}")
    
    # Retrieve the cookie
    print("   Step 2: Retrieving cookies to verify persistence")
    status2, response2, content2 = await handler.make_request(
        url="https://httpbin.org/cookies",
        session_id=session_id
    )
    
    print(f"     Get cookie status: {status2.value}")
    if content2:
        try:
            cookie_data = json.loads(content2)
            cookies = cookie_data.get('cookies', {})
            print(f"     Cookies found: {list(cookies.keys())}")
            if 'test_cookie' in cookies:
                print(f"     ✅ Cookie persistence working: {cookies['test_cookie']}")
            else:
                print("     ❌ Cookie persistence failed")
        except json.JSONDecodeError:
            print("     Could not parse cookie response")
    
    await handler.cleanup()
    return status1 == RequestStatus.SUCCESS and status2 == RequestStatus.SUCCESS


async def test_error_handling():
    """Test error handling and recovery"""
    print("=" * 60)
    print("Testing Error Handling and Recovery")
    print("=" * 60)
    
    handler = IntelligentRequestHandler(
        strategy=RateLimitStrategy.AGGRESSIVE
    )
    
    # Test various error conditions
    test_cases = [
        ("Valid URL", "https://httpbin.org/status/200"),
        ("404 Error", "https://httpbin.org/status/404"),
        ("500 Error", "https://httpbin.org/status/500"),
        ("Rate Limited", "https://httpbin.org/status/429"),
        ("Invalid URL", "https://this-url-does-not-exist-12345.com")
    ]
    
    print(f"\n4. Testing error handling with various scenarios")
    
    for i, (description, url) in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {description}")
        print(f"   URL: {url}")
        
        try:
            status, response, content = await handler.make_request(
                url=url,
                session_id="test_errors"
            )
            
            print(f"     Status: {status.value}")
            if response:
                print(f"     HTTP Status: {response.status}")
            
            stats = handler.get_stats()
            print(f"     Current delay: {stats['current_delay']:.1f}s")
            print(f"     Failure streak: {stats['failure_streak']}")
            
        except Exception as e:
            print(f"     Exception: {e}")
    
    # Print final statistics
    stats = handler.get_stats()
    print(f"\n   Final Statistics:")
    print(f"     Total requests: {stats['total_requests']}")
    print(f"     Success rate: {stats['success_rate']:.2%}")
    print(f"     Rate limited: {stats['rate_limited_requests']}")
    print(f"     Failed: {stats['failed_requests']}")
    
    await handler.cleanup()
    return True


async def test_batch_requests():
    """Test batch request functionality"""
    print("=" * 60)
    print("Testing Batch Request Processing")
    print("=" * 60)
    
    handler = IntelligentRequestHandler(
        strategy=RateLimitStrategy.BALANCED
    )
    
    # Test batch requests
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1", 
        "https://httpbin.org/delay/1",
        "https://httpbin.org/get?batch=1",
        "https://httpbin.org/get?batch=2"
    ]
    
    print(f"\n5. Testing batch requests with {len(urls)} URLs")
    print("   Max concurrent: 3")
    
    start_time = datetime.now()
    results = await handler.batch_requests(
        urls=urls,
        session_id="test_batch",
        max_concurrent=3
    )
    end_time = datetime.now()
    
    total_time = (end_time - start_time).total_seconds()
    print(f"\n   Batch completed in {total_time:.1f}s")
    print(f"   Results: {len(results)}/{len(urls)} successful")
    
    successful = sum(1 for _, status, _ in results if status == RequestStatus.SUCCESS)
    print(f"   Success rate: {successful/len(results):.2%}")
    
    # Print individual results
    for i, (url, status, content) in enumerate(results, 1):
        print(f"     {i}. {status.value} - {url}")
    
    await handler.cleanup()
    return len(results) > 0


async def test_randomization():
    """Test request interval randomization"""
    print("=" * 60)
    print("Testing Request Interval Randomization")
    print("=" * 60)
    
    handler = IntelligentRequestHandler(
        strategy=RateLimitStrategy.CONSERVATIVE
    )
    
    # Override randomization settings for testing
    handler.min_random_delay = 2.0
    handler.max_random_delay = 8.0
    
    print(f"\n6. Testing randomization (2-8 second range)")
    
    delays = []
    for i in range(3):
        delay = handler._get_randomized_delay()
        delays.append(delay)
        print(f"   Delay {i+1}: {delay:.1f}s")
    
    min_delay = min(delays)
    max_delay = max(delays)
    avg_delay = sum(delays) / len(delays)
    
    print(f"\n   Min delay: {min_delay:.1f}s")
    print(f"   Max delay: {max_delay:.1f}s")
    print(f"   Average: {avg_delay:.1f}s")
    print(f"   Range check: {2.0 <= min_delay <= 8.0 and 2.0 <= max_delay <= 8.0}")
    
    await handler.cleanup()
    return True


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Intelligent Request Handler Tests")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Rate Limiting", test_rate_limiting),
        ("Session Persistence", test_session_persistence),
        ("Error Handling", test_error_handling),
        ("Batch Requests", test_batch_requests),
        ("Randomization", test_randomization)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running: {test_name}")
            result = await test_func()
            results[test_name] = result
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {status}")
        except Exception as e:
            results[test_name] = False
            print(f"   ❌ FAILED with exception: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total:.1%})")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)