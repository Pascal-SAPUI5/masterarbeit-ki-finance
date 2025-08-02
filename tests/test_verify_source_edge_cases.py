#!/usr/bin/env python3
"""
Edge case tests for the verify_source method
Tests network issues, malformed data, and boundary conditions
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.citation_quality_control import CitationQualityControl

class TestVerifySourceEdgeCases:
    """Edge case tests for verify_source method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.qc = CitationQualityControl()
    
    def test_malformed_author_formats(self):
        """Test various malformed author formats."""
        test_cases = [
            {
                "title": "Test Paper",
                "authors": "",  # Empty string
                "year": "2023",
                "journal": "Test Journal"
            },
            {
                "title": "Test Paper", 
                "authors": [],  # Empty list
                "year": "2023",
                "journal": "Test Journal"
            },
            {
                "title": "Test Paper",
                "authors": [""],  # List with empty string
                "year": "2023", 
                "journal": "Test Journal"
            },
            {
                "title": "Test Paper",
                "authors": 123,  # Wrong type
                "year": "2023",
                "journal": "Test Journal"
            }
        ]
        
        for i, source in enumerate(test_cases):
            result = self.qc.verify_source(source)
            # Should handle malformed authors gracefully
            assert 'verified' in result, f"Test case {i}: Missing 'verified' key"
            assert 'issues' in result, f"Test case {i}: Missing 'issues' key"
    
    def test_year_boundary_conditions(self):
        """Test year validation boundary conditions."""
        test_cases = [
            ("1899", "Very old year"),
            ("2019", "Just before minimum"),
            ("2020", "Exact minimum"),
            ("2024", "Current valid year"),
            ("2025", "Current year"),
            ("2026", "Future year"),
            ("3000", "Far future"),
            ("abc", "Non-numeric"),
            ("20.23", "Decimal"),
            ("-2023", "Negative"),
            ("", "Empty string"),
        ]
        
        for year, description in test_cases:
            source = {
                "title": f"Test Paper {description}",
                "authors": ["Smith, J."],
                "year": year,
                "journal": "Test Journal"
            }
            
            result = self.qc.verify_source(source)
            assert isinstance(result, dict), f"Year {year}: Should return dict"
            assert 'verified' in result, f"Year {year}: Missing verified key"
            assert 'issues' in result, f"Year {year}: Missing issues key"
    
    def test_special_characters_in_fields(self):
        """Test handling of special characters."""
        source = {
            "title": "Test Paper with 特殊字符 and émojis 🔬",
            "authors": ["Müller, Hans", "José, María", "李, 明"],
            "year": "2023",
            "journal": "Журнал специальных символов & More"
        }
        
        result = self.qc.verify_source(source)
        assert result['verified'] in [True, False], "Should handle special characters"
        assert isinstance(result['issues'], list), "Issues should be a list"
    
    def test_extremely_long_fields(self):
        """Test handling of extremely long field values."""
        long_title = "A" * 10000  # Very long title
        long_author = "B" * 1000   # Very long author name
        
        source = {
            "title": long_title,
            "authors": [long_author],
            "year": "2023",
            "journal": "Test Journal"
        }
        
        result = self.qc.verify_source(source)
        assert isinstance(result, dict), "Should handle long fields gracefully"
        assert 'verified' in result, "Should still return verification status"
    
    def test_nested_data_structures(self):
        """Test handling of nested data in source fields."""
        source = {
            "title": "Test Paper",
            "authors": [{"name": "Smith", "affiliation": "University"}],  # Nested dict
            "year": {"value": "2023", "certainty": "high"},  # Nested object
            "journal": "Test Journal"
        }
        
        result = self.qc.verify_source(source)
        assert isinstance(result, dict), "Should handle nested structures"
        # Should treat non-string/non-list authors as invalid
    
    def test_none_and_null_values(self):
        """Test handling of None and null values."""
        source = {
            "title": None,
            "authors": None,
            "year": None,
            "journal": None
        }
        
        result = self.qc.verify_source(source)
        assert result['verified'] == False, "Should not verify source with None values"
        assert len(result['issues']) > 0, "Should have issues for None values"
    
    def test_case_sensitivity(self):
        """Test case sensitivity in journal names and quartiles."""
        test_cases = [
            {"journal": "journal of finance", "quartile": "q1"},  # lowercase
            {"journal": "JOURNAL OF FINANCE", "quartile": "Q1"},  # uppercase
            {"journal": "Journal Of Finance", "quartile": "Q1"},  # title case
        ]
        
        for case in test_cases:
            source = {
                "title": "Test Paper",
                "authors": ["Smith, J."],
                "year": "2023",
                **case
            }
            
            result = self.qc.verify_source(source)
            assert 'verified' in result, f"Case test failed for {case}"
    
    def test_memory_and_performance(self):
        """Test with many sources to check memory usage."""
        sources = []
        for i in range(100):
            sources.append({
                "title": f"Test Paper {i}",
                "authors": [f"Author{i}, Test"],
                "year": str(2020 + (i % 5)),
                "journal": f"Journal {i % 10}"
            })
        
        results = []
        for source in sources:
            result = self.qc.verify_source(source)
            results.append(result)
            assert isinstance(result, dict), f"Source {source['title']}: Should return dict"
        
        assert len(results) == 100, "Should process all 100 sources"
    
    def test_journal_matching_algorithms(self):
        """Test journal matching with slight variations."""
        base_source = {
            "title": "Test Paper",
            "authors": ["Smith, J."],
            "year": "2023"
        }
        
        # Test variations of known Q1 journals
        journal_variations = [
            "Journal of Finance",
            "The Journal of Finance",
            "Journal of Finance (JF)",
            "J. of Finance",
            "journal of finance",  # Case variation
        ]
        
        for journal in journal_variations:
            source = {**base_source, "journal": journal}
            result = self.qc.verify_source(source)
            # Should handle variations reasonably
            assert 'verified' in result, f"Journal variation failed: {journal}"
    
    def test_concurrent_access(self):
        """Test thread safety (basic test)."""
        import threading
        import time
        
        results = []
        errors = []
        
        def verify_source_thread(thread_id):
            try:
                source = {
                    "title": f"Test Paper {thread_id}",
                    "authors": [f"Author{thread_id}"],
                    "year": "2023",
                    "journal": "Test Journal"
                }
                result = self.qc.verify_source(source)
                results.append((thread_id, result))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=verify_source_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0, f"Concurrent access errors: {errors}"
        assert len(results) == 10, "Should complete all concurrent verifications"

def run_edge_case_tests():
    """Run all edge case tests manually."""
    test_class = TestVerifySourceEdgeCases()
    test_class.setup_method()
    
    print("🧪 Running edge case tests for verify_source method...")
    
    tests = [
        ("test_malformed_author_formats", test_class.test_malformed_author_formats),
        ("test_year_boundary_conditions", test_class.test_year_boundary_conditions),
        ("test_special_characters_in_fields", test_class.test_special_characters_in_fields),
        ("test_extremely_long_fields", test_class.test_extremely_long_fields),
        ("test_nested_data_structures", test_class.test_nested_data_structures),
        ("test_none_and_null_values", test_class.test_none_and_null_values),
        ("test_case_sensitivity", test_class.test_case_sensitivity),
        ("test_memory_and_performance", test_class.test_memory_and_performance),
        ("test_journal_matching_algorithms", test_class.test_journal_matching_algorithms),
        ("test_concurrent_access", test_class.test_concurrent_access),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"  Running {test_name}...", end=" ")
            test_func()
            print("✅")
            passed += 1
        except Exception as e:
            print(f"❌ - {str(e)}")
            failed += 1
    
    print(f"\n📊 Edge Case Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    success = run_edge_case_tests()
    exit(0 if success else 1)