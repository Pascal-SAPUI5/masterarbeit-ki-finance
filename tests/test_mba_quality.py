#!/usr/bin/env python3
"""
MBA Quality Testing Module
Tests and validates the MBA quality control system for thesis evaluation
"""
import unittest
import json
from pathlib import Path
from typing import Dict, List, Tuple
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mba_quality_checker import MBAQualityChecker


class TestMBAQuality(unittest.TestCase):
    """Test cases for MBA quality evaluation system."""
    
    def setUp(self):
        """Set up test environment."""
        self.checker = MBAQualityChecker()
        self.test_data_dir = Path(__file__).parent / "test_data"
        self.test_data_dir.mkdir(exist_ok=True)
        
    def test_evaluation_criteria_weights(self):
        """Test that evaluation criteria weights sum to 1.0."""
        criteria = self.checker.config["evaluation_criteria"]
        total_weight = sum(criterion["weight"] for criterion in criteria.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2,
                               msg="Evaluation criteria weights must sum to 1.0")
        
    def test_evaluation_criteria_points(self):
        """Test that evaluation criteria points sum to 100."""
        criteria = self.checker.config["evaluation_criteria"]
        total_points = sum(criterion["total_points"] for criterion in criteria.values())
        self.assertEqual(total_points, 100,
                         msg="Evaluation criteria points must sum to 100")
        
    def test_subcriteria_weights(self):
        """Test that subcriteria weights match parent criteria."""
        criteria = self.checker.config["evaluation_criteria"]
        for name, criterion in criteria.items():
            if "aspects" in criterion:
                aspect_weight_sum = sum(aspect["weight"] for aspect in criterion["aspects"].values())
                self.assertAlmostEqual(aspect_weight_sum, criterion["weight"], places=2,
                                       msg=f"Subcriteria weights for {name} must match parent weight")
                
    def test_subcriteria_points(self):
        """Test that subcriteria points match parent criteria."""
        criteria = self.checker.config["evaluation_criteria"]
        for name, criterion in criteria.items():
            if "aspects" in criterion:
                aspect_points_sum = sum(aspect["points"] for aspect in criterion["aspects"].values())
                self.assertEqual(aspect_points_sum, criterion["total_points"],
                                 msg=f"Subcriteria points for {name} must match parent points")
                
    def test_grade_calculation_sehr_gut(self):
        """Test grade calculation for 'sehr gut' (90-100%)."""
        test_scores = {
            "aufbau_und_form": 18,  # 90% of 20
            "forschungsfrage_und_literatur": 27,  # 90% of 30
            "qualitaet_methodische_durchfuehrung": 36,  # 90% of 40
            "innovationsgrad_relevanz": 9  # 90% of 10
        }
        result = self.checker.calculate_grade(test_scores)
        self.assertEqual(result["total_points"], 90)
        self.assertEqual(result["percentage"], 90)
        self.assertEqual(result["grade_category"], "sehr_gut")
        self.assertIn(result["numeric_grade"], ["1.0", "1.3"])
        
    def test_grade_calculation_gut(self):
        """Test grade calculation for 'gut' (80-89%)."""
        test_scores = {
            "aufbau_und_form": 16,  # 80% of 20
            "forschungsfrage_und_literatur": 24,  # 80% of 30
            "qualitaet_methodische_durchfuehrung": 32,  # 80% of 40
            "innovationsgrad_relevanz": 8  # 80% of 10
        }
        result = self.checker.calculate_grade(test_scores)
        self.assertEqual(result["total_points"], 80)
        self.assertEqual(result["percentage"], 80)
        self.assertEqual(result["grade_category"], "gut")
        self.assertIn(result["numeric_grade"], ["1.7", "2.0", "2.3"])
        
    def test_grade_calculation_befriedigend(self):
        """Test grade calculation for 'befriedigend' (70-79%)."""
        test_scores = {
            "aufbau_und_form": 14,  # 70% of 20
            "forschungsfrage_und_literatur": 21,  # 70% of 30
            "qualitaet_methodische_durchfuehrung": 28,  # 70% of 40
            "innovationsgrad_relevanz": 7  # 70% of 10
        }
        result = self.checker.calculate_grade(test_scores)
        self.assertEqual(result["total_points"], 70)
        self.assertEqual(result["percentage"], 70)
        self.assertEqual(result["grade_category"], "befriedigend")
        self.assertIn(result["numeric_grade"], ["2.7", "3.0", "3.3"])
        
    def test_grade_calculation_ausreichend(self):
        """Test grade calculation for 'ausreichend' (60-69%)."""
        test_scores = {
            "aufbau_und_form": 12,  # 60% of 20
            "forschungsfrage_und_literatur": 18,  # 60% of 30
            "qualitaet_methodische_durchfuehrung": 24,  # 60% of 40
            "innovationsgrad_relevanz": 6  # 60% of 10
        }
        result = self.checker.calculate_grade(test_scores)
        self.assertEqual(result["total_points"], 60)
        self.assertEqual(result["percentage"], 60)
        self.assertEqual(result["grade_category"], "ausreichend")
        self.assertIn(result["numeric_grade"], ["3.7", "4.0"])
        
    def test_grade_calculation_nicht_ausreichend(self):
        """Test grade calculation for 'nicht ausreichend' (0-59%)."""
        test_scores = {
            "aufbau_und_form": 10,  # 50% of 20
            "forschungsfrage_und_literatur": 15,  # 50% of 30
            "qualitaet_methodische_durchfuehrung": 20,  # 50% of 40
            "innovationsgrad_relevanz": 5  # 50% of 10
        }
        result = self.checker.calculate_grade(test_scores)
        self.assertEqual(result["total_points"], 50)
        self.assertEqual(result["percentage"], 50)
        self.assertEqual(result["grade_category"], "nicht_ausreichend")
        self.assertEqual(result["numeric_grade"], "5.0")
        
    def test_literature_quality_sehr_gut(self):
        """Test literature quality assessment for 'sehr gut'."""
        test_literature = {
            "aktualitaet": 95,  # >90% from 2020+
            "q1_percentage": 85,  # >80% Q1 journals
            "internationalitaet": {"US": 35, "EU": 35, "Other": 30},  # Balanced
            "doi_coverage": 100,  # 100% DOI coverage
            "methodology": "Systematic and transparent"
        }
        score = self.checker.assess_literature_quality(test_literature)
        self.assertEqual(score["points"], 5)
        self.assertEqual(score["category"], "sehr_gut_5_punkte")
        
    def test_literature_quality_gut(self):
        """Test literature quality assessment for 'gut'."""
        test_literature = {
            "aktualitaet": 75,  # >70% from 2020+
            "q1_percentage": 65,  # >60% Q1 journals
            "internationalitaet": {"US": 40, "EU": 40, "Other": 20},  # Good distribution
            "doi_coverage": 92,  # >90% DOI coverage
            "methodology": "Structured and justified"
        }
        score = self.checker.assess_literature_quality(test_literature)
        self.assertEqual(score["points"], 4)
        self.assertEqual(score["category"], "gut_4_punkte")
        
    def test_literature_quality_befriedigend(self):
        """Test literature quality assessment for 'befriedigend'."""
        test_literature = {
            "aktualitaet": 55,  # >50% from 2020+
            "q1_percentage": 45,  # >40% Q1 journals
            "internationalitaet": {"US": 60, "EU": 30, "Other": 10},  # Regional focus
            "doi_coverage": 82,  # >80% DOI coverage
            "methodology": "Basic systematic approach"
        }
        score = self.checker.assess_literature_quality(test_literature)
        self.assertEqual(score["points"], 3)
        self.assertEqual(score["category"], "befriedigend_3_punkte")
        
    def test_detailed_scoring(self):
        """Test detailed scoring for individual aspects."""
        detailed_scores = {
            "schluessigkeit_aufbau": 4.5,  # out of 5
            "formale_praesentation": 6.0,  # out of 7
            "nachvollziehbarkeit_quellen": 7.0,  # out of 8
            "breite_literatur": 8.5,  # out of 10
            "meta_problemstellung": 17.0,  # out of 20
            "durchfuehrung_methodik": 18.0,  # out of 20
            "qualitaet_empirische_ergebnisse": 16.0,  # out of 20
            "innovationsgrad_nutzen": 4.0,  # out of 5
            "selbstaendigkeit_originalitaet": 4.0  # out of 5
        }
        result = self.checker.calculate_detailed_grade(detailed_scores)
        
        # Verify category scores
        self.assertAlmostEqual(result["categories"]["aufbau_und_form"], 17.5, places=1)
        self.assertAlmostEqual(result["categories"]["forschungsfrage_und_literatur"], 25.5, places=1)
        self.assertAlmostEqual(result["categories"]["qualitaet_methodische_durchfuehrung"], 34.0, places=1)
        self.assertAlmostEqual(result["categories"]["innovationsgrad_relevanz"], 8.0, places=1)
        
        # Verify total
        self.assertAlmostEqual(result["total_points"], 85.0, places=1)
        self.assertEqual(result["grade_category"], "gut")
        
    def test_generate_quality_report(self):
        """Test generation of comprehensive quality report."""
        test_scores = {
            "aufbau_und_form": {
                "score": 17,
                "details": {
                    "schluessigkeit_aufbau": 4.5,
                    "formale_praesentation": 5.5,
                    "nachvollziehbarkeit_quellen": 7.0
                }
            },
            "forschungsfrage_und_literatur": {
                "score": 25,
                "details": {
                    "breite_literatur": 8.0,
                    "meta_problemstellung": 17.0
                }
            },
            "qualitaet_methodische_durchfuehrung": {
                "score": 32,
                "details": {
                    "durchfuehrung_methodik": 16.0,
                    "qualitaet_empirische_ergebnisse": 16.0
                }
            },
            "innovationsgrad_relevanz": {
                "score": 8,
                "details": {
                    "innovationsgrad_nutzen": 4.0,
                    "selbstaendigkeit_originalitaet": 4.0
                }
            }
        }
        
        literature_stats = {
            "total_sources": 120,
            "aktualitaet": 75,
            "q1_percentage": 65,
            "doi_coverage": 92,
            "international_distribution": {"US": 40, "EU": 35, "Other": 25}
        }
        
        report = self.checker.generate_quality_report(test_scores, literature_stats)
        
        # Verify report structure
        self.assertIn("summary", report)
        self.assertIn("detailed_evaluation", report)
        self.assertIn("literature_quality", report)
        self.assertIn("recommendations", report)
        self.assertIn("grade_breakdown", report)
        
        # Verify calculations
        self.assertEqual(report["summary"]["total_points"], 82)
        self.assertEqual(report["summary"]["grade_category"], "gut")
        
    def test_boundary_conditions(self):
        """Test edge cases and boundary conditions."""
        # Test minimum passing score
        min_passing = {
            "aufbau_und_form": 12,
            "forschungsfrage_und_literatur": 18,
            "qualitaet_methodische_durchfuehrung": 24,
            "innovationsgrad_relevanz": 6
        }
        result = self.checker.calculate_grade(min_passing)
        self.assertEqual(result["grade_category"], "ausreichend")
        
        # Test boundary between grades
        boundary_scores = [
            (89.5, "gut"),  # Just below sehr gut
            (79.5, "befriedigend"),  # Just below gut
            (69.5, "ausreichend"),  # Just below befriedigend
            (59.5, "nicht_ausreichend")  # Just below ausreichend
        ]
        
        for score, expected_grade in boundary_scores:
            test_scores = self._create_scores_for_percentage(score)
            result = self.checker.calculate_grade(test_scores)
            self.assertEqual(result["grade_category"], expected_grade,
                             f"Score {score}% should be graded as {expected_grade}")
            
    def test_missing_scores_handling(self):
        """Test handling of missing or invalid scores."""
        # Missing category
        incomplete_scores = {
            "aufbau_und_form": 18,
            "forschungsfrage_und_literatur": 27,
            "qualitaet_methodische_durchfuehrung": 36
            # Missing innovationsgrad_relevanz
        }
        
        with self.assertRaises(ValueError) as context:
            self.checker.calculate_grade(incomplete_scores)
        self.assertIn("Missing required category", str(context.exception))
        
        # Invalid score (exceeds maximum)
        invalid_scores = {
            "aufbau_und_form": 25,  # Exceeds max of 20
            "forschungsfrage_und_literatur": 27,
            "qualitaet_methodische_durchfuehrung": 36,
            "innovationsgrad_relevanz": 9
        }
        
        with self.assertRaises(ValueError) as context:
            self.checker.calculate_grade(invalid_scores)
        self.assertIn("exceeds maximum", str(context.exception))
        
    def test_improvement_recommendations(self):
        """Test generation of improvement recommendations."""
        weak_scores = {
            "aufbau_und_form": 10,  # 50% - needs improvement
            "forschungsfrage_und_literatur": 18,  # 60% - acceptable
            "qualitaet_methodische_durchfuehrung": 20,  # 50% - needs improvement
            "innovationsgrad_relevanz": 7  # 70% - good
        }
        
        recommendations = self.checker.generate_recommendations(weak_scores)
        
        # Should recommend improvements for weak areas
        self.assertIn("aufbau_und_form", recommendations["priority_improvements"])
        self.assertIn("qualitaet_methodische_durchfuehrung", recommendations["priority_improvements"])
        
        # Should acknowledge strong areas
        self.assertIn("innovationsgrad_relevanz", recommendations["strengths"])
        
        # Should estimate potential grade improvement
        self.assertGreater(recommendations["potential_grade_improvement"], 0)
        
    def _create_scores_for_percentage(self, percentage: float) -> Dict[str, float]:
        """Helper to create scores that result in a specific percentage."""
        return {
            "aufbau_und_form": 20 * (percentage / 100),
            "forschungsfrage_und_literatur": 30 * (percentage / 100),
            "qualitaet_methodische_durchfuehrung": 40 * (percentage / 100),
            "innovationsgrad_relevanz": 10 * (percentage / 100)
        }
        

