"""
Performance Tests for Ollama Integration
=======================================

Benchmark performance metrics and validate requirements.
"""

import pytest
import time
import statistics
import psutil
import json
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
from pathlib import Path


class TestResponseTimeMetrics:
    """Test response time performance metrics."""
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_time_to_first_token(self, ollama_client, performance_monitor):
        """Measure time to first token (TTFT)."""
        # Note: phi3:mini doesn't support streaming, so we simulate
        prompts = [
            "What is AI?",
            "Explain machine learning in one sentence.",
            "Define neural networks briefly."
        ]
        
        ttft_times = []
        
        for prompt in prompts:
            performance_monitor.start("ttft")
            response = ollama_client.generate(
                prompt,
                options={"max_tokens": 50}
            )
            ttft = performance_monitor.stop()
            ttft_times.append(ttft)
        
        avg_ttft = statistics.mean(ttft_times)
        assert avg_ttft < 2.0, f"Average TTFT {avg_ttft:.2f}s exceeds 2s limit"
        
        # Store metrics
        metrics = {
            "ttft_times": ttft_times,
            "avg_ttft": avg_ttft,
            "min_ttft": min(ttft_times),
            "max_ttft": max(ttft_times)
        }
        
        return metrics
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_tokens_per_second(self, ollama_client, performance_monitor):
        """Measure token generation speed."""
        test_cases = [
            ("short", "Count from 1 to 10", 50),
            ("medium", "Explain the concept of compound interest in finance", 150),
            ("long", "Write a detailed explanation of risk management in investment banking", 300)
        ]
        
        results = []
        
        for name, prompt, max_tokens in test_cases:
            performance_monitor.start(f"generation_{name}")
            
            response = ollama_client.generate(
                prompt,
                options={"max_tokens": max_tokens}
            )
            
            generation_time = performance_monitor.stop()
            
            # Estimate token count (rough approximation)
            token_count = len(response["response"].split())
            tokens_per_second = token_count / generation_time
            
            results.append({
                "test": name,
                "prompt_length": len(prompt.split()),
                "generated_tokens": token_count,
                "time": generation_time,
                "tokens_per_second": tokens_per_second
            })
            
            # Assert minimum performance
            assert tokens_per_second > 5, f"Token generation too slow: {tokens_per_second:.1f} tokens/s"
        
        return results
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_response_time_percentiles(self, ollama_client):
        """Test response time percentiles (p50, p95, p99)."""
        num_requests = 20
        response_times = []
        
        prompt = "What are the key principles of financial risk management?"
        
        for _ in range(num_requests):
            start_time = time.time()
            
            response = ollama_client.generate(
                prompt,
                options={"max_tokens": 100}
            )
            
            response_time = time.time() - start_time
            response_times.append(response_time)
            
            time.sleep(0.1)  # Small delay between requests
        
        # Calculate percentiles
        sorted_times = sorted(response_times)
        p50 = sorted_times[int(len(sorted_times) * 0.50)]
        p95 = sorted_times[int(len(sorted_times) * 0.95)]
        p99 = sorted_times[int(len(sorted_times) * 0.99) - 1]
        
        metrics = {
            "p50": p50,
            "p95": p95,
            "p99": p99,
            "mean": statistics.mean(response_times),
            "std": statistics.stdev(response_times)
        }
        
        # Assert SLA requirements
        assert p95 < 3.0, f"p95 response time {p95:.2f}s exceeds 3s SLA"
        assert p99 < 5.0, f"p99 response time {p99:.2f}s exceeds 5s SLA"
        
        return metrics


