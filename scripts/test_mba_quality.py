#!/usr/bin/env python3
"""
Test script for MBA Quality Checker
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from mba_quality_module import MBAQualityModule

def test_grammar_check():
    """Test grammar and spelling check functionality."""
    checker = MBAQualityModule()
    
    # Test text with intentional errors
    test_text = """
    Die digitale Transformation stellt Unternehmen vor neue Herausforderungen.
    Das ist ein Satz mit einem Rechtschreibfeler.
    Diese Arbeit untersucht die Implementierung von KI-Agenten in SAP BTP.
    """
    
    result = checker.check_grammar_spelling(test_text)
    print("Grammar Check Test:")
    print(f"Score: {result['score']}/100")
    print(f"Total errors: {result['total_errors']}")
    print(f"Grammar errors: {result['grammar_errors']}")
    print(f"Spelling errors: {result['spelling_errors']}")
    print("-" * 50)

def test_apa7_validation():
    """Test APA7 citation validation."""
    checker = MBAQualityModule()
    
    test_citations = [
        "(Smith, 2023)",  # Correct
        "(Miller & Johnson, 2022)",  # Correct
        "(Brown et al., 2021)",  # Correct
        "(Jones 2020)",  # Missing comma
        "(Lee and Park, 2023)",  # Should use &
        "(Kim et al, 2022)",  # Missing period after al
    ]
    
    print("\nAPA7 Citation Validation Test:")
    for citation in test_citations:
        result = checker.validate_apa7_citation(citation)
        print(f"\nCitation: {citation}")
        print(f"Valid: {result['valid']}")
        print(f"Score: {result['apa7_score']}/100")
        if result['format_issues']:
            print(f"Issues: {', '.join(result['format_issues'])}")
    print("-" * 50)

def test_literature_quality():
    """Test literature quality analysis."""
    checker = MBAQualityModule()
    
    # Sample references
    test_references = [
        {"authors": ["Smith, J."], "year": "2023", "title": "AI in Business", "journal": "MIS Quarterly", "quartile": "Q1", "doi": "10.1234/misq.2023.001"},
        {"authors": ["Brown, A."], "year": "2022", "title": "Digital Transformation", "journal": "Journal of Management Information Systems", "quartile": "Q1", "doi": "10.1234/jmis.2022.002"},
        {"authors": ["Lee, K."], "year": "2021", "title": "Enterprise AI", "journal": "Information Systems Research", "quartile": "Q1", "doi": "10.1234/isr.2021.003"},
        {"authors": ["Park, S."], "year": "2020", "title": "Cloud Computing", "journal": "Regular Journal", "doi": "10.1234/rj.2020.004"},
        {"authors": ["Kim, H."], "year": "2019", "title": "Legacy Systems", "journal": "Old Journal"},  # No DOI
    ]
    
    result = checker.analyze_literature_quality(test_references)
    print("\nLiterature Quality Analysis Test:")
    print(f"Total references: {result['total_references']}")
    print("\nQuality Metrics:")
    for metric, value in result['quality_metrics'].items():
        if isinstance(value, float):
            print(f"- {metric}: {value:.1f}%")
        else:
            print(f"- {metric}: {value}")
    print(f"\nOverall Literature Score: {result['overall_literature_score']:.1f}/5")
    print("-" * 50)

def test_theoretical_foundation():
    """Test theoretical foundation verification."""
    checker = MBAQualityModule()
    
    test_text = """
    This research employs the Technology-Organization-Environment (TOE) framework
    as the primary theoretical lens to examine SAP BTP adoption. The TOE framework,
    developed by Tornatzky and Fleischer (1990), provides a comprehensive approach
    to understanding technology adoption in organizations.
    
    Additionally, we integrate the Resource-Based View (RBV) theory to analyze
    how SAP BTP can serve as a strategic resource. The VRIO framework helps
    assess whether these capabilities provide sustainable competitive advantage.
    
    Dynamic Capabilities theory complements our analysis by explaining how
    organizations can adapt and reconfigure their resources in response to
    rapidly changing digital environments.
    """
    
    result = checker.verify_theoretical_foundation(test_text)
    print("\nTheoretical Foundation Test:")
    print(f"Has primary framework: {result['has_primary_framework']}")
    print(f"Frameworks found: {', '.join(result['frameworks_found'])}")
    print(f"Theory density: {result['theory_density']:.2f} theories/1000 words")
    print(f"Score: {result['score']}/100")
    print("-" * 50)

def test_overall_scoring():
    """Test overall MBA quality scoring."""
    checker = MBAQualityModule()
    
    # Simulate component scores
    grammar_score = 85
    citation_score = 90
    literature_score = 75
    theory_score = 80
    
    result = checker.calculate_overall_score(
        grammar_score=grammar_score,
        citation_score=citation_score,
        literature_score=literature_score,
        theory_score=theory_score
    )
    
    print("\nOverall MBA Quality Score Test:")
    print(f"Total Score: {result['total_score']:.1f}/100")
    print(f"Grade: {result['grade']}")
    print("\nCategory Breakdown:")
    for category, data in result['category_scores'].items():
        print(f"- {category}: {data['raw_score']:.1f}% (Weight: {data['weight']}%)")
    
    print("\nPriority Improvements:")
    for i, improvement in enumerate(result['priority_improvements'], 1):
        print(f"{i}. {improvement['category']}: {improvement['current_score']:.1f} → {improvement['target_score']} "
              f"(+{improvement['potential_point_gain']:.1f} points, Priority: {improvement['priority']})")

if __name__ == "__main__":
    print("MBA Quality Checker Test Suite")
    print("=" * 50)
    
    try:
        test_grammar_check()
    except Exception as e:
        print(f"Grammar check test failed: {e}")
    
    test_apa7_validation()
    test_literature_quality()
    test_theoretical_foundation()
    test_overall_scoring()
    
    print("\n✅ Test suite completed!")
    print("\nTo run a full quality check on a thesis file, use:")
    print("python scripts/mba_quality_checker.py --check-file <path> --full-report")