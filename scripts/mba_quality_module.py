#!/usr/bin/env python3
"""
MBA Quality Module
Comprehensive quality assessment for MBA thesis according to evaluation criteria
Includes grammar checking, APA7 validation, literature quality analysis, and theoretical foundation verification
"""
import re
import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime
import language_tool_python
from scripts.utils import get_project_root, load_json, save_json
from scripts.citation_quality_control import CitationQualityControl

class MBAQualityModule:
    def __init__(self):
        self.project_root = get_project_root()
        self.standards = self._load_mba_standards()
        self.citation_checker = CitationQualityControl()
        
        # Initialize language tool for German grammar/spelling
        self.language_tool = None
        try:
            self.language_tool = language_tool_python.LanguageToolPublicAPI('de-DE')
        except Exception as e:
            # Try offline tool if API fails
            try:
                self.language_tool = language_tool_python.LanguageTool('de-DE')
            except Exception as e2:
                # Language tool not available
                print(f"Warning: Language tool not available: {e2}")
                self.language_tool = None
        
        # Scoring weights from MBA standards
        self.scoring_weights = {
            "aufbau_und_form": 20,
            "forschungsfrage_und_literatur": 30,
            "qualitaet_methodische_durchfuehrung": 40,
            "innovationsgrad_relevanz": 10
        }
    
    def _load_mba_standards(self) -> Dict:
        """Load MBA evaluation standards."""
        standards_file = self.project_root / "config" / "mba-standards.json"
        if standards_file.exists():
            return load_json(standards_file)
        return {}
    
    def check_grammar_spelling(self, text: str) -> Dict[str, Any]:
        """Check grammar and spelling using language_tool_python."""
        result = {
            "total_errors": 0,
            "grammar_errors": 0,
            "spelling_errors": 0,
            "style_issues": 0,
            "issues": [],
            "score": 100  # Start with perfect score
        }
        
        if not self.language_tool:
            result["error"] = "Language tool not available - skipping grammar check"
            result["score"] = 70  # Default score when check not available
            return result
        
        try:
            matches = self.language_tool.check(text)
            
            for match in matches:
                issue = {
                    "message": match.message,
                    "type": match.ruleIssueType,
                    "context": match.context,
                    "replacements": match.replacements[:3] if match.replacements else [],
                    "offset": match.offset,
                    "length": match.errorLength
                }
                
                # Categorize errors
                if match.ruleIssueType == 'misspelling':
                    result["spelling_errors"] += 1
                    result["score"] -= 2  # -2 points per spelling error
                elif match.ruleIssueType in ['grammar', 'typographical']:
                    result["grammar_errors"] += 1
                    result["score"] -= 3  # -3 points per grammar error
                else:
                    result["style_issues"] += 1
                    result["score"] -= 1  # -1 point per style issue
                
                result["issues"].append(issue)
            
            result["total_errors"] = len(matches)
            result["score"] = max(0, result["score"])  # Don't go below 0
            
        except Exception as e:
            result["error"] = f"Language check failed: {str(e)}"
            result["score"] = 70  # Default score if check fails
        
        return result
    
    def validate_apa7_citation(self, citation: str) -> Dict[str, Any]:
        """Validate APA 7th edition citation format."""
        result = {
            "valid": True,
            "format_issues": [],
            "suggestions": [],
            "apa7_score": 100
        }
        
        # APA7 patterns
        patterns = {
            "in_text_single": r'\([A-Z][a-z]+,\s*\d{4}\)',  # (Author, 2020)
            "in_text_multiple": r'\([A-Z][a-z]+\s*&\s*[A-Z][a-z]+,\s*\d{4}\)',  # (Author & Author, 2020)
            "in_text_et_al": r'\([A-Z][a-z]+\s+et\s+al\.,\s*\d{4}\)',  # (Author et al., 2020)
            "in_text_with_page": r'\([A-Z][a-z]+.*?,\s*\d{4},\s*[Ss]\.\s*\d+\)',  # (Author, 2020, S. 123)
            "narrative": r'[A-Z][a-z]+\s*\(\d{4}\)',  # Author (2020)
        }
        
        # Check if citation matches any valid pattern
        matched = False
        for pattern_name, pattern in patterns.items():
            if re.match(pattern, citation):
                matched = True
                break
        
        if not matched:
            result["valid"] = False
            result["format_issues"].append("Citation does not match APA7 format")
            result["apa7_score"] -= 20
        
        # Specific APA7 checks
        # Check for comma before year
        if "(" in citation and ")" in citation:
            content = citation[citation.find("(")+1:citation.find(")")]
            if "," not in content and not re.match(r'^\d{4}$', content):
                result["format_issues"].append("Missing comma before year")
                result["apa7_score"] -= 10
        
        # Check for proper et al. formatting
        if "et al" in citation and "et al." not in citation:
            result["format_issues"].append("'et al.' should include period")
            result["apa7_score"] -= 5
        
        # Check for proper ampersand usage
        if " and " in citation and "(" in citation:
            result["format_issues"].append("Use '&' instead of 'and' in parenthetical citations")
            result["apa7_score"] -= 5
        
        # Generate suggestions
        if result["format_issues"]:
            result["suggestions"].append("Review APA 7th edition citation guidelines")
            if "comma" in str(result["format_issues"]):
                result["suggestions"].append("Format: (Author, Year) or (Author & Author, Year)")
        
        result["apa7_score"] = max(0, result["apa7_score"])
        return result
    
    def analyze_literature_quality(self, references: List[Dict]) -> Dict[str, Any]:
        """Analyze literature quality based on MBA standards."""
        result = {
            "total_references": len(references),
            "quality_metrics": {},
            "scores": {},
            "issues": [],
            "recommendations": []
        }
        
        if not references:
            result["issues"].append("No references found")
            return result
        
        # Calculate metrics
        current_year = datetime.now().year
        recent_pubs = sum(1 for ref in references if int(ref.get("year", 0)) >= 2020)
        very_recent_pubs = sum(1 for ref in references if int(ref.get("year", 0)) >= 2022)
        
        # Q1 journal ratio
        q1_count = sum(1 for ref in references if 
                      ref.get("quartile") == "Q1" or 
                      ref.get("journal", "") in self.citation_checker._load_q1_journals())
        
        # DOI availability
        doi_count = sum(1 for ref in references if ref.get("doi"))
        
        # International distribution (simplified - would need country data)
        journals = [ref.get("journal", "") for ref in references if ref.get("journal")]
        unique_journals = len(set(journals))
        
        # Calculate percentages
        result["quality_metrics"] = {
            "aktualitaet_2020_plus": (recent_pubs / len(references)) * 100,
            "aktualitaet_2022_plus": (very_recent_pubs / len(references)) * 100,
            "q1_journal_ratio": (q1_count / len(references)) * 100,
            "doi_availability": (doi_count / len(references)) * 100,
            "journal_diversity": unique_journals,
            "average_publication_year": sum(int(ref.get("year", 0)) for ref in references) / len(references)
        }
        
        # Score based on MBA standards
        scores = {}
        
        # Aktualität (Currency) Score
        if result["quality_metrics"]["aktualitaet_2020_plus"] >= 90:
            scores["aktualitaet"] = 5  # sehr gut
        elif result["quality_metrics"]["aktualitaet_2020_plus"] >= 70:
            scores["aktualitaet"] = 4  # gut
        elif result["quality_metrics"]["aktualitaet_2020_plus"] >= 50:
            scores["aktualitaet"] = 3  # befriedigend
        elif result["quality_metrics"]["aktualitaet_2020_plus"] >= 30:
            scores["aktualitaet"] = 2  # ausreichend
        else:
            scores["aktualitaet"] = 1  # nicht ausreichend
        
        # Q1 Journal Score
        if result["quality_metrics"]["q1_journal_ratio"] >= 80:
            scores["q1_journals"] = 5
        elif result["quality_metrics"]["q1_journal_ratio"] >= 60:
            scores["q1_journals"] = 4
        elif result["quality_metrics"]["q1_journal_ratio"] >= 40:
            scores["q1_journals"] = 3
        elif result["quality_metrics"]["q1_journal_ratio"] >= 20:
            scores["q1_journals"] = 2
        else:
            scores["q1_journals"] = 1
        
        # DOI Availability Score
        if result["quality_metrics"]["doi_availability"] == 100:
            scores["doi_verfuegbarkeit"] = 5
        elif result["quality_metrics"]["doi_availability"] >= 90:
            scores["doi_verfuegbarkeit"] = 4
        elif result["quality_metrics"]["doi_availability"] >= 80:
            scores["doi_verfuegbarkeit"] = 3
        elif result["quality_metrics"]["doi_availability"] >= 60:
            scores["doi_verfuegbarkeit"] = 2
        else:
            scores["doi_verfuegbarkeit"] = 1
        
        result["scores"] = scores
        result["overall_literature_score"] = sum(scores.values()) / len(scores)
        
        # Generate issues and recommendations
        if result["quality_metrics"]["aktualitaet_2020_plus"] < 70:
            result["issues"].append(f"Only {result['quality_metrics']['aktualitaet_2020_plus']:.1f}% of literature from 2020+")
            result["recommendations"].append("Add more recent publications (2020-2025)")
        
        if result["quality_metrics"]["q1_journal_ratio"] < 60:
            result["issues"].append(f"Q1 journal ratio is {result['quality_metrics']['q1_journal_ratio']:.1f}% (target: >60%)")
            result["recommendations"].append("Include more high-impact Q1 journal articles")
        
        if result["quality_metrics"]["doi_availability"] < 90:
            result["issues"].append(f"DOI availability is {result['quality_metrics']['doi_availability']:.1f}% (target: >90%)")
            result["recommendations"].append("Ensure all academic sources have DOIs")
        
        return result
    
    def verify_theoretical_foundation(self, text: str) -> Dict[str, Any]:
        """Verify if text includes proper theoretical foundations."""
        result = {
            "has_primary_framework": False,
            "frameworks_found": [],
            "theory_density": 0,
            "score": 0,
            "issues": [],
            "recommendations": []
        }
        
        # Load expected theories from MBA standards
        if self.standards and "theoretical_foundations" in self.standards:
            core_theories = self.standards["theoretical_foundations"]["core_theories"]
            primary_framework = core_theories.get("primary_framework", {})
            supporting_theories = core_theories.get("supporting_theories", [])
            
            # Check for primary framework
            if primary_framework:
                framework_name = primary_framework.get("name", "")
                if framework_name.lower() in text.lower() or "TOE" in text:
                    result["has_primary_framework"] = True
                    result["frameworks_found"].append(framework_name)
            
            # Check for supporting theories
            theory_mentions = 0
            for theory in supporting_theories:
                theory_name = theory.get("name", "")
                if theory_name.lower() in text.lower() or any(keyword in text.lower() for keyword in ["RBV", "VRIO", "dynamic capabilities"]):
                    result["frameworks_found"].append(theory_name)
                    theory_mentions += 1
            
            # Calculate theory density (theories per 1000 words)
            word_count = len(text.split())
            result["theory_density"] = (theory_mentions / word_count) * 1000 if word_count > 0 else 0
            
            # Scoring
            if result["has_primary_framework"] and len(result["frameworks_found"]) >= 3:
                result["score"] = 90
            elif result["has_primary_framework"] and len(result["frameworks_found"]) >= 2:
                result["score"] = 75
            elif len(result["frameworks_found"]) >= 2:
                result["score"] = 60
            elif len(result["frameworks_found"]) >= 1:
                result["score"] = 40
            else:
                result["score"] = 20
            
            # Issues and recommendations
            if not result["has_primary_framework"]:
                result["issues"].append("Primary theoretical framework (TOE) not found")
                result["recommendations"].append("Include Technology-Organization-Environment (TOE) Framework as primary foundation")
            
            if len(result["frameworks_found"]) < 3:
                result["issues"].append(f"Only {len(result['frameworks_found'])} theoretical frameworks found (minimum: 3)")
                result["recommendations"].append("Add supporting theories like RBV, Dynamic Capabilities, or Digital Business Strategy")
            
            if result["theory_density"] < 2:
                result["issues"].append("Low theoretical density in text")
                result["recommendations"].append("Increase theoretical depth and discussion")
        
        return result
    
    def calculate_overall_score(self, 
                               grammar_score: float,
                               citation_score: float,
                               literature_score: float,
                               theory_score: float) -> Dict[str, Any]:
        """Calculate overall MBA quality score based on evaluation criteria."""
        
        # Map component scores to MBA evaluation categories
        aufbau_form_score = (grammar_score * 0.7 + citation_score * 0.3)
        literature_quality_score = (literature_score * 0.6 + theory_score * 0.4)
        
        # For now, use placeholder scores for methodology and innovation
        # These would be calculated from actual methodology analysis
        methodology_score = 70  # Placeholder
        innovation_score = 75   # Placeholder
        
        # Calculate weighted scores
        scores = {
            "aufbau_und_form": {
                "raw_score": aufbau_form_score,
                "weight": self.scoring_weights["aufbau_und_form"],
                "weighted_score": (aufbau_form_score / 100) * self.scoring_weights["aufbau_und_form"]
            },
            "forschungsfrage_und_literatur": {
                "raw_score": literature_quality_score,
                "weight": self.scoring_weights["forschungsfrage_und_literatur"],
                "weighted_score": (literature_quality_score / 100) * self.scoring_weights["forschungsfrage_und_literatur"]
            },
            "qualitaet_methodische_durchfuehrung": {
                "raw_score": methodology_score,
                "weight": self.scoring_weights["qualitaet_methodische_durchfuehrung"],
                "weighted_score": (methodology_score / 100) * self.scoring_weights["qualitaet_methodische_durchfuehrung"]
            },
            "innovationsgrad_relevanz": {
                "raw_score": innovation_score,
                "weight": self.scoring_weights["innovationsgrad_relevanz"],
                "weighted_score": (innovation_score / 100) * self.scoring_weights["innovationsgrad_relevanz"]
            }
        }
        
        # Calculate total score
        total_score = sum(cat["weighted_score"] for cat in scores.values())
        
        # Determine grade
        if total_score >= 90:
            grade = "sehr gut (1.0-1.3)"
            grade_numeric = 1.0
        elif total_score >= 80:
            grade = "gut (1.7-2.3)"
            grade_numeric = 2.0
        elif total_score >= 70:
            grade = "befriedigend (2.7-3.3)"
            grade_numeric = 3.0
        elif total_score >= 60:
            grade = "ausreichend (3.7-4.0)"
            grade_numeric = 3.7
        else:
            grade = "nicht ausreichend (5.0)"
            grade_numeric = 5.0
        
        return {
            "category_scores": scores,
            "total_score": total_score,
            "total_possible": 100,
            "percentage": total_score,
            "grade": grade,
            "grade_numeric": grade_numeric,
            "strengths": [cat for cat, data in scores.items() if data["raw_score"] >= 80],
            "weaknesses": [cat for cat, data in scores.items() if data["raw_score"] < 60],
            "priority_improvements": self._get_priority_improvements(scores)
        }
    
    def _get_priority_improvements(self, scores: Dict) -> List[Dict]:
        """Identify priority improvements based on weight and potential gain."""
        improvements = []
        
        for category, data in scores.items():
            if data["raw_score"] < 80:  # Room for improvement
                potential_gain = (80 - data["raw_score"]) * data["weight"] / 100
                improvements.append({
                    "category": category,
                    "current_score": data["raw_score"],
                    "target_score": 80,
                    "weight": data["weight"],
                    "potential_point_gain": potential_gain,
                    "priority": "high" if potential_gain > 5 else "medium" if potential_gain > 2 else "low"
                })
        
        # Sort by potential gain
        improvements.sort(key=lambda x: x["potential_point_gain"], reverse=True)
        return improvements[:3]  # Return top 3 priorities
    
    def generate_quality_report(self, file_path: str) -> Dict[str, Any]:
        """Generate comprehensive quality report for a thesis file."""
        path = Path(file_path)
        if not path.exists():
            path = self.project_root / "writing" / "chapters" / file_path
        
        if not path.exists():
            return {"error": "File not found"}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Run all quality checks
        grammar_check = self.check_grammar_spelling(content)
        citation_check = self.citation_checker.check_document_citations(str(path))
        
        # Get references for literature analysis
        ref_file = self.project_root / "research" / "validated-literature.json"
        references = load_json(ref_file) if ref_file.exists() else []
        literature_analysis = self.analyze_literature_quality(references)
        
        theory_check = self.verify_theoretical_foundation(content)
        
        # Calculate citation score from citation check results
        citation_score = 100
        if citation_check.get("total_citations", 0) > 0:
            citation_score = (citation_check.get("valid_citations", 0) / citation_check["total_citations"]) * 100
        
        # Calculate overall score
        overall_assessment = self.calculate_overall_score(
            grammar_score=grammar_check.get("score", 70),
            citation_score=citation_score,
            literature_score=literature_analysis.get("overall_literature_score", 3) * 20,  # Convert 1-5 to percentage
            theory_score=theory_check.get("score", 50)
        )
        
        # Compile report
        report = {
            "file": str(file_path),
            "timestamp": datetime.now().isoformat(),
            "word_count": len(content.split()),
            "components": {
                "grammar_spelling": grammar_check,
                "citations": citation_check,
                "literature_quality": literature_analysis,
                "theoretical_foundation": theory_check
            },
            "overall_assessment": overall_assessment,
            "executive_summary": self._generate_executive_summary(overall_assessment),
            "action_items": self._generate_action_items(grammar_check, citation_check, 
                                                       literature_analysis, theory_check)
        }
        
        # Save report
        report_path = self.project_root / "research" / "quality_reports" / f"mba_quality_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        save_json(report, report_path)
        
        return report
    
    def _generate_executive_summary(self, assessment: Dict) -> str:
        """Generate executive summary of quality assessment."""
        summary = f"""MBA Quality Assessment Summary:
        
Overall Score: {assessment['total_score']:.1f}/100 ({assessment['grade']})

Category Breakdown:
- Aufbau & Form: {assessment['category_scores']['aufbau_und_form']['raw_score']:.1f}% (Weight: {assessment['category_scores']['aufbau_und_form']['weight']}%)
- Forschungsfrage & Literatur: {assessment['category_scores']['forschungsfrage_und_literatur']['raw_score']:.1f}% (Weight: {assessment['category_scores']['forschungsfrage_und_literatur']['weight']}%)
- Methodische Durchführung: {assessment['category_scores']['qualitaet_methodische_durchfuehrung']['raw_score']:.1f}% (Weight: {assessment['category_scores']['qualitaet_methodische_durchfuehrung']['weight']}%)
- Innovationsgrad: {assessment['category_scores']['innovationsgrad_relevanz']['raw_score']:.1f}% (Weight: {assessment['category_scores']['innovationsgrad_relevanz']['weight']}%)

Strengths: {', '.join(assessment['strengths']) if assessment['strengths'] else 'None identified'}
Areas for Improvement: {', '.join(assessment['weaknesses']) if assessment['weaknesses'] else 'None identified'}
"""
        return summary
    
    def _generate_action_items(self, grammar: Dict, citations: Dict, 
                              literature: Dict, theory: Dict) -> List[Dict]:
        """Generate prioritized action items."""
        actions = []
        
        # Grammar/spelling actions
        if grammar.get("total_errors", 0) > 10:
            actions.append({
                "priority": "high",
                "category": "Aufbau & Form",
                "action": f"Fix {grammar['total_errors']} grammar/spelling errors",
                "impact": "Direct impact on Formale Präsentation score (7 points)",
                "effort": "medium"
            })
        
        # Citation actions
        if citations.get("issues", []):
            actions.append({
                "priority": "high",
                "category": "Aufbau & Form",
                "action": f"Correct {len(citations['issues'])} citation format issues",
                "impact": "Critical for Nachvollziehbarkeit der Quellen (8 points)",
                "effort": "low"
            })
        
        # Literature quality actions
        if literature.get("quality_metrics", {}).get("q1_journal_ratio", 0) < 60:
            actions.append({
                "priority": "high",
                "category": "Forschungsfrage & Literatur",
                "action": "Increase Q1 journal ratio from {:.1f}% to >60%".format(
                    literature['quality_metrics']['q1_journal_ratio']),
                "impact": "Major impact on Literatur score (30 points total)",
                "effort": "high"
            })
        
        # Theory actions
        if not theory.get("has_primary_framework"):
            actions.append({
                "priority": "critical",
                "category": "Forschungsfrage & Literatur",
                "action": "Add primary theoretical framework (TOE)",
                "impact": "Essential for theoretical foundation (20 points)",
                "effort": "medium"
            })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        actions.sort(key=lambda x: priority_order.get(x["priority"], 999))
        
        return actions

