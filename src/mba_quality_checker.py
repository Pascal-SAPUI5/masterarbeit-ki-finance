#!/usr/bin/env python3
"""
MBA Quality Checker Module
Implements comprehensive quality evaluation for MBA thesis based on official standards
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re


class MBAQualityChecker:
    """MBA thesis quality evaluation system based on official criteria."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize with MBA standards configuration."""
        self.project_root = Path(__file__).parent.parent
        if config_path:
            config_file = Path(config_path)
        else:
            config_file = self.project_root / "config" / "mba-standards.json"
            
        with open(config_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
            
        # Known Q1 journals list
        self.q1_journals = [
            "Nature", "Science", "Cell", "BMJ", "JAMA", "Lancet",
            "Journal of Finance", "Journal of Financial Economics",
            "Review of Financial Studies", "Journal of Banking & Finance",
            "Information Systems Research", "MIS Quarterly",
            "Journal of Management Information Systems",
            "Journal of Strategic Information Systems",
            "Strategic Management Journal", "Academy of Management Journal",
            "Journal of Marketing", "Marketing Science", "Journal of Consumer Research"
        ]
        
    def calculate_grade(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate final grade based on evaluation criteria scores."""
        # Validate all required categories are present
        required_categories = ["aufbau_und_form", "forschungsfrage_und_literatur",
                               "qualitaet_methodische_durchfuehrung", "innovationsgrad_relevanz"]
        
        for category in required_categories:
            if category not in scores:
                raise ValueError(f"Missing required category: {category}")
                
        # Validate scores don't exceed maximums
        criteria = self.config["evaluation_criteria"]
        for category, score in scores.items():
            max_points = criteria[category]["total_points"]
            if score > max_points:
                raise ValueError(f"Score for {category} ({score}) exceeds maximum ({max_points})")
                
        # Calculate total points
        total_points = sum(scores.values())
        percentage = (total_points / 100) * 100
        
        # Determine grade category
        grade_scale = self.config["grading_scale"]
        if percentage >= 90:
            grade_category = "sehr_gut"
            numeric_grade = self._interpolate_grade(percentage, 90, 100, 1.0, 1.3)
        elif percentage >= 80:
            grade_category = "gut"
            numeric_grade = self._interpolate_grade(percentage, 80, 89, 1.7, 2.3)
        elif percentage >= 70:
            grade_category = "befriedigend"
            numeric_grade = self._interpolate_grade(percentage, 70, 79, 2.7, 3.3)
        elif percentage >= 60:
            grade_category = "ausreichend"
            numeric_grade = self._interpolate_grade(percentage, 60, 69, 3.7, 4.0)
        else:
            grade_category = "nicht_ausreichend"
            numeric_grade = "5.0"
            
        return {
            "total_points": int(total_points),
            "percentage": int(percentage),
            "grade_category": grade_category,
            "numeric_grade": numeric_grade,
            "description": grade_scale[grade_category]["description"]
        }
        
    def _interpolate_grade(self, percentage: float, min_pct: float, max_pct: float,
                           best_grade: float, worst_grade: float) -> str:
        """Interpolate numeric grade within a category range."""
        # Map percentage to grade (inverse relationship)
        position = (percentage - min_pct) / (max_pct - min_pct)
        grade = worst_grade - (position * (worst_grade - best_grade))
        
        # Round to nearest valid grade
        valid_grades = [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0, 5.0]
        closest_grade = min(valid_grades, key=lambda x: abs(x - grade))
        
        return str(closest_grade)
        
    def calculate_detailed_grade(self, detailed_scores: Dict[str, float]) -> Dict[str, Any]:
        """Calculate grade from detailed aspect scores."""
        # Map detailed scores to categories
        category_scores = {
            "aufbau_und_form": (
                detailed_scores.get("schluessigkeit_aufbau", 0) +
                detailed_scores.get("formale_praesentation", 0) +
                detailed_scores.get("nachvollziehbarkeit_quellen", 0)
            ),
            "forschungsfrage_und_literatur": (
                detailed_scores.get("breite_literatur", 0) +
                detailed_scores.get("meta_problemstellung", 0)
            ),
            "qualitaet_methodische_durchfuehrung": (
                detailed_scores.get("durchfuehrung_methodik", 0) +
                detailed_scores.get("qualitaet_empirische_ergebnisse", 0)
            ),
            "innovationsgrad_relevanz": (
                detailed_scores.get("innovationsgrad_nutzen", 0) +
                detailed_scores.get("selbstaendigkeit_originalitaet", 0)
            )
        }
        
        # Calculate grade
        grade_result = self.calculate_grade(category_scores)
        grade_result["categories"] = category_scores
        
        return grade_result
        
    def assess_literature_quality(self, literature_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Assess literature quality based on MBA standards."""
        standards = self.config["literature_quality_standards"]
        
        # Extract metrics
        aktualitaet = literature_stats.get("aktualitaet", 0)
        q1_percentage = literature_stats.get("q1_percentage", 0)
        doi_coverage = literature_stats.get("doi_coverage", 0)
        international_dist = literature_stats.get("internationalitaet", {})
        
        # Check distribution balance
        is_balanced = self._check_international_balance(international_dist)
        
        # Determine quality level
        if (aktualitaet > 90 and q1_percentage > 80 and doi_coverage == 100 and is_balanced):
            category = "sehr_gut_5_punkte"
            points = 5
        elif (aktualitaet > 70 and q1_percentage > 60 and doi_coverage > 90):
            category = "gut_4_punkte"
            points = 4
        elif (aktualitaet > 50 and q1_percentage > 40 and doi_coverage > 80):
            category = "befriedigend_3_punkte"
            points = 3
        elif (aktualitaet > 30 and q1_percentage > 20 and doi_coverage > 60):
            category = "ausreichend_2_punkte"
            points = 2
        else:
            category = "nicht_ausreichend_1_punkt"
            points = 1
            
        return {
            "category": category,
            "points": points,
            "details": standards[category],
            "metrics": {
                "aktualitaet": aktualitaet,
                "q1_percentage": q1_percentage,
                "doi_coverage": doi_coverage,
                "international_balance": is_balanced
            }
        }
        
    def _check_international_balance(self, distribution: Dict[str, float]) -> bool:
        """Check if geographic distribution is balanced."""
        if not distribution:
            return False
            
        values = list(distribution.values())
        if len(values) < 3:
            return False
            
        # Check if no region dominates too much (>50%)
        max_percentage = max(values)
        if max_percentage > 50:
            return False
            
        # Check if distribution is reasonably balanced
        min_percentage = min(values)
        if min_percentage < 10:
            return False
            
        return True
        
    def generate_quality_report(self, scores: Dict[str, Any], 
                                literature_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        # Calculate main grade
        main_scores = {k: v["score"] for k, v in scores.items()}
        grade_result = self.calculate_grade(main_scores)
        
        # Assess literature quality
        lit_assessment = self.assess_literature_quality(literature_stats)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(main_scores)
        
        return {
            "summary": {
                "total_points": grade_result["total_points"],
                "percentage": grade_result["percentage"],
                "grade_category": grade_result["grade_category"],
                "numeric_grade": grade_result["numeric_grade"]
            },
            "detailed_evaluation": scores,
            "literature_quality": lit_assessment,
            "recommendations": recommendations,
            "grade_breakdown": {
                "main_evaluation": grade_result["total_points"],
                "literature_bonus": lit_assessment["points"],
                "total_with_bonus": min(100, grade_result["total_points"] + lit_assessment["points"])
            },
            "timestamp": datetime.now().isoformat()
        }
        
    def generate_recommendations(self, scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate improvement recommendations based on scores."""
        criteria = self.config["evaluation_criteria"]
        
        # Calculate percentages for each category
        category_percentages = {}
        priority_improvements = []
        strengths = []
        
        for category, score in scores.items():
            max_points = criteria[category]["total_points"]
            percentage = (score / max_points) * 100
            category_percentages[category] = percentage
            
            if percentage < 60:
                priority_improvements.append(category)
            elif percentage >= 70:
                strengths.append(category)
                
        # Calculate potential improvement
        current_total = sum(scores.values())
        potential_total = sum(
            max(score, criteria[cat]["total_points"] * 0.8)
            for cat, score in scores.items()
        )
        potential_improvement = potential_total - current_total
        
        # Generate specific recommendations
        specific_recommendations = []
        
        if "aufbau_und_form" in priority_improvements:
            specific_recommendations.append({
                "category": "Aufbau und Form",
                "actions": [
                    "Überarbeitung der Gliederung für bessere Schlüssigkeit",
                    "Korrektur formaler Fehler (Grammatik, Rechtschreibung)",
                    "Vervollständigung der Quellenangaben"
                ],
                "potential_points": criteria["aufbau_und_form"]["total_points"] * 0.8 - scores["aufbau_und_form"]
            })
            
        if "forschungsfrage_und_literatur" in priority_improvements:
            specific_recommendations.append({
                "category": "Forschungsfrage und Literatur",
                "actions": [
                    "Präzisierung der Forschungsfrage",
                    "Erweiterung der Literaturrecherche um Q1-Journals",
                    "Aktualisierung veralteter Quellen (2020+)"
                ],
                "potential_points": criteria["forschungsfrage_und_literatur"]["total_points"] * 0.8 - scores["forschungsfrage_und_literatur"]
            })
            
        if "qualitaet_methodische_durchfuehrung" in priority_improvements:
            specific_recommendations.append({
                "category": "Methodische Durchführung",
                "actions": [
                    "Detailliertere Methodenbeschreibung",
                    "Erhöhung der Stichprobengröße",
                    "Klarere Darstellung der Ergebnisse"
                ],
                "potential_points": criteria["qualitaet_methodische_durchfuehrung"]["total_points"] * 0.8 - scores["qualitaet_methodische_durchfuehrung"]
            })
            
        return {
            "priority_improvements": priority_improvements,
            "strengths": strengths,
            "category_percentages": category_percentages,
            "potential_grade_improvement": potential_improvement,
            "specific_recommendations": specific_recommendations,
            "estimated_effort": self._estimate_effort(priority_improvements)
        }
        
    def _estimate_effort(self, priority_improvements: List[str]) -> Dict[str, Any]:
        """Estimate effort required for improvements."""
        effort_mapping = {
            "aufbau_und_form": {"hours": 20, "difficulty": "medium"},
            "forschungsfrage_und_literatur": {"hours": 40, "difficulty": "high"},
            "qualitaet_methodische_durchfuehrung": {"hours": 60, "difficulty": "high"},
            "innovationsgrad_relevanz": {"hours": 30, "difficulty": "medium"}
        }
        
        total_hours = sum(effort_mapping[cat]["hours"] for cat in priority_improvements)
        max_difficulty = max(
            (effort_mapping[cat]["difficulty"] for cat in priority_improvements),
            default="low"
        )
        
        return {
            "total_hours": total_hours,
            "weeks_needed": (total_hours / 40) + 1,  # Assuming 40 hours/week
            "difficulty": max_difficulty,
            "priority_order": sorted(
                priority_improvements,
                key=lambda x: effort_mapping[x]["hours"]
            )
        }
        
    def detect_journal_quartile(self, journal_name: str) -> Optional[str]:
        """Detect journal quartile based on known Q1 journals list."""
        if journal_name in self.q1_journals:
            return "Q1"
        return None
        
    def analyze_publication_years(self, references: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze distribution of publication years."""
        years = [int(ref.get("year", 0)) for ref in references if ref.get("year")]
        
        if not years:
            return {"error": "No valid years found"}
            
        current_year = datetime.now().year
        total = len(years)
        
        # Count publications by recency
        count_2020_plus = sum(1 for y in years if y >= 2020)
        count_2022_plus = sum(1 for y in years if y >= 2022)
        
        return {
            "total_references": total,
            "newest_year": max(years),
            "oldest_year": min(years),
            "average_year": sum(years) / total,
            "percentage_2020_plus": (count_2020_plus / total) * 100,
            "percentage_2022_plus": (count_2022_plus / total) * 100,
            "distribution": {
                "2024-2025": sum(1 for y in years if y >= 2024),
                "2022-2023": sum(1 for y in years if 2022 <= y < 2024),
                "2020-2021": sum(1 for y in years if 2020 <= y < 2022),
                "pre-2020": sum(1 for y in years if y < 2020)
            }
        }
        
    def analyze_geographic_distribution(self, references: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze geographic distribution of references."""
        regions = {"US": 0, "EU": 0, "Other": 0}
        
        # Country to region mapping
        us_keywords = ["USA", "United States", "Harvard", "MIT", "Stanford"]
        eu_keywords = ["Germany", "France", "UK", "Munich", "Sorbonne", "Oxford"]
        
        for ref in references:
            affiliation = ref.get("affiliation", "")
            
            if any(keyword in affiliation for keyword in us_keywords):
                regions["US"] += 1
            elif any(keyword in affiliation for keyword in eu_keywords):
                regions["EU"] += 1
            else:
                # Everything else (including Asia) goes to Other
                regions["Other"] += 1
                
        total = sum(regions.values())
        if total == 0:
            return {"error": "No affiliations found"}
            
        # Convert to percentages
        distribution = {k: (v / total) * 100 for k, v in regions.items()}
        distribution["is_balanced"] = self._check_international_balance(distribution)
        
        return distribution
        
    def generate_comprehensive_report(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive evaluation report."""
        # Extract scores
        total_points = 0
        category_breakdown = {}
        
        for category, data in evaluation_data["scores"].items():
            total_points += data["total"]
            category_breakdown[category] = {
                "score": data["total"],
                "max_points": self.config["evaluation_criteria"][category]["total_points"],
                "percentage": (data["total"] / self.config["evaluation_criteria"][category]["total_points"]) * 100,
                "details": data["breakdown"]
            }
            
        # Calculate final grade
        percentage = (total_points / 100) * 100
        grade_info = self.calculate_grade({k: v["total"] for k, v in evaluation_data["scores"].items()})
        
        # Assess literature quality
        lit_metrics = evaluation_data["literature_analysis"]["quality_metrics"]
        lit_assessment = self.assess_literature_quality({
            "aktualitaet": lit_metrics["aktualitaet"]["2020_plus"],
            "q1_percentage": lit_metrics["journal_quality"]["q1_journals"],
            "doi_coverage": lit_metrics["doi_coverage"],
            "internationalitaet": lit_metrics["geographic_distribution"]
        })
        
        # Generate recommendations
        scores_dict = {k: v["total"] for k, v in evaluation_data["scores"].items()}
        recommendations = self.generate_recommendations(scores_dict)
        
        return {
            "metadata": {
                "thesis_title": evaluation_data["thesis_title"],
                "author": evaluation_data["author"],
                "evaluation_date": evaluation_data["date"],
                "generated_at": datetime.now().isoformat()
            },
            "executive_summary": {
                "final_grade": grade_info["numeric_grade"],
                "grade_category": grade_info["grade_category"],
                "total_points": total_points,
                "percentage": percentage,
                "key_strengths": self._identify_strengths(category_breakdown),
                "main_weaknesses": self._identify_weaknesses(category_breakdown)
            },
            "detailed_evaluation": category_breakdown,
            "literature_quality_assessment": {
                "score": lit_assessment,
                "statistics": evaluation_data["literature_analysis"],
                "top_journals": evaluation_data["literature_analysis"].get("top_journals", []),
                "theoretical_coverage": evaluation_data["literature_analysis"].get("theoretical_frameworks", [])
            },
            "final_grade": grade_info,
            "recommendations": recommendations,
            "quality_indicators": {
                "meets_mba_standards": percentage >= 60,
                "literature_quality": lit_assessment["category"],
                "innovation_level": self._assess_innovation_level(
                    evaluation_data["scores"]["innovationsgrad_relevanz"]["total"]
                ),
                "recommendation": self._generate_final_recommendation(percentage)
            }
        }
        
    def _identify_strengths(self, breakdown: Dict[str, Any]) -> List[str]:
        """Identify key strengths from evaluation."""
        strengths = []
        for category, data in breakdown.items():
            if data["percentage"] >= 85:
                strengths.append(f"Exzellente Leistung in {category.replace('_', ' ').title()}")
            elif data["percentage"] >= 75:
                strengths.append(f"Sehr gute Leistung in {category.replace('_', ' ').title()}")
        return strengths
        
    def _identify_weaknesses(self, breakdown: Dict[str, Any]) -> List[str]:
        """Identify main weaknesses from evaluation."""
        weaknesses = []
        for category, data in breakdown.items():
            if data["percentage"] < 60:
                weaknesses.append(f"Verbesserungsbedarf in {category.replace('_', ' ').title()}")
            elif data["percentage"] < 70:
                weaknesses.append(f"Ausbaufähig in {category.replace('_', ' ').title()}")
        return weaknesses
        
    def _assess_innovation_level(self, innovation_score: float) -> str:
        """Assess the innovation level based on score."""
        max_score = self.config["evaluation_criteria"]["innovationsgrad_relevanz"]["total_points"]
        percentage = (innovation_score / max_score) * 100
        
        if percentage >= 90:
            return "Herausragend innovativ"
        elif percentage >= 80:
            return "Sehr innovativ"
        elif percentage >= 70:
            return "Innovativ"
        elif percentage >= 60:
            return "Teilweise innovativ"
        else:
            return "Wenig innovativ"
            
    def _generate_final_recommendation(self, percentage: float) -> str:
        """Generate final recommendation based on overall performance."""
        if percentage >= 90:
            return "Hervorragende Arbeit - Zur Veröffentlichung empfohlen"
        elif percentage >= 80:
            return "Sehr gute Arbeit - Annahme ohne Auflagen"
        elif percentage >= 70:
            return "Gute Arbeit - Annahme mit kleineren Überarbeitungen"
        elif percentage >= 60:
            return "Ausreichende Arbeit - Annahme mit größeren Überarbeitungen"
        else:
            return "Nicht ausreichend - Grundlegende Überarbeitung erforderlich"
            
    def generate_html_report(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML version of the quality report."""
        html = f"""
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MBA Qualitätsbericht - {report_data['metadata']['thesis_title'][:50]}...</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background-color: #1e3a5f;
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    margin-bottom: 30px;
                }}
                .summary-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }}
                .grade-badge {{
                    display: inline-block;
                    font-size: 48px;
                    font-weight: bold;
                    color: #1e3a5f;
                    border: 3px solid #1e3a5f;
                    border-radius: 50%;
                    width: 100px;
                    height: 100px;
                    line-height: 94px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .category-score {{
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-left: 4px solid #1e3a5f;
                    border-radius: 5px;
                }}
                .progress-bar {{
                    background: #e0e0e0;
                    height: 25px;
                    border-radius: 5px;
                    overflow: hidden;
                    margin: 10px 0;
                }}
                .progress-fill {{
                    background: #4caf50;
                    height: 100%;
                    text-align: center;
                    color: white;
                    line-height: 25px;
                    font-weight: bold;
                }}
                .recommendation {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                .strength {{
                    color: #4caf50;
                    font-weight: bold;
                }}
                .weakness {{
                    color: #f44336;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>MBA Qualitätsbericht</h1>
                <h2>{report_data['metadata']['thesis_title']}</h2>
                <p>Autor: {report_data['metadata']['author']} | Datum: {report_data['metadata']['evaluation_date']}</p>
            </div>
            
            <div class="summary-card">
                <h2>Gesamtbewertung</h2>
                <div style="text-align: center;">
                    <div class="grade-badge">{report_data['executive_summary']['final_grade']}</div>
                    <h3>{report_data['executive_summary']['grade_category'].replace('_', ' ').title()}</h3>
                    <p style="font-size: 24px;">{report_data['executive_summary']['total_points']}/100 Punkte ({report_data['executive_summary']['percentage']}%)</p>
                </div>
                
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {report_data['executive_summary']['percentage']}%">
                        {report_data['executive_summary']['percentage']}%
                    </div>
                </div>
                
                <p><strong>Empfehlung:</strong> {report_data['quality_indicators']['recommendation']}</p>
            </div>
            
            <div class="summary-card">
                <h2>Detaillierte Bewertung nach Kategorien</h2>
        """
        
        # Add category details
        for category, data in report_data['detailed_evaluation'].items():
            category_name = category.replace('_', ' ').title()
            html += f"""
                <div class="category-score">
                    <h3>{category_name}</h3>
                    <p><strong>{data['score']}/{data['max_points']} Punkte ({data['percentage']:.1f}%)</strong></p>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {data['percentage']:.1f}%; background: {'#4caf50' if data['percentage'] >= 80 else '#ff9800' if data['percentage'] >= 60 else '#f44336'}">
                            {data['percentage']:.1f}%
                        </div>
                    </div>
            """
            
            # Add subcriteria details
            if data.get('details'):
                html += "<table><tr><th>Aspekt</th><th>Punkte</th><th>Kommentar</th></tr>"
                for aspect, details in data['details'].items():
                    html += f"""
                        <tr>
                            <td>{aspect.replace('_', ' ').title()}</td>
                            <td>{details['score']}/{details['max']}</td>
                            <td>{details.get('comments', '')}</td>
                        </tr>
                    """
                html += "</table>"
            html += "</div>"
            
        # Add literature quality
        lit_quality = report_data['literature_quality_assessment']
        html += f"""
            <div class="summary-card">
                <h2>Literaturqualität</h2>
                <div class="category-score">
                    <p><strong>Bewertung:</strong> {lit_quality['score']['category'].replace('_', ' ').title()}</p>
                    <p><strong>Punkte:</strong> {lit_quality['score']['points']}/5</p>
                    
                    <h4>Kennzahlen:</h4>
                    <ul>
                        <li>Gesamtquellen: {lit_quality['statistics']['total_sources']}</li>
                        <li>Aktualität (2020+): {lit_quality['statistics']['quality_metrics']['aktualitaet']['2020_plus']}%</li>
                        <li>Q1-Journals: {lit_quality['statistics']['quality_metrics']['journal_quality']['q1_journals']}%</li>
                        <li>DOI-Verfügbarkeit: {lit_quality['statistics']['quality_metrics']['doi_coverage']}%</li>
                    </ul>
                </div>
            </div>
        """
        
        # Add recommendations
        recommendations = report_data['recommendations']
        html += """
            <div class="summary-card">
                <h2>Empfehlungen zur Verbesserung</h2>
        """
        
        if recommendations['specific_recommendations']:
            for rec in recommendations['specific_recommendations']:
                html += f"""
                    <div class="recommendation">
                        <h4>{rec['category']}</h4>
                        <ul>
                """
                for action in rec['actions']:
                    html += f"<li>{action}</li>"
                html += f"""
                        </ul>
                        <p><strong>Potenzielle Punktverbesserung:</strong> +{rec['potential_points']:.1f} Punkte</p>
                    </div>
                """
                
        html += """
            </div>
            
            <div class="summary-card">
                <h2>Stärken und Schwächen</h2>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <h3 class="strength">Stärken</h3>
                        <ul>
        """
        
        for strength in report_data['executive_summary']['key_strengths']:
            html += f"<li>{strength}</li>"
            
        html += """
                        </ul>
                    </div>
                    <div>
                        <h3 class="weakness">Verbesserungsbereiche</h3>
                        <ul>
        """
        
        for weakness in report_data['executive_summary']['main_weaknesses']:
            html += f"<li>{weakness}</li>"
            
        html += """
                        </ul>
                    </div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px; color: #666;">
                <p>Bericht generiert am: {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr</p>
                <p>MBA Qualitätssicherungssystem v1.0</p>
            </div>
        </body>
        </html>
        """
        
        return html


def main():
    """CLI interface for MBA quality checking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MBA Quality Checker")
    parser.add_argument("--test", action="store_true", help="Run test evaluation")
    parser.add_argument("--report", help="Generate report for thesis file")
    
    args = parser.parse_args()
    
    checker = MBAQualityChecker()
    
    if args.test:
        # Run test evaluation
        test_scores = {
            "aufbau_und_form": 17,
            "forschungsfrage_und_literatur": 26,
            "qualitaet_methodische_durchfuehrung": 32,
            "innovationsgrad_relevanz": 8
        }
        
        result = checker.calculate_grade(test_scores)
        print(f"Test Evaluation Result:")
        print(f"Total Points: {result['total_points']}/100")
        print(f"Grade: {result['numeric_grade']} ({result['grade_category']})")
        print(f"Description: {result['description']}")
        

if __name__ == "__main__":
    main()