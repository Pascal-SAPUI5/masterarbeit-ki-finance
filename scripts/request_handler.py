#!/usr/bin/env python3
"""
Intelligent Request Handler with Throttling and Session Management
Implements adaptive rate limiting, session persistence, and proxy rotation
"""

import asyncio
import json
import logging
import pickle
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import os
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.utils import get_project_root, get_timestamp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    CONSERVATIVE = "conservative"  # 1 req per 10s initially
    BALANCED = "balanced"         # 1 req per 7s initially
    AGGRESSIVE = "aggressive"     # 1 req per 5s initially


class RequestStatus(Enum):
    """Request status types"""
    SUCCESS = "success"
    RATE_LIMITED = "rate_limited"
    CAPTCHA_REQUIRED = "captcha_required"
    BLOCKED = "blocked"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class RequestStats:
    """Track request statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rate_limited_requests: int = 0
    captcha_requests: int = 0
    blocked_requests: int = 0
    average_response_time: float = 0.0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    current_delay: float = 10.0
    success_streak: int = 0
    failure_streak: int = 0


@dataclass
class ProxyConfig:
    """Proxy configuration"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"
    
    @property
    def url(self) -> str:
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"


class SessionManager:
    """Manages persistent sessions with cookies and headers"""
    
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, aiohttp.ClientSession] = {}
        self.session_data: Dict[str, Dict] = {}
        
    async def get_session(self, session_id: str, headers: Optional[Dict] = None) -> aiohttp.ClientSession:
        """Get or create a session with persistent cookies"""
        if session_id not in self.sessions:
            # Load persistent session data
            session_file = self.session_dir / f"{session_id}.pkl"
            cookies = None
            
            if session_file.exists():
                try:
                    async with aiofiles.open(session_file, 'rb') as f:
                        session_data = pickle.loads(await f.read())
                        cookies = session_data.get('cookies')
                        logger.info(f"Loaded persistent session data for {session_id}")
                except Exception as e:
                    logger.warning(f"Failed to load session data: {e}")
            
            # Default headers for web scraping
            default_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            if headers:
                default_headers.update(headers)
            
            # Create timeout configuration
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            # Create session with persistent cookies
            jar = aiohttp.CookieJar()
            if cookies:
                for cookie_data in cookies:
                    jar.update_cookies(cookie_data)
            
            session = aiohttp.ClientSession(
                headers=default_headers,
                timeout=timeout,
                cookie_jar=jar,
                connector=aiohttp.TCPConnector(limit=10, limit_per_host=5)
            )
            
            self.sessions[session_id] = session
            self.session_data[session_id] = {}
            
        return self.sessions[session_id]
    
    async def save_session(self, session_id: str):
        """Save session cookies and data to disk"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session_file = self.session_dir / f"{session_id}.pkl"
            
            # Extract cookies
            cookies = []
            for cookie in session.cookie_jar:
                cookies.append({
                    'name': cookie.key,
                    'value': cookie.value,
                    'domain': cookie.get('domain', ''),
                    'path': cookie.get('path', '/'),
                })
            
            session_data = {
                'cookies': cookies,
                'timestamp': datetime.now().isoformat(),
                'data': self.session_data.get(session_id, {})
            }
            
            try:
                async with aiofiles.open(session_file, 'wb') as f:
                    await f.write(pickle.dumps(session_data))
                logger.info(f"Saved session data for {session_id}")
            except Exception as e:
                logger.error(f"Failed to save session data: {e}")
    
    async def close_session(self, session_id: str):
        """Close and save a session"""
        if session_id in self.sessions:
            await self.save_session(session_id)
            await self.sessions[session_id].close()
            del self.sessions[session_id]
            if session_id in self.session_data:
                del self.session_data[session_id]
    
    async def close_all_sessions(self):
        """Close all sessions"""
        for session_id in list(self.sessions.keys()):
            await self.close_session(session_id)


class ProxyRotator:
    """Manages proxy rotation with health checks"""
    
    def __init__(self, proxies: List[ProxyConfig]):
        self.proxies = proxies
        self.current_index = 0
        self.failed_proxies: set = set()
        self.proxy_stats: Dict[str, Dict] = {}
        
    def get_current_proxy(self) -> Optional[ProxyConfig]:
        """Get current working proxy"""
        if not self.proxies:
            return None
            
        attempts = 0
        while attempts < len(self.proxies):
            proxy = self.proxies[self.current_index]
            proxy_key = f"{proxy.host}:{proxy.port}"
            
            if proxy_key not in self.failed_proxies:
                return proxy
                
            self.current_index = (self.current_index + 1) % len(self.proxies)
            attempts += 1
            
        return None  # All proxies failed
    
    def mark_proxy_failed(self, proxy: ProxyConfig):
        """Mark a proxy as failed"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        self.failed_proxies.add(proxy_key)
        logger.warning(f"Marked proxy {proxy_key} as failed")
        
    def rotate_proxy(self):
        """Move to next proxy"""
        self.current_index = (self.current_index + 1) % len(self.proxies)
        
    async def test_proxy(self, proxy: ProxyConfig) -> bool:
        """Test if proxy is working"""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    'http://httpbin.org/ip',
                    proxy=proxy.url
                ) as response:
                    if response.status == 200:
                        logger.info(f"Proxy {proxy.host}:{proxy.port} is working")
                        return True
        except Exception as e:
            logger.warning(f"Proxy {proxy.host}:{proxy.port} failed test: {e}")
        return False