def main():
    """CLI interface for MBA quality checking."""
    import argparse
    parser = argparse.ArgumentParser(description="MBA thesis quality checker")
    parser.add_argument("--check-file", help="Check quality of a specific file")
    parser.add_argument("--check-grammar", help="Check only grammar/spelling")
    parser.add_argument("--check-citations", help="Check only citations")
    parser.add_argument("--check-literature", help="Analyze literature quality")
    parser.add_argument("--full-report", help="Generate full quality report", action="store_true")
    
    args = parser.parse_args()
    
    checker = MBAQualityModule()
    
    if args.check_file:
        if args.full_report:
            report = checker.generate_quality_report(args.check_file)
            print(report["executive_summary"])
            
            print("\nPriority Action Items:")
            for i, action in enumerate(report["action_items"][:5], 1):
                print(f"\n{i}. [{action['priority'].upper()}] {action['action']}")
                print(f"   Impact: {action['impact']}")
                print(f"   Effort: {action['effort']}")
        else:
            print("Use --full-report flag to generate comprehensive quality report")
    
    elif args.check_grammar:
        with open(args.check_grammar, 'r', encoding='utf-8') as f:
            text = f.read()
        result = checker.check_grammar_spelling(text)
        print(f"Grammar/Spelling Score: {result['score']}/100")
        print(f"Total errors: {result['total_errors']}")
        print(f"- Grammar: {result['grammar_errors']}")
        print(f"- Spelling: {result['spelling_errors']}")
        print(f"- Style: {result['style_issues']}")
    
    elif args.check_literature:
        ref_file = checker.project_root / "research" / "validated-literature.json"
        if ref_file.exists():
            references = load_json(ref_file)
            result = checker.analyze_literature_quality(references)
            print(f"\nLiterature Quality Analysis:")
            print(f"Total references: {result['total_references']}")
            print(f"\nQuality Metrics:")
            for metric, value in result['quality_metrics'].items():
                print(f"- {metric}: {value:.1f}")
            print(f"\nOverall Literature Score: {result['overall_literature_score']:.1f}/5")
            
            if result['recommendations']:
                print("\nRecommendations:")
                for rec in result['recommendations']:
                    print(f"- {rec}")

if __name__ == "__main__":
    main()