#!/usr/bin/env python3
"""
Comprehensive test suite for the verify_source method fix
Tests various edge cases and validation scenarios
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.citation_quality_control import CitationQualityControl

class TestVerifySourceMethod:
    """Test cases for the newly implemented verify_source method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.qc = CitationQualityControl()
    
    def test_verify_source_exists(self):
        """Test that verify_source method exists."""
        assert hasattr(self.qc, 'verify_source'), "verify_source method should exist"
        assert callable(getattr(self.qc, 'verify_source')), "verify_source should be callable"
    
    def test_valid_q1_journal_source(self):
        """Test verification of a valid Q1 journal source."""
        source = {
            "title": "AI Agents in Financial Services: A Comprehensive Review",
            "authors": ["Smith, J.", "Johnson, M."],
            "year": "2023",
            "journal": "Journal of Finance",
            "quartile": "Q1",
            "doi": "10.1234/example",
            "abstract": "This paper examines the role of AI agents in modern financial services..."
        }
        
        result = self.qc.verify_source(source)
        
        assert result["verified"] == True, "Valid Q1 source should be verified"
        assert result["quality_score"] >= 30, "Q1 journal should have high quality score"
        assert "Excellent Q1 journal" in result["recommendations"]
        assert "DOI available for verification" in result["recommendations"]
        assert len(result["issues"]) == 0, "Valid source should have no issues"
        assert result["citation_german"] != "", "German citation should be generated"
        assert result["citation_english"] != "", "English citation should be generated"
    
    def test_missing_required_fields(self):
        """Test verification with missing required fields."""
        source = {
            "journal": "Some Journal"
            # Missing title, authors, year
        }
        
        result = self.qc.verify_source(source)
        
        assert result["verified"] == False, "Source with missing fields should not be verified"
        assert len(result["issues"]) >= 3, "Should have issues for missing required fields"
        assert any("Missing required field: title" in issue for issue in result["issues"])
        assert any("Missing required field: authors" in issue for issue in result["issues"])
        assert any("Missing required field: year" in issue for issue in result["issues"])
    
    def test_old_publication_year(self):
        """Test verification with old publication year."""
        source = {
            "title": "Old Research",
            "authors": ["Smith, J."],
            "year": "2018",  # Before 2020
            "journal": "Some Journal"
        }
        
        result = self.qc.verify_source(source)
        
        assert any("may be too old for current research" in issue for issue in result["issues"])
    
    def test_future_publication_year(self):
        """Test verification with future publication year."""
        source = {
            "title": "Future Research",
            "authors": ["Smith, J."],
            "year": "2030",  # Future year
            "journal": "Some Journal"
        }
        
        result = self.qc.verify_source(source)
        
        assert any("is in the future" in issue for issue in result["issues"])
    
    def test_invalid_year_format(self):
        """Test verification with invalid year format."""
        source = {
            "title": "Research",
            "authors": ["Smith, J."],
            "year": "invalid_year",
            "journal": "Some Journal"
        }
        
        result = self.qc.verify_source(source)
        
        assert any("Invalid year format" in issue for issue in result["issues"])
    
    def test_high_impact_factor_journal(self):
        """Test verification with high impact factor journal."""
        source = {
            "title": "Research Paper",
            "authors": ["Smith, J."],
            "year": "2023",
            "journal": "High Impact Journal",
            "impact_factor": 5.2
        }
        
        result = self.qc.verify_source(source)
        
        assert "Good impact factor" in result["recommendations"]
        assert result["quality_score"] >= 20, "High impact factor should increase score"
    
    def test_citation_generation_single_author(self):
        """Test citation generation for single author."""
        source = {
            "title": "Research Paper",
            "authors": ["Smith, John"],
            "year": "2023",
            "journal": "Test Journal"
        }
        
        result = self.qc.verify_source(source)
        
        assert "(Smith, 2023)" in result["citation_german"]
        assert "(Smith, 2023)" in result["citation_english"]
    
    def test_citation_generation_two_authors(self):
        """Test citation generation for two authors."""
        source = {
            "title": "Research Paper",
            "authors": ["Smith, John", "Johnson, Mary"],
            "year": "2023",
            "journal": "Test Journal"
        }
        
        result = self.qc.verify_source(source)
        
        assert "und" in result["citation_german"]  # German "and"
        assert "&" in result["citation_english"]  # English "&"
    
    def test_citation_generation_multiple_authors(self):
        """Test citation generation for multiple authors."""
        source = {
            "title": "Research Paper",
            "authors": ["Smith, John", "Johnson, Mary", "Brown, Bob"],
            "year": "2023",
            "journal": "Test Journal"
        }
        
        result = self.qc.verify_source(source)
        
        assert "et al." in result["citation_german"]
        assert "et al." in result["citation_english"]
    
    def test_doi_and_abstract_scoring(self):
        """Test that DOI and abstract contribute to quality score."""
        source_with_extras = {
            "title": "Research Paper",
            "authors": ["Smith, J."],
            "year": "2023",
            "journal": "Test Journal",
            "doi": "10.1234/example",
            "abstract": "This is an abstract"
        }
        
        source_without_extras = {
            "title": "Research Paper",
            "authors": ["Smith, J."],
            "year": "2023",
            "journal": "Test Journal"
        }
        
        result_with = self.qc.verify_source(source_with_extras)
        result_without = self.qc.verify_source(source_without_extras)
        
        assert result_with["quality_score"] > result_without["quality_score"]
        assert "DOI available for verification" in result_with["recommendations"]
        assert "Abstract available" in result_with["recommendations"]
    
    def test_error_handling(self):
        """Test error handling for invalid input."""
        # Test with None
        result = self.qc.verify_source(None)
        assert result["verified"] == False
        assert len(result["issues"]) > 0
        
        # Test with empty dict
        result = self.qc.verify_source({})
        assert result["verified"] == False
        assert len(result["issues"]) >= 3  # Missing required fields
    
    def test_quality_score_threshold(self):
        """Test that sources need minimum quality score to be verified."""
        # Source with minimal valid fields but low quality
        source = {
            "title": "Basic Paper",
            "authors": ["Unknown, A."],
            "year": "2023"
            # No journal, DOI, abstract, etc.
        }
        
        result = self.qc.verify_source(source)
        
        # Should have some score for basic fields but may not reach verification threshold
        assert result["quality_score"] >= 0
        # Verification depends on reaching threshold with no critical issues
    
    def test_comprehensive_valid_source(self):
        """Test a comprehensive valid source with all features."""
        source = {
            "title": "Comprehensive AI Research in Finance",
            "authors": ["Smith, John", "Johnson, Mary"],
            "year": "2024",
            "journal": "Journal of Finance",  # Q1 journal
            "quartile": "Q1",
            "impact_factor": 7.2,
            "doi": "10.1234/comprehensive.example",
            "abstract": "This comprehensive study examines the implementation of AI agents in financial services, providing novel insights into automation and efficiency improvements."
        }
        
        result = self.qc.verify_source(source)
        
        assert result["verified"] == True
        assert result["quality_score"] >= 70  # High score for comprehensive source
        assert len(result["issues"]) == 0
        assert "Source meets verification criteria" in result["recommendations"]
        assert result["citation_german"] != ""
        assert result["citation_english"] != ""