class IntelligentRequestHandler:
    """
    Intelligent request handler with adaptive rate limiting,
    session persistence, and proxy rotation
    """
    
    def __init__(
        self,
        strategy: RateLimitStrategy = RateLimitStrategy.CONSERVATIVE,
        session_dir: Optional[Path] = None,
        proxies: Optional[List[ProxyConfig]] = None,
        enable_cookies: bool = True
    ):
        self.project_root = get_project_root()
        self.strategy = strategy
        self.stats = RequestStats()
        
        # Set up session directory
        if session_dir is None:
            session_dir = self.project_root / ".request_handler" / "sessions"
        self.session_manager = SessionManager(session_dir)
        
        # Set up proxy rotation
        self.proxy_rotator = ProxyRotator(proxies or [])
        
        # Rate limiting configuration
        self.rate_limits = {
            RateLimitStrategy.CONSERVATIVE: {
                'initial_delay': 10.0,
                'success_reduction': 0.8,
                'failure_increase': 2.0,
                'min_delay': 5.0,
                'max_delay': 60.0
            },
            RateLimitStrategy.BALANCED: {
                'initial_delay': 7.0,
                'success_reduction': 0.9,
                'failure_increase': 1.5,
                'min_delay': 3.0,
                'max_delay': 45.0
            },
            RateLimitStrategy.AGGRESSIVE: {
                'initial_delay': 5.0,
                'success_reduction': 0.95,
                'failure_increase': 1.2,
                'min_delay': 2.0,
                'max_delay': 30.0
            }
        }
        
        self.current_config = self.rate_limits[strategy]
        self.stats.current_delay = self.current_config['initial_delay']
        
        # Request history for pattern detection
        self.request_history: List[Tuple[datetime, RequestStatus, float]] = []
        
        # Randomization settings
        self.randomize_intervals = True
        self.min_random_delay = 5.0
        self.max_random_delay = 15.0
        
        # CAPTCHA handling
        self.captcha_pause_duration = 30.0
        self.last_captcha_time: Optional[datetime] = None
        
    def _get_randomized_delay(self) -> float:
        """Get randomized delay based on current strategy"""
        if not self.randomize_intervals:
            return self.stats.current_delay
            
        # Add randomization (±20% of current delay)
        base_delay = self.stats.current_delay
        randomization = base_delay * 0.2
        
        # Ensure we stay within global min/max bounds
        min_delay = max(self.min_random_delay, base_delay - randomization)
        max_delay = min(self.max_random_delay, base_delay + randomization)
        
        return random.uniform(min_delay, max_delay)
    
    def _update_rate_limit(self, status: RequestStatus, response_time: float):
        """Update rate limiting based on request outcome"""
        config = self.current_config
        
        if status == RequestStatus.SUCCESS:
            self.stats.success_streak += 1
            self.stats.failure_streak = 0
            
            # Reduce delay after successful requests
            if self.stats.success_streak >= 10:  # After 10 successful requests
                self.stats.current_delay *= config['success_reduction']
                self.stats.current_delay = max(
                    config['min_delay'],
                    self.stats.current_delay
                )
                self.stats.success_streak = 0  # Reset streak
                
        elif status in [RequestStatus.RATE_LIMITED, RequestStatus.BLOCKED]:
            self.stats.failure_streak += 1
            self.stats.success_streak = 0
            
            # Increase delay after rate limiting
            self.stats.current_delay *= config['failure_increase']
            self.stats.current_delay = min(
                config['max_delay'],
                self.stats.current_delay
            )
            
        elif status == RequestStatus.CAPTCHA_REQUIRED:
            # Special handling for CAPTCHA
            self.last_captcha_time = datetime.now()
            self.stats.current_delay = max(
                self.captcha_pause_duration,
                self.stats.current_delay * 2
            )
            
        # Update average response time
        if response_time > 0:
            if self.stats.average_response_time == 0:
                self.stats.average_response_time = response_time
            else:
                self.stats.average_response_time = (
                    self.stats.average_response_time * 0.9 + response_time * 0.1
                )
    
    def _detect_request_status(self, response: aiohttp.ClientResponse, content: str) -> RequestStatus:
        """Detect request status from response"""
        # Check status codes
        if response.status == 429:
            return RequestStatus.RATE_LIMITED
        elif response.status == 403:
            return RequestStatus.BLOCKED
        elif response.status >= 400:
            return RequestStatus.ERROR
            
        # Check content for CAPTCHA indicators
        captcha_indicators = [
            'captcha', 'recaptcha', 'hcaptcha',
            'security check', 'verify you are human',
            'unusual traffic', 'suspicious activity'
        ]
        
        content_lower = content.lower()
        if any(indicator in content_lower for indicator in captcha_indicators):
            return RequestStatus.CAPTCHA_REQUIRED
            
        # Check for blocking indicators
        blocking_indicators = [
            'access denied', 'blocked', 'banned',
            'too many requests', 'rate limit'
        ]
        
        if any(indicator in content_lower for indicator in blocking_indicators):
            return RequestStatus.BLOCKED
            
        return RequestStatus.SUCCESS
    
    async def _wait_for_rate_limit(self):
        """Wait according to current rate limiting strategy"""
        # Check if we're in CAPTCHA pause period
        if self.last_captcha_time:
            time_since_captcha = datetime.now() - self.last_captcha_time
            if time_since_captcha.total_seconds() < self.captcha_pause_duration:
                remaining_pause = self.captcha_pause_duration - time_since_captcha.total_seconds()
                logger.info(f"CAPTCHA pause: waiting {remaining_pause:.1f} more seconds")
                await asyncio.sleep(remaining_pause)
                
        # Get randomized delay
        delay = self._get_randomized_delay()
        logger.info(f"Rate limiting: waiting {delay:.1f} seconds")
        await asyncio.sleep(delay)
    
    async def make_request(
        self,
        url: str,
        method: str = 'GET',
        session_id: str = 'default',
        headers: Optional[Dict] = None,
        data: Optional[Union[Dict, str]] = None,
        params: Optional[Dict] = None,
        use_proxy: bool = True
    ) -> Tuple[RequestStatus, Optional[aiohttp.ClientResponse], Optional[str]]:
        """
        Make an intelligent HTTP request with rate limiting and error handling
        
        Args:
            url: Target URL
            method: HTTP method
            session_id: Session identifier for cookie persistence
            headers: Additional headers
            data: Request data
            params: URL parameters
            use_proxy: Whether to use proxy rotation
            
        Returns:
            Tuple of (status, response, content)
        """
        start_time = time.time()
        
        # Wait for rate limiting
        await self._wait_for_rate_limit()
        
        # Get session
        session = await self.session_manager.get_session(session_id, headers)
        
        # Get proxy if enabled
        proxy = None
        if use_proxy and self.proxy_rotator.proxies:
            proxy_config = self.proxy_rotator.get_current_proxy()
            if proxy_config:
                proxy = proxy_config.url
        
        try:
            # Make request
            async with session.request(
                method=method,
                url=url,
                data=data,
                params=params,
                proxy=proxy
            ) as response:
                content = await response.text()
                response_time = time.time() - start_time
                
                # Detect status
                status = self._detect_request_status(response, content)
                
                # Update statistics
                self.stats.total_requests += 1
                if status == RequestStatus.SUCCESS:
                    self.stats.successful_requests += 1
                    self.stats.last_success_time = datetime.now()
                else:
                    self.stats.failed_requests += 1
                    self.stats.last_failure_time = datetime.now()
                    
                    if status == RequestStatus.RATE_LIMITED:
                        self.stats.rate_limited_requests += 1
                    elif status == RequestStatus.CAPTCHA_REQUIRED:
                        self.stats.captcha_requests += 1
                    elif status == RequestStatus.BLOCKED:
                        self.stats.blocked_requests += 1
                
                # Update rate limiting
                self._update_rate_limit(status, response_time)
                
                # Record in history
                self.request_history.append((
                    datetime.now(), status, response_time
                ))
                
                # Keep only last 100 requests in history
                if len(self.request_history) > 100:
                    self.request_history = self.request_history[-100:]
                
                # Handle proxy rotation on failure
                if status in [RequestStatus.BLOCKED, RequestStatus.RATE_LIMITED] and proxy:
                    self.proxy_rotator.rotate_proxy()
                
                # Save session after successful requests
                if status == RequestStatus.SUCCESS:
                    await self.session_manager.save_session(session_id)
                
                return status, response, content
                
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self.stats.total_requests += 1
            self.stats.failed_requests += 1
            self._update_rate_limit(RequestStatus.TIMEOUT, response_time)
            
            return RequestStatus.TIMEOUT, None, None
            
        except Exception as e:
            response_time = time.time() - start_time
            self.stats.total_requests += 1
            self.stats.failed_requests += 1
            self._update_rate_limit(RequestStatus.ERROR, response_time)
            
            logger.error(f"Request error: {e}")
            return RequestStatus.ERROR, None, str(e)
    
    async def batch_requests(
        self,
        urls: List[str],
        session_id: str = 'batch',
        max_concurrent: int = 3,
        **request_kwargs
    ) -> List[Tuple[str, RequestStatus, Optional[str]]]:
        """
        Make multiple requests with intelligent batching and rate limiting
        
        Args:
            urls: List of URLs to request
            session_id: Session identifier
            max_concurrent: Maximum concurrent requests
            **request_kwargs: Additional arguments for make_request
            
        Returns:
            List of (url, status, content) tuples
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        results = []
        
        async def make_single_request(url: str):
            async with semaphore:
                status, response, content = await self.make_request(
                    url=url,
                    session_id=session_id,
                    **request_kwargs
                )
                return url, status, content
        
        # Execute requests with concurrency control
        tasks = [make_single_request(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        clean_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Batch request exception: {result}")
            else:
                clean_results.append(result)
        
        return clean_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current request statistics"""
        success_rate = 0.0
        if self.stats.total_requests > 0:
            success_rate = self.stats.successful_requests / self.stats.total_requests
            
        return {
            'total_requests': self.stats.total_requests,
            'successful_requests': self.stats.successful_requests,
            'failed_requests': self.stats.failed_requests,
            'success_rate': success_rate,
            'rate_limited_requests': self.stats.rate_limited_requests,
            'captcha_requests': self.stats.captcha_requests,
            'blocked_requests': self.stats.blocked_requests,
            'current_delay': self.stats.current_delay,
            'average_response_time': self.stats.average_response_time,
            'success_streak': self.stats.success_streak,
            'failure_streak': self.stats.failure_streak,
            'strategy': self.strategy.value,
            'last_success': self.stats.last_success_time.isoformat() if self.stats.last_success_time else None,
            'last_failure': self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None
        }
    
    async def save_stats(self, filepath: Optional[Path] = None):
        """Save statistics to file"""
        if filepath is None:
            filepath = self.project_root / ".request_handler" / "stats.json"
            
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        stats_data = self.get_stats()
        stats_data['timestamp'] = datetime.now().isoformat()
        
        async with aiofiles.open(filepath, 'w') as f:
            await f.write(json.dumps(stats_data, indent=2))
    
    async def cleanup(self):
        """Clean up resources"""
        await self.session_manager.close_all_sessions()
        await self.save_stats()