class TestLiteratureQualityAnalysis(unittest.TestCase):
    """Test literature quality analysis functionality."""
    
    def setUp(self):
        self.checker = MBAQualityChecker()
        
    def test_journal_quartile_detection(self):
        """Test detection of journal quartiles."""
        test_cases = [
            ("Nature", "Q1"),
            ("MIS Quarterly", "Q1"),
            ("Journal of Finance", "Q1"),
            ("Unknown Journal", None)
        ]
        
        for journal, expected_quartile in test_cases:
            result = self.checker.detect_journal_quartile(journal)
            self.assertEqual(result, expected_quartile,
                             f"Journal {journal} should be detected as {expected_quartile}")
            
    def test_publication_year_analysis(self):
        """Test analysis of publication years."""
        test_references = [
            {"year": "2024", "title": "Recent study"},
            {"year": "2023", "title": "Current research"},
            {"year": "2022", "title": "Recent work"},
            {"year": "2021", "title": "Established research"},
            {"year": "2020", "title": "Foundation work"},
            {"year": "2019", "title": "Older study"},
            {"year": "2018", "title": "Classical work"}
        ]
        
        analysis = self.checker.analyze_publication_years(test_references)
        
        self.assertAlmostEqual(analysis["percentage_2020_plus"], 71.4, places=1)
        self.assertAlmostEqual(analysis["percentage_2022_plus"], 42.9, places=1)
        self.assertEqual(analysis["newest_year"], 2024)
        self.assertEqual(analysis["oldest_year"], 2018)
        
    def test_geographic_distribution(self):
        """Test analysis of geographic distribution."""
        test_references = [
            {"authors": ["Smith, J."], "affiliation": "Harvard University, USA"},
            {"authors": ["Mueller, K."], "affiliation": "University of Munich, Germany"},
            {"authors": ["Chen, L."], "affiliation": "Tsinghua University, China"},
            {"authors": ["Johnson, M."], "affiliation": "MIT, USA"},
            {"authors": ["Dubois, P."], "affiliation": "Sorbonne, France"}
        ]
        
        distribution = self.checker.analyze_geographic_distribution(test_references)
        
        self.assertEqual(distribution["US"], 40)
        self.assertEqual(distribution["EU"], 40)
        self.assertEqual(distribution["Other"], 20)
        self.assertTrue(distribution["is_balanced"])
        

