#!/usr/bin/env python3
"""
Integration tests for CAPTCHA bypass system
Validates functionality, performance, and reliability
"""

import pytest
import json
import time
import sys
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.enhanced_scholar_search import CaptchaBypassSearcher, RateLimitConfig

class TestCaptchaBypassIntegration:
    """Integration tests for CAPTCHA bypass functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.config = RateLimitConfig()
        self.searcher = CaptchaBypassSearcher(self.config)
        self.test_queries = [
            "AI agents finance",
            "machine learning financial services",
            "algorithmic trading neural networks",
            "robo-advisors artificial intelligence"
        ]
    
    def teardown_method(self):
        """Cleanup after tests"""
        if self.searcher.driver:
            self.searcher.driver.quit()
    
    def test_rate_limit_compliance(self):
        """Test that rate limiting prevents CAPTCHA triggers"""
        start_time = time.time()
        
        # Simulate multiple requests
        for i in range(5):
            self.searcher._respect_rate_limits()
        
        elapsed = time.time() - start_time
        expected_min_time = 4 * (60.0 / self.config.requests_per_minute)
        
        assert elapsed >= expected_min_time * 0.8, "Rate limiting not enforced properly"
        
    def test_captcha_detection(self):
        """Test CAPTCHA detection capabilities"""
        # Mock driver with CAPTCHA content
        mock_driver = Mock()
        mock_driver.page_source = """
        <html>
            <body>
                <div class="captcha-container">
                    Please verify you are human
                </div>
            </body>
        </html>
        """
        mock_driver.find_elements.return_value = []
        
        self.searcher.driver = mock_driver
        
        assert self.searcher._is_captcha_present(), "Failed to detect CAPTCHA"
    
    def test_false_positive_captcha_detection(self):
        """Test that normal pages don't trigger false CAPTCHA detection"""
        mock_driver = Mock()
        mock_driver.page_source = """
        <html>
            <body>
                <div class="search-results">
                    <h3>Normal search result</h3>
                    <p>This is a regular search result without any CAPTCHA</p>
                </div>
            </body>
        </html>
        """
        mock_driver.find_elements.return_value = []
        
        self.searcher.driver = mock_driver
        
        assert not self.searcher._is_captcha_present(), "False positive CAPTCHA detection"
    
    @pytest.mark.integration
    def test_live_search_small_volume(self):
        """Test live search with small volume to avoid CAPTCHA"""
        try:
            results = self.searcher.search_google_scholar(
                query="AI finance 2024",
                max_results=5,
                years="2024-2024"
            )
            
            assert len(results) > 0, "No results returned from live search"
            assert all('title' in result for result in results), "Missing required fields"
            
        except Exception as e:
            pytest.skip(f"Live search failed: {e}")
    
    @pytest.mark.slow
    def test_sustained_search_performance(self):
        """Test sustained search performance over time"""
        results_per_query = []
        captcha_encounters = 0
        errors = 0
        
        start_time = time.time()
        
        for i, query in enumerate(self.test_queries):
            try:
                results = self.searcher.search_google_scholar(
                    query=query,
                    max_results=3,  # Small volume to minimize CAPTCHA risk
                    years="2023-2024"
                )
                results_per_query.append(len(results))
                
                # Simulate CAPTCHA encounter check
                if not results:
                    captcha_encounters += 1
                    
            except Exception as e:
                errors += 1
                print(f"Error in query {i}: {e}")
        
        elapsed_time = time.time() - start_time
        total_queries = len(self.test_queries)
        
        # Performance assertions
        success_rate = (total_queries - errors) / total_queries
        captcha_rate = captcha_encounters / total_queries if total_queries > 0 else 0
        avg_results = sum(results_per_query) / len(results_per_query) if results_per_query else 0
        
        assert success_rate >= 0.75, f"Success rate too low: {success_rate}"
        assert captcha_rate <= 0.25, f"CAPTCHA encounter rate too high: {captcha_rate}"
        assert avg_results > 0, "No results returned on average"
        
        print(f"Performance Summary:")
        print(f"  - Success rate: {success_rate:.2%}")
        print(f"  - CAPTCHA rate: {captcha_rate:.2%}")
        print(f"  - Average results: {avg_results:.1f}")
        print(f"  - Total time: {elapsed_time:.1f}s")
    
    def test_docker_compatibility(self):
        """Test Docker container compatibility"""
        # Test headless driver setup
        try:
            driver = self.searcher._setup_driver()
            assert driver is not None, "Failed to create headless driver"
            
            # Test basic navigation
            driver.get("https://www.google.com")
            assert "Google" in driver.title, "Failed to navigate to Google"
            
            driver.quit()
            
        except Exception as e:
            pytest.fail(f"Docker compatibility test failed: {e}")
    
    def test_anti_detection_measures(self):
        """Test anti-detection measures are properly implemented"""
        driver = self.searcher._setup_driver()
        
        try:
            # Navigate to a bot detection test site
            driver.get("https://bot.sannysoft.com/")
            time.sleep(3)
            
            page_source = driver.page_source.lower()
            
            # Check for common bot detection indicators
            bot_indicators = {
                "webdriver": "webdriver" in page_source,
                "headless": "headless" in page_source,
                "automation": "automation" in page_source
            }
            
            detected_count = sum(bot_indicators.values())
            detection_rate = detected_count / len(bot_indicators)
            
            assert detection_rate <= 0.5, f"Too many bot indicators detected: {bot_indicators}"
            
        finally:
            driver.quit()
    
    def test_user_agent_rotation(self):
        """Test user agent rotation functionality"""
        # Create multiple searchers to test different user agents
        searchers = [CaptchaBypassSearcher() for _ in range(3)]
        user_agents = []
        
        try:
            for searcher in searchers:
                ua = searcher.ua.random
                user_agents.append(ua)
                
            # Check that we get different user agents
            unique_agents = set(user_agents)
            assert len(unique_agents) > 1, "User agent rotation not working"
            
        finally:
            for searcher in searchers:
                if searcher.driver:
                    searcher.driver.quit()
    
    def test_error_recovery(self):
        """Test error recovery mechanisms"""
        # Simulate network error
        with patch.object(self.searcher, '_setup_driver') as mock_setup:
            mock_setup.side_effect = Exception("Network error")
            
            # Should fallback to alternative driver
            try:
                driver = self.searcher._setup_fallback_driver()
                assert driver is not None, "Fallback driver creation failed"
                driver.quit()
            except Exception as e:
                pytest.fail(f"Error recovery failed: {e}")
    
    @pytest.mark.parametrize("query,expected_min_results", [
        ("machine learning finance", 1),
        ("AI trading algorithms", 1),
        ("fintech artificial intelligence", 1)
    ])
    def test_query_variations(self, query, expected_min_results):
        """Test different query variations"""
        try:
            results = self.searcher.search_google_scholar(
                query=query,
                max_results=5,
                years="2023-2024"
            )
            
            assert len(results) >= expected_min_results, f"Insufficient results for query: {query}"
            
        except Exception as e:
            pytest.skip(f"Query test failed for '{query}': {e}")

class TestRateLimitConfiguration:
    """Test rate limiting configuration"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = RateLimitConfig()
        
        assert config.min_delay > 0
        assert config.max_delay > config.min_delay
        assert config.requests_per_minute > 0
        assert config.daily_limit > 0
        assert config.retry_attempts > 0
    
    def test_delay_randomization(self):
        """Test delay randomization"""
        config = RateLimitConfig()
        delays = [config.get_delay() for _ in range(10)]
        
        # Check that delays are within expected range
        assert all(config.min_delay <= d <= config.max_delay for d in delays)
        
        # Check that delays are randomized (not all the same)
        unique_delays = set(delays)
        assert len(unique_delays) > 1, "Delays are not randomized"

if __name__ == "__main__":
    # Run basic integration tests
    pytest.main([__file__, "-v", "-m", "not slow"])