# Example usage functions
async def test_google_scholar_requests():
    """Test the request handler with Google Scholar"""
    # Sample proxies (replace with real ones)
    proxies = [
        ProxyConfig("proxy1.example.com", 8080),
        ProxyConfig("proxy2.example.com", 8080),
    ]
    
    handler = IntelligentRequestHandler(
        strategy=RateLimitStrategy.CONSERVATIVE,
        proxies=proxies
    )
    
    test_urls = [
        "https://scholar.google.com/scholar?q=artificial+intelligence+finance",
        "https://scholar.google.com/scholar?q=machine+learning+trading",
        "https://scholar.google.com/scholar?q=algorithmic+trading+AI"
    ]
    
    print("Testing intelligent request handler...")
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nRequest {i}/{len(test_urls)}: {url}")
        
        status, response, content = await handler.make_request(
            url=url,
            session_id="scholar_test"
        )
        
        print(f"Status: {status.value}")
        if response:
            print(f"HTTP Status: {response.status}")
            print(f"Content Length: {len(content) if content else 0}")
        
        # Print current stats
        stats = handler.get_stats()
        print(f"Success Rate: {stats['success_rate']:.2%}")
        print(f"Current Delay: {stats['current_delay']:.1f}s")
        
    await handler.cleanup()


if __name__ == "__main__":
    # Test the request handler
    asyncio.run(test_google_scholar_requests())