class TestQualityReportGeneration(unittest.TestCase):
    """Test quality report generation."""
    
    def setUp(self):
        self.checker = MBAQualityChecker()
        self.output_dir = Path(__file__).parent / "test_output"
        self.output_dir.mkdir(exist_ok=True)
        
    def test_sample_quality_report(self):
        """Generate a sample quality report demonstrating all features."""
        # Create comprehensive test data
        sample_evaluation = {
            "thesis_title": "Implementierung von Agentic Workflows mit SAP BTP: Eine empirische Analyse der Effizienzgewinne durch KI-gestützte Automatisierung unter Berücksichtigung des EU AI Acts",
            "author": "Test Student",
            "date": "2025-01-27",
            "scores": {
                "aufbau_und_form": {
                    "total": 17.5,
                    "breakdown": {
                        "schluessigkeit_aufbau": {"score": 4.5, "max": 5, "comments": "Sehr gute Strukturierung mit klarem rotem Faden"},
                        "formale_praesentation": {"score": 6.0, "max": 7, "comments": "Einige kleinere Formatierungsfehler"},
                        "nachvollziehbarkeit_quellen": {"score": 7.0, "max": 8, "comments": "Korrekte Zitierweise, vereinzelt fehlende Seitenzahlen"}
                    }
                },
                "forschungsfrage_und_literatur": {
                    "total": 26.0,
                    "breakdown": {
                        "breite_literatur": {"score": 8.5, "max": 10, "comments": "Sehr gute Literaturbreite, könnte mehr Q1-Journals nutzen"},
                        "meta_problemstellung": {"score": 17.5, "max": 20, "comments": "Präzise formulierte Forschungsfrage mit hoher Relevanz"}
                    }
                },
                "qualitaet_methodische_durchfuehrung": {
                    "total": 34.0,
                    "breakdown": {
                        "durchfuehrung_methodik": {"score": 17.0, "max": 20, "comments": "Solide Methodik, Stichprobengröße könnte größer sein"},
                        "qualitaet_empirische_ergebnisse": {"score": 17.0, "max": 20, "comments": "Gute Ergebnispräsentation mit klaren Handlungsempfehlungen"}
                    }
                },
                "innovationsgrad_relevanz": {
                    "total": 8.5,
                    "breakdown": {
                        "innovationsgrad_nutzen": {"score": 4.5, "max": 5, "comments": "Hoher Innovationsgrad durch Kombination von SAP BTP und Agentic AI"},
                        "selbstaendigkeit_originalitaet": {"score": 4.0, "max": 5, "comments": "Eigenständige Herangehensweise mit kritischer Reflexion"}
                    }
                }
            },
            "literature_analysis": {
                "total_sources": 145,
                "quality_metrics": {
                    "aktualitaet": {
                        "2020_plus": 78,
                        "2022_plus": 45,
                        "2024_2025": 12
                    },
                    "journal_quality": {
                        "q1_journals": 68,
                        "q2_journals": 22,
                        "other": 10
                    },
                    "geographic_distribution": {
                        "US": 38,
                        "EU": 35,
                        "Asia": 20,
                        "Other": 7
                    },
                    "doi_coverage": 94,
                    "open_access": 42
                },
                "top_journals": [
                    {"name": "MIS Quarterly", "count": 8, "impact_factor": 7.92},
                    {"name": "Journal of Strategic Information Systems", "count": 6, "impact_factor": 6.0},
                    {"name": "Information Systems Research", "count": 5, "impact_factor": 5.8}
                ],
                "theoretical_frameworks": [
                    {"name": "TOE Framework", "usage_count": 15},
                    {"name": "RBV Theory", "usage_count": 12},
                    {"name": "Dynamic Capabilities", "usage_count": 10}
                ]
            }
        }
        
        # Generate the report
        report = self.checker.generate_comprehensive_report(sample_evaluation)
        
        # Save report as JSON
        report_path = self.output_dir / "sample_mba_quality_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        # Generate HTML report
        html_report = self.checker.generate_html_report(report)
        html_path = self.output_dir / "sample_mba_quality_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
            
        # Verify report completeness
        self.assertIn("executive_summary", report)
        self.assertIn("detailed_evaluation", report)
        self.assertIn("literature_quality_assessment", report)
        self.assertIn("final_grade", report)
        self.assertIn("recommendations", report)
        
        # Verify grade calculation
        self.assertEqual(report["final_grade"]["total_points"], 86)
        self.assertEqual(report["final_grade"]["percentage"], 86)
        self.assertEqual(report["final_grade"]["grade_category"], "gut")
        self.assertIn(report["final_grade"]["numeric_grade"], ["1.7", "2.0"])
        
        print(f"\nSample quality report generated:")
        print(f"  JSON: {report_path}")
        print(f"  HTML: {html_path}")
        print(f"\nFinal Grade: {report['final_grade']['numeric_grade']} ({report['final_grade']['grade_category']})")
        print(f"Total Points: {report['final_grade']['total_points']}/100")
        

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)