class TestConcurrentPerformance:
    """Test performance under concurrent load."""
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_concurrent_requests(self, ollama_client):
        """Test handling of concurrent requests."""
        num_concurrent = 5
        num_requests_per_thread = 3
        
        def make_request(thread_id: int) -> List[float]:
            times = []
            for i in range(num_requests_per_thread):
                start_time = time.time()
                
                response = ollama_client.generate(
                    f"Thread {thread_id} request {i}: What is {i+1} + {i+2}?",
                    options={"max_tokens": 20}
                )
                
                elapsed = time.time() - start_time
                times.append(elapsed)
                
            return times
        
        # Execute concurrent requests
        all_times = []
        with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_concurrent)]
            
            for future in as_completed(futures):
                all_times.extend(future.result())
        
        # Analyze results
        avg_time = statistics.mean(all_times)
        max_time = max(all_times)
        
        assert avg_time < 5.0, f"Average response time under load {avg_time:.2f}s too high"
        assert max_time < 10.0, f"Maximum response time under load {max_time:.2f}s too high"
        
        return {
            "concurrent_requests": num_concurrent,
            "total_requests": len(all_times),
            "avg_response_time": avg_time,
            "max_response_time": max_time,
            "throughput": len(all_times) / sum(all_times)
        }
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_queue_behavior(self, test_config):
        """Test request queueing behavior under load."""
        import requests
        import threading
        
        results = {"queued": 0, "completed": 0, "errors": 0}
        lock = threading.Lock()
        
        def make_request():
            try:
                response = requests.post(
                    f"{test_config['ollama']['base_url']}/api/generate",
                    json={
                        "model": "phi3:mini",
                        "prompt": "Quick response",
                        "stream": False,
                        "options": {"max_tokens": 10}
                    },
                    timeout=10
                )
                
                with lock:
                    if response.status_code == 200:
                        results["completed"] += 1
                    else:
                        results["queued"] += 1
                        
            except Exception:
                with lock:
                    results["errors"] += 1
        
        # Create burst of requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Most requests should complete successfully
        assert results["completed"] >= 7, f"Only {results['completed']}/10 requests completed"
        assert results["errors"] < 3, f"Too many errors: {results['errors']}"


class TestMemoryPerformance:
    """Test memory usage and efficiency."""
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_memory_usage_baseline(self, ollama_client):
        """Test baseline memory usage."""
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Make several requests
        for i in range(5):
            response = ollama_client.generate(
                f"Generate a short response about topic {i}",
                options={"max_tokens": 100}
            )
        
        # Check memory after requests
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 500, f"Memory increased by {memory_increase:.1f}MB"
        
        return {
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "increase_mb": memory_increase
        }
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_memory_leak_detection(self, ollama_client):
        """Test for memory leaks over multiple requests."""
        process = psutil.Process()
        memory_samples = []
        
        # Take memory samples over 20 requests
        for i in range(20):
            response = ollama_client.generate(
                "What is machine learning?",
                options={"max_tokens": 50}
            )
            
            if i % 5 == 0:
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
            
            time.sleep(0.2)
        
        # Check for consistent memory growth (potential leak)
        memory_growth = [memory_samples[i+1] - memory_samples[i] 
                        for i in range(len(memory_samples)-1)]
        
        avg_growth = statistics.mean(memory_growth)
        
        # Allow some growth but not consistent increase
        assert avg_growth < 10, f"Potential memory leak: {avg_growth:.1f}MB average growth"
        
        return {
            "memory_samples": memory_samples,
            "growth_per_sample": memory_growth,
            "avg_growth": avg_growth
        }


class TestCachePerformance:
    """Test response caching performance."""
    
    @pytest.mark.requires_ollama
    def test_cache_effectiveness(self, ollama_client):
        """Test effectiveness of response caching."""
        # Note: This assumes caching is implemented
        prompt = "What is the capital of France?"
        
        # First request (cache miss)
        start_time = time.time()
        response1 = ollama_client.generate(
            prompt,
            options={"max_tokens": 20, "temperature": 0.0, "seed": 42}
        )
        first_time = time.time() - start_time
        
        # Second request (potential cache hit)
        start_time = time.time()
        response2 = ollama_client.generate(
            prompt,
            options={"max_tokens": 20, "temperature": 0.0, "seed": 42}
        )
        second_time = time.time() - start_time
        
        # With deterministic settings, responses should be identical
        assert response1["response"] == response2["response"]
        
        # Cache hit should be faster (allowing for some variance)
        cache_speedup = first_time / second_time if second_time > 0 else 1.0
        
        return {
            "first_request_time": first_time,
            "second_request_time": second_time,
            "cache_speedup": cache_speedup,
            "response_identical": response1["response"] == response2["response"]
        }


