#!/usr/bin/env python3
"""
MBA Quality Control System - Demonstration
Shows all features of the MBA quality evaluation system
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.mba_quality_checker import MBAQualityChecker


def demonstrate_mba_quality_system():
    """Demonstrate all features of the MBA quality system."""
    print("\n" + "="*60)
    print("MBA QUALITY CONTROL SYSTEM - DEMONSTRATION")
    print("="*60 + "\n")
    
    checker = MBAQualityChecker()
    
    # 1. Demonstrate grade calculation
    print("1. GRADE CALCULATION DEMONSTRATION")
    print("-" * 40)
    
    test_scenarios = [
        {
            "name": "Exzellente Arbeit",
            "scores": {
                "aufbau_und_form": 19,
                "forschungsfrage_und_literatur": 28,
                "qualitaet_methodische_durchfuehrung": 37,
                "innovationsgrad_relevanz": 9
            }
        },
        {
            "name": "Durchschnittliche Arbeit",
            "scores": {
                "aufbau_und_form": 14,
                "forschungsfrage_und_literatur": 21,
                "qualitaet_methodische_durchfuehrung": 28,
                "innovationsgrad_relevanz": 7
            }
        }
    ]
    
    for scenario in test_scenarios:
        result = checker.calculate_grade(scenario["scores"])
        print(f"\n{scenario['name']}:")
        print(f"  Total Points: {result['total_points']}/100")
        print(f"  Percentage: {result['percentage']}%")
        print(f"  Grade: {result['numeric_grade']} ({result['grade_category']})")
        print(f"  Description: {result['description'][:50]}...")
    
    # 2. Demonstrate literature quality assessment
    print("\n\n2. LITERATURE QUALITY ASSESSMENT")
    print("-" * 40)
    
    literature_examples = [
        {
            "name": "High-Quality Literature",
            "stats": {
                "aktualitaet": 85,
                "q1_percentage": 75,
                "doi_coverage": 95,
                "internationalitaet": {"US": 35, "EU": 40, "Other": 25}
            }
        },
        {
            "name": "Average Literature",
            "stats": {
                "aktualitaet": 45,
                "q1_percentage": 35,
                "doi_coverage": 70,
                "internationalitaet": {"US": 70, "EU": 20, "Other": 10}
            }
        }
    ]
    
    for example in literature_examples:
        result = checker.assess_literature_quality(example["stats"])
        print(f"\n{example['name']}:")
        print(f"  Category: {result['category']}")
        print(f"  Points: {result['points']}/5")
        print(f"  Metrics:")
        for key, value in result['metrics'].items():
            print(f"    - {key}: {value}")
    
    # 3. Demonstrate detailed scoring
    print("\n\n3. DETAILED SCORING BREAKDOWN")
    print("-" * 40)
    
    detailed_scores = {
        "schluessigkeit_aufbau": 4.2,
        "formale_praesentation": 5.8,
        "nachvollziehbarkeit_quellen": 6.5,
        "breite_literatur": 8.0,
        "meta_problemstellung": 16.5,
        "durchfuehrung_methodik": 16.0,
        "qualitaet_empirische_ergebnisse": 15.5,
        "innovationsgrad_nutzen": 4.0,
        "selbstaendigkeit_originalitaet": 3.5
    }
    
    result = checker.calculate_detailed_grade(detailed_scores)
    print("\nDetailed Aspect Scores:")
    for aspect, score in detailed_scores.items():
        print(f"  {aspect.replace('_', ' ').title()}: {score}")
    
    print("\nCategory Totals:")
    for category, score in result['categories'].items():
        print(f"  {category.replace('_', ' ').title()}: {score}")
    
    print(f"\nFinal Grade: {result['numeric_grade']} ({result['total_points']}/100 points)")
    
    # 4. Demonstrate recommendation generation
    print("\n\n4. IMPROVEMENT RECOMMENDATIONS")
    print("-" * 40)
    
    weak_scores = {
        "aufbau_und_form": 11,  # 55% - needs improvement
        "forschungsfrage_und_literatur": 18,  # 60% - borderline
        "qualitaet_methodische_durchfuehrung": 22,  # 55% - needs improvement
        "innovationsgrad_relevanz": 7.5  # 75% - good
    }
    
    recommendations = checker.generate_recommendations(weak_scores)
    
    print("\nStrengths:")
    for strength in recommendations['strengths']:
        print(f"  ✓ {strength}")
    
    print("\nPriority Improvements:")
    for improvement in recommendations['priority_improvements']:
        print(f"  ⚠ {improvement}")
    
    print("\nSpecific Recommendations:")
    for rec in recommendations['specific_recommendations']:
        print(f"\n  {rec['category']}:")
        for action in rec['actions']:
            print(f"    - {action}")
        print(f"    Potential improvement: +{rec['potential_points']:.1f} points")
    
    print(f"\nEstimated Effort:")
    effort = recommendations['estimated_effort']
    print(f"  Total hours: {effort['total_hours']}")
    print(f"  Weeks needed: {effort['weeks_needed']:.1f}")
    print(f"  Difficulty: {effort['difficulty']}")
    
    # 5. Generate sample full evaluation
    print("\n\n5. FULL EVALUATION REPORT GENERATION")
    print("-" * 40)
    
    sample_data = {
        "thesis_title": "Implementierung von Agentic Workflows mit SAP BTP",
        "author": "Demo Student",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "scores": {
            "aufbau_und_form": {
                "total": 16.5,
                "breakdown": {
                    "schluessigkeit_aufbau": {
                        "score": 4.0,
                        "max": 5,
                        "comments": "Gute Strukturierung, kleine Verbesserungen möglich"
                    },
                    "formale_praesentation": {
                        "score": 5.5,
                        "max": 7,
                        "comments": "Einige Formatierungsfehler und Tippfehler"
                    },
                    "nachvollziehbarkeit_quellen": {
                        "score": 7.0,
                        "max": 8,
                        "comments": "Sehr gute Zitierweise"
                    }
                }
            },
            "forschungsfrage_und_literatur": {
                "total": 24.5,
                "breakdown": {
                    "breite_literatur": {
                        "score": 8.0,
                        "max": 10,
                        "comments": "Gute Literaturauswahl, mehr aktuelle Quellen wünschenswert"
                    },
                    "meta_problemstellung": {
                        "score": 16.5,
                        "max": 20,
                        "comments": "Klar formulierte Forschungsfrage"
                    }
                }
            },
            "qualitaet_methodische_durchfuehrung": {
                "total": 31.5,
                "breakdown": {
                    "durchfuehrung_methodik": {
                        "score": 16.0,
                        "max": 20,
                        "comments": "Solide Methodik, Stichprobe könnte größer sein"
                    },
                    "qualitaet_empirische_ergebnisse": {
                        "score": 15.5,
                        "max": 20,
                        "comments": "Gute Ergebnisdarstellung"
                    }
                }
            },
            "innovationsgrad_relevanz": {
                "total": 8.0,
                "breakdown": {
                    "innovationsgrad_nutzen": {
                        "score": 4.0,
                        "max": 5,
                        "comments": "Hohe praktische Relevanz"
                    },
                    "selbstaendigkeit_originalitaet": {
                        "score": 4.0,
                        "max": 5,
                        "comments": "Eigenständige Herangehensweise"
                    }
                }
            }
        },
        "literature_analysis": {
            "total_sources": 125,
            "quality_metrics": {
                "aktualitaet": {
                    "2020_plus": 72,
                    "2022_plus": 38,
                    "2024_2025": 8
                },
                "journal_quality": {
                    "q1_journals": 62,
                    "q2_journals": 25,
                    "other": 13
                },
                "geographic_distribution": {
                    "US": 42,
                    "EU": 38,
                    "Other": 20
                },
                "doi_coverage": 89,
                "open_access": 35
            },
            "top_journals": [
                {"name": "MIS Quarterly", "count": 6, "impact_factor": 7.92},
                {"name": "Information Systems Research", "count": 4, "impact_factor": 5.8},
                {"name": "Journal of Strategic Information Systems", "count": 4, "impact_factor": 6.0}
            ],
            "theoretical_frameworks": [
                {"name": "TOE Framework", "usage_count": 12},
                {"name": "RBV Theory", "usage_count": 8},
                {"name": "Dynamic Capabilities", "usage_count": 6}
            ]
        }
    }
    
    report = checker.generate_comprehensive_report(sample_data)
    
    print("\nGenerated Comprehensive Report:")
    print(f"  Final Grade: {report['final_grade']['numeric_grade']} ({report['final_grade']['grade_category']})")
    print(f"  Total Points: {report['final_grade']['total_points']}/100")
    print(f"  Literature Quality: {report['literature_quality_assessment']['score']['category']}")
    print(f"  Meets MBA Standards: {report['quality_indicators']['meets_mba_standards']}")
    print(f"  Innovation Level: {report['quality_indicators']['innovation_level']}")
    print(f"  Recommendation: {report['quality_indicators']['recommendation']}")
    
    # Save demo reports
    output_dir = Path("demo_output")
    output_dir.mkdir(exist_ok=True)
    
    # JSON report
    json_path = output_dir / "demo_evaluation.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # HTML report
    html_report = checker.generate_html_report(report)
    html_path = output_dir / "demo_evaluation.html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"\nDemo reports saved:")
    print(f"  JSON: {json_path}")
    print(f"  HTML: {html_path}")
    
    # 6. Show evaluation criteria structure
    print("\n\n6. EVALUATION CRITERIA STRUCTURE")
    print("-" * 40)
    
    criteria = checker.config["evaluation_criteria"]
    total_weight = 0
    total_points = 0
    
    for category, details in criteria.items():
        print(f"\n{category.replace('_', ' ').title()}:")
        print(f"  Weight: {details['weight']*100:.0f}%")
        print(f"  Points: {details['total_points']}")
        total_weight += details['weight']
        total_points += details['total_points']
        
        if 'aspects' in details:
            print("  Sub-criteria:")
            for aspect, aspect_details in details['aspects'].items():
                print(f"    - {aspect.replace('_', ' ').title()}: {aspect_details['points']} points")
    
    print(f"\nTotal Weight: {total_weight*100:.0f}%")
    print(f"Total Points: {total_points}")
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    demonstrate_mba_quality_system()