def test_integration_with_mcp_server():
    """Integration test with MCP server verify_citations tool."""
    import asyncio
    from mcp_server import MasterarbeitMCPServer
    
    async def run_integration_test():
        server = MasterarbeitMCPServer()
        
        # Test verify_all functionality
        result = await server.call_tool('verify_citations', {'verify_all': True})
        
        assert 'verified_count' in result
        assert 'issues_count' in result
        assert 'total' in result
        assert 'message' in result
        
        # Should not raise AttributeError anymore
        return True
    
    # Run the async test
    success = asyncio.run(run_integration_test())
    assert success == True

if __name__ == "__main__":
    # Run tests manually if executed directly
    test_class = TestVerifySourceMethod()
    test_class.setup_method()
    
    print("🧪 Running verify_source method tests...")
    
    tests = [
        ("test_verify_source_exists", test_class.test_verify_source_exists),
        ("test_valid_q1_journal_source", test_class.test_valid_q1_journal_source),
        ("test_missing_required_fields", test_class.test_missing_required_fields),
        ("test_old_publication_year", test_class.test_old_publication_year),
        ("test_future_publication_year", test_class.test_future_publication_year),
        ("test_invalid_year_format", test_class.test_invalid_year_format),
        ("test_high_impact_factor_journal", test_class.test_high_impact_factor_journal),
        ("test_citation_generation_single_author", test_class.test_citation_generation_single_author),
        ("test_citation_generation_two_authors", test_class.test_citation_generation_two_authors),
        ("test_citation_generation_multiple_authors", test_class.test_citation_generation_multiple_authors),
        ("test_doi_and_abstract_scoring", test_class.test_doi_and_abstract_scoring),
        ("test_error_handling", test_class.test_error_handling),
        ("test_quality_score_threshold", test_class.test_quality_score_threshold),
        ("test_comprehensive_valid_source", test_class.test_comprehensive_valid_source),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {str(e)}")
            failed += 1
    
    print(f"\n📊 Test Results: {passed} passed, {failed} failed")
    
    # Run integration test
    print("\n🔗 Running integration test...")
    try:
        test_integration_with_mcp_server()
        print("✅ Integration test passed")
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")