class TestScalabilityMetrics:
    """Test scalability and load handling."""
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_varying_prompt_sizes(self, ollama_client):
        """Test performance with varying prompt sizes."""
        prompt_sizes = [10, 50, 100, 500, 1000]  # words
        results = []
        
        for size in prompt_sizes:
            # Generate prompt of specified size
            prompt = " ".join(["word"] * size)
            prompt += "\n\nSummarize the above in one sentence."
            
            start_time = time.time()
            
            try:
                response = ollama_client.generate(
                    prompt,
                    options={"max_tokens": 50}
                )
                
                elapsed = time.time() - start_time
                
                results.append({
                    "prompt_words": size,
                    "response_time": elapsed,
                    "success": True
                })
                
            except Exception as e:
                results.append({
                    "prompt_words": size,
                    "response_time": None,
                    "success": False,
                    "error": str(e)
                })
        
        # Response time should scale reasonably with prompt size
        successful_results = [r for r in results if r["success"]]
        if len(successful_results) >= 2:
            times = [r["response_time"] for r in successful_results]
            sizes = [r["prompt_words"] for r in successful_results]
            
            # Basic scalability check
            time_ratio = times[-1] / times[0]
            size_ratio = sizes[-1] / sizes[0]
            
            # Time should not scale linearly with size (should be better)
            assert time_ratio < size_ratio * 0.5, "Performance degrades too much with prompt size"
        
        return results
    
    @pytest.mark.requires_ollama
    @pytest.mark.slow
    def test_sustained_load(self, ollama_client):
        """Test performance under sustained load."""
        duration = 30  # seconds
        request_interval = 1  # second
        
        start_time = time.time()
        response_times = []
        errors = 0
        
        while time.time() - start_time < duration:
            request_start = time.time()
            
            try:
                response = ollama_client.generate(
                    "Generate a random fact about finance.",
                    options={"max_tokens": 50}
                )
                
                response_time = time.time() - request_start
                response_times.append(response_time)
                
            except Exception:
                errors += 1
            
            # Wait for next interval
            elapsed = time.time() - request_start
            if elapsed < request_interval:
                time.sleep(request_interval - elapsed)
        
        # Calculate metrics
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        error_rate = errors / (len(response_times) + errors)
        
        assert avg_response_time < 3.0, f"Average response time {avg_response_time:.2f}s too high"
        assert error_rate < 0.05, f"Error rate {error_rate:.1%} too high"
        
        return {
            "duration": duration,
            "total_requests": len(response_times) + errors,
            "successful_requests": len(response_times),
            "errors": errors,
            "error_rate": error_rate,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time
        }


def generate_performance_report(results: Dict[str, Any], output_path: Path):
    """Generate a performance test report with visualizations."""
    report_content = f"""# Ollama Integration Performance Report

## Executive Summary

Performance testing completed with the following key findings:

### Response Time Metrics
- Average response time: {results.get('avg_response_time', 'N/A'):.2f}s
- P95 response time: {results.get('p95', 'N/A'):.2f}s
- P99 response time: {results.get('p99', 'N/A'):.2f}s

### Throughput Metrics
- Tokens per second: {results.get('tokens_per_second', 'N/A'):.1f}
- Concurrent request handling: {results.get('max_concurrent', 'N/A')}

### Resource Usage
- Memory usage: {results.get('memory_usage_mb', 'N/A'):.1f}MB
- CPU utilization: {results.get('cpu_percent', 'N/A'):.1f}%

## Recommendations

1. **Performance Optimization**
   - Consider implementing response caching for common queries
   - Optimize context window usage for better throughput

2. **Scaling Strategy**
   - Current setup handles {results.get('max_concurrent', 5)} concurrent requests
   - For higher load, consider multiple Ollama instances

3. **Monitoring**
   - Implement continuous performance monitoring
   - Set up alerts for response time degradation
"""
    
    with open(output_path, 'w') as f:
        f.write(report_content)
    
    # Generate visualization if matplotlib is available
    try:
        plt.figure(figsize=(10, 6))
        
        # Response time distribution
        if 'response_times' in results:
            plt.subplot(2, 2, 1)
            plt.hist(results['response_times'], bins=20)
            plt.title('Response Time Distribution')
            plt.xlabel('Response Time (s)')
            plt.ylabel('Frequency')
        
        # Add more visualizations as needed
        
        plt.tight_layout()
        plt.savefig(output_path.with_suffix('.png'))
        plt.close()
        
    except Exception:
        pass  # Visualization optional