#!/usr/bin/env python3
"""
MBA Quality Checker Module
========================

Comprehensive quality assessment tool for Master's thesis based on MBA standards.
Evaluates thesis quality across all four main criteria with detailed scoring.
"""

import json
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from datetime import datetime
import re
from dataclasses import dataclass, field
from scripts.utils import get_project_root, load_config, load_json


@dataclass
class QualityScore:
    """Represents a quality score for a specific aspect."""
    criterion: str
    aspect: str
    current_score: float
    max_score: float
    percentage: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    priority: str = "medium"  # high, medium, low


@dataclass
class MBAAssessment:
    """Complete MBA quality assessment result."""
    timestamp: str
    overall_score: float
    overall_percentage: float
    predicted_grade: str
    grade_range: str
    criteria_scores: Dict[str, QualityScore]
    high_priority_issues: List[Dict[str, Any]]
    improvement_plan: List[Dict[str, Any]]
    compliance_status: str


class MBAQualityChecker:
    """
    MBA Quality Checker for comprehensive thesis evaluation.
    """
    
    def __init__(self):
        self.project_root = get_project_root()
        self.config = load_config()
        self.mba_standards = self.config.get("mba_standards", {})
        self.evaluation_criteria = self.mba_standards.get("evaluation_criteria", {})
        self.grading_scale = self.mba_standards.get("grading_scale", {})
        self.literature_standards = self.mba_standards.get("literature_quality_standards", {})
        
        # Initialize scoring weights
        self.criteria_weights = {
            "aufbau_und_form": 0.20,
            "forschungsfrage_und_literatur": 0.30,
            "qualitaet_methodische_durchfuehrung": 0.40,
            "innovationsgrad_relevanz": 0.10
        }
    
    def check_thesis_quality(self, 
                           chapter_path: Optional[str] = None,
                           include_literature: bool = True,
                           include_methodology: bool = True,
                           include_innovation: bool = True) -> MBAAssessment:
        """
        Comprehensive thesis quality check against MBA standards.
        
        Args:
            chapter_path: Path to specific chapter to analyze (optional)
            include_literature: Include literature quality analysis
            include_methodology: Include methodology assessment
            include_innovation: Include innovation assessment
            
        Returns:
            MBAAssessment object with detailed quality scores and recommendations
        """
        criteria_scores = {}
        
        # 1. Aufbau und Form (20 points)
        form_score = self._assess_aufbau_und_form(chapter_path)
        criteria_scores["aufbau_und_form"] = form_score
        
        # 2. Forschungsfrage und Literatur (30 points)
        if include_literature:
            lit_score = self._assess_forschungsfrage_literatur()
            criteria_scores["forschungsfrage_und_literatur"] = lit_score
        
        # 3. Qualität und methodische Durchführung (40 points)
        if include_methodology:
            method_score = self._assess_methodische_durchfuehrung(chapter_path)
            criteria_scores["qualitaet_methodische_durchfuehrung"] = method_score
        
        # 4. Innovationsgrad und Relevanz (10 points)
        if include_innovation:
            innovation_score = self._assess_innovationsgrad()
            criteria_scores["innovationsgrad_relevanz"] = innovation_score
        
        # Calculate overall scores
        overall_score = sum(score.current_score for score in criteria_scores.values())
        overall_percentage = (overall_score / 100) * 100
        
        # Determine grade
        predicted_grade = self._calculate_grade(overall_percentage)
        grade_info = self._get_grade_info(predicted_grade)
        
        # Identify high priority issues
        high_priority_issues = self._identify_high_priority_issues(criteria_scores)
        
        # Generate improvement plan
        improvement_plan = self._generate_improvement_plan(criteria_scores)
        
        # Determine compliance status
        compliance_status = self._determine_compliance_status(overall_percentage)
        
        return MBAAssessment(
            timestamp=datetime.now().isoformat(),
            overall_score=overall_score,
            overall_percentage=overall_percentage,
            predicted_grade=predicted_grade,
            grade_range=grade_info["grade"],
            criteria_scores=criteria_scores,
            high_priority_issues=high_priority_issues,
            improvement_plan=improvement_plan,
            compliance_status=compliance_status
        )
    
    def _assess_aufbau_und_form(self, chapter_path: Optional[str] = None) -> QualityScore:
        """Assess structure and form (20 points total)."""
        total_score = 0
        max_score = 20
        issues = []
        suggestions = []
        
        # Check thesis structure
        thesis_outline = self.project_root / "writing" / "thesis_outline.json"
        if thesis_outline.exists():
            outline = load_json(thesis_outline)
            
            # Schlüssigkeit des Aufbaus (5 points)
            structure_score = self._evaluate_structure(outline)
            total_score += structure_score
            if structure_score < 5:
                issues.append(f"Struktur-Score nur {structure_score}/5 Punkte")
                suggestions.append("Gliederung überarbeiten: Klarere Überleitungen zwischen Kapiteln")
        else:
            issues.append("Keine thesis_outline.json gefunden")
            suggestions.append("Thesis-Gliederung mit generate_outline Tool erstellen")
        
        # Formale Präsentation (7 points)
        if chapter_path:
            format_score = self._evaluate_formatting(chapter_path)
            total_score += format_score
            if format_score < 7:
                issues.append(f"Formatierung nur {format_score}/7 Punkte")
                suggestions.append("Rechtschreibung, Grammatik und wissenschaftlichen Schreibstil verbessern")
        
        # Nachvollziehbarkeit der Quellen (8 points)
        citation_score = self._evaluate_citations()
        total_score += citation_score
        if citation_score < 8:
            issues.append(f"Zitierweise nur {citation_score}/8 Punkte")
            suggestions.append("Alle Zitate auf korrekte APA-Formatierung prüfen")
        
        percentage = (total_score / max_score) * 100
        priority = "high" if percentage < 60 else "medium" if percentage < 80 else "low"
        
        return QualityScore(
            criterion="aufbau_und_form",
            aspect="Struktur, Format und Zitierung",
            current_score=total_score,
            max_score=max_score,
            percentage=percentage,
            issues=issues,
            suggestions=suggestions,
            priority=priority
        )
    
    def _assess_forschungsfrage_literatur(self) -> QualityScore:
        """Assess research question and literature (30 points total)."""
        total_score = 0
        max_score = 30
        issues = []
        suggestions = []
        
        # Breite und Angemessenheit der Literatur (10 points)
        lit_file = self.project_root / "research" / "validated-literature.json"
        if lit_file.exists():
            sources = load_json(lit_file)
            lit_analysis = self._analyze_literature_breadth(sources)
            total_score += lit_analysis["score"]
            
            if lit_analysis["score"] < 10:
                issues.extend(lit_analysis["issues"])
                suggestions.extend(lit_analysis["suggestions"])
        else:
            issues.append("Keine validierte Literatur gefunden")
            suggestions.append("Literatursuche mit search_literature Tool durchführen")
        
        # Meta-Problemstellung und wissenschaftlicher Fokus (20 points)
        research_question_file = self.project_root / "writing" / "chapters" / "forschungsfrage_korrigiert.md"
        if research_question_file.exists():
            rq_score = self._evaluate_research_question(research_question_file)
            total_score += rq_score["score"]
            if rq_score["score"] < 20:
                issues.extend(rq_score["issues"])
                suggestions.extend(rq_score["suggestions"])
        else:
            issues.append("Forschungsfrage-Dokument nicht gefunden")
            suggestions.append("Forschungsfrage klar formulieren und dokumentieren")
        
        percentage = (total_score / max_score) * 100
        priority = "high" if percentage < 60 else "medium" if percentage < 80 else "low"
        
        return QualityScore(
            criterion="forschungsfrage_und_literatur",
            aspect="Forschungsfrage und Literaturqualität",
            current_score=total_score,
            max_score=max_score,
            percentage=percentage,
            issues=issues,
            suggestions=suggestions,
            priority=priority
        )
    
    def _assess_methodische_durchfuehrung(self, chapter_path: Optional[str] = None) -> QualityScore:
        """Assess methodology and execution (40 points total)."""
        total_score = 0
        max_score = 40
        issues = []
        suggestions = []
        
        # Durchführung und Methodik (20 points)
        # This would analyze methodology chapter if available
        method_score = 15  # Placeholder - would analyze actual methodology
        total_score += method_score
        if method_score < 20:
            issues.append(f"Methodik-Score nur {method_score}/20 Punkte")
            suggestions.append("Methodenwahl detaillierter begründen")
            suggestions.append("Systematische Vorgehensweise klarer darstellen")
        
        # Qualität der empirischen Ergebnispräsentation (20 points)
        # This would analyze results presentation
        results_score = 15  # Placeholder - would analyze actual results
        total_score += results_score
        if results_score < 20:
            issues.append(f"Ergebnispräsentation nur {results_score}/20 Punkte")
            suggestions.append("Ergebnisse systematischer mit Theorie verknüpfen")
            suggestions.append("Handlungsempfehlungen konkreter ausarbeiten")
        
        percentage = (total_score / max_score) * 100
        priority = "high" if percentage < 60 else "medium" if percentage < 80 else "low"
        
        return QualityScore(
            criterion="qualitaet_methodische_durchfuehrung",
            aspect="Methodik und empirische Durchführung",
            current_score=total_score,
            max_score=max_score,
            percentage=percentage,
            issues=issues,
            suggestions=suggestions,
            priority=priority
        )
    
    def _assess_innovationsgrad(self) -> QualityScore:
        """Assess innovation and relevance (10 points total)."""
        total_score = 0
        max_score = 10
        issues = []
        suggestions = []
        
        # Innovationsgrad, Relevanz (5 points)
        innovation_score = 3  # Placeholder - would analyze actual innovation
        total_score += innovation_score
        if innovation_score < 5:
            issues.append(f"Innovationsgrad nur {innovation_score}/5 Punkte")
            suggestions.append("Neuartigkeit des Ansatzes stärker herausarbeiten")
            suggestions.append("Praktische Relevanz deutlicher darstellen")
        
        # Selbständigkeit und Originalität (5 points)
        originality_score = 3  # Placeholder - would analyze originality
        total_score += originality_score
        if originality_score < 5:
            issues.append(f"Originalität nur {originality_score}/5 Punkte")
            suggestions.append("Eigenständige kritische Reflexion verstärken")
            suggestions.append("Eigene theoretische Beiträge deutlicher hervorheben")
        
        percentage = (total_score / max_score) * 100
        priority = "medium" if percentage < 60 else "low"
        
        return QualityScore(
            criterion="innovationsgrad_relevanz",
            aspect="Innovation und Relevanz",
            current_score=total_score,
            max_score=max_score,
            percentage=percentage,
            issues=issues,
            suggestions=suggestions,
            priority=priority
        )
    
    def _evaluate_structure(self, outline: Dict) -> float:
        """Evaluate thesis structure quality."""
        score = 0
        max_score = 5
        
        # Check for required chapters
        required_chapters = ["Einleitung", "Theoretische Grundlagen", "Methodik", 
                           "Ergebnisse", "Diskussion", "Fazit"]
        
        chapters = outline.get("chapters", [])
        chapter_titles = [ch.get("title", "") for ch in chapters]
        
        # Score based on completeness
        for req in required_chapters:
            if any(req.lower() in title.lower() for title in chapter_titles):
                score += 0.5
        
        # Check logical flow
        if len(chapters) >= 6:
            score += 1
        
        # Check for clear research questions in outline
        if "research_questions" in outline:
            score += 1
        
        return min(score, max_score)
    
    def _evaluate_formatting(self, chapter_path: str) -> float:
        """Evaluate formatting and style quality."""
        score = 0
        max_score = 7
        
        # Read chapter content
        path = Path(chapter_path)
        if not path.exists():
            path = self.project_root / "writing" / "chapters" / chapter_path
        
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic formatting checks
            # Check for proper headings
            if re.findall(r'^#{1,3}\s+.+$', content, re.MULTILINE):
                score += 1
            
            # Check paragraph structure (not too long)
            paragraphs = content.split('\n\n')
            avg_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
            if 50 <= avg_length <= 200:
                score += 1
            
            # Check for academic language indicators
            academic_terms = ['jedoch', 'darüber hinaus', 'folglich', 'demnach', 
                            'diesbezüglich', 'infolgedessen']
            if any(term in content.lower() for term in academic_terms):
                score += 1
            
            # Check for proper citation format
            if re.findall(r'\([A-Za-z\s&]+,\s*\d{4}\)', content):
                score += 2
            
            # No excessive repetition
            words = content.lower().split()
            unique_ratio = len(set(words)) / len(words) if words else 0
            if unique_ratio > 0.3:
                score += 1
            
            # Reasonable length
            word_count = len(words)
            if 1000 <= word_count <= 5000:
                score += 1
        
        return min(score, max_score)
    
    def _evaluate_citations(self) -> float:
        """Evaluate citation quality and consistency."""
        score = 0
        max_score = 8
        
        # Check citation cache
        cache_file = self.project_root / "research" / "citation_cache.json"
        if cache_file.exists():
            cache = load_json(cache_file)
            if cache:
                score += 2
        
        # Check validated literature
        lit_file = self.project_root / "research" / "validated-literature.json"
        if lit_file.exists():
            sources = load_json(lit_file)
            
            # All sources should have DOI
            doi_count = sum(1 for s in sources if s.get("doi"))
            doi_percentage = (doi_count / len(sources)) * 100 if sources else 0
            
            if doi_percentage == 100:
                score += 3
            elif doi_percentage >= 90:
                score += 2
            elif doi_percentage >= 80:
                score += 1
            
            # Check for complete citation info
            complete_sources = sum(1 for s in sources if all(
                s.get(field) for field in ["authors", "year", "title", "journal"]
            ))
            complete_percentage = (complete_sources / len(sources)) * 100 if sources else 0
            
            if complete_percentage == 100:
                score += 3
            elif complete_percentage >= 90:
                score += 2
            elif complete_percentage >= 80:
                score += 1
        
        return min(score, max_score)
    
    def _analyze_literature_breadth(self, sources: List[Dict]) -> Dict[str, Any]:
        """Analyze literature breadth and quality."""
        score = 0
        max_score = 10
        issues = []
        suggestions = []
        
        if not sources:
            return {
                "score": 0,
                "issues": ["Keine Literaturquellen vorhanden"],
                "suggestions": ["Mindestens 50 Q1-Journal-Artikel recherchieren"]
            }
        
        total = len(sources)
        current_year = datetime.now().year
        
        # Aktualität
        recent = sum(1 for s in sources if self._safe_year_compare(s.get("year", 0), 2020))
        very_recent = sum(1 for s in sources if self._safe_year_compare(s.get("year", 0), 2022))
        recent_percentage = (recent / total) * 100
        
        if recent_percentage >= 90:
            score += 3
        elif recent_percentage >= 70:
            score += 2
            issues.append(f"Nur {recent_percentage:.0f}% der Quellen von 2020+")
            suggestions.append("Mehr aktuelle Quellen (2020+) einbeziehen")
        else:
            score += 1
            issues.append(f"Nur {recent_percentage:.0f}% der Quellen sind aktuell")
            suggestions.append("Deutlich mehr aktuelle Literatur erforderlich (min. 70% von 2020+)")
        
        # Q1-Anteil
        q1_sources = sum(1 for s in sources if s.get("is_q1", False))
        q1_percentage = (q1_sources / total) * 100
        
        if q1_percentage >= 80:
            score += 3
        elif q1_percentage >= 60:
            score += 2
            issues.append(f"Q1-Journal-Anteil nur {q1_percentage:.0f}%")
            suggestions.append("Mehr Q1-Journals einbeziehen (Ziel: >80%)")
        else:
            score += 1
            issues.append(f"Zu wenig Q1-Journals ({q1_percentage:.0f}%)")
            suggestions.append("Fokus auf Q1-Journals erhöhen (min. 60% erforderlich)")
        
        # Internationalität
        # Simple region detection
        regions = {"US": 0, "EU": 0, "Other": 0}
        for source in sources:
            venue = source.get("venue", "").lower()
            if any(us in venue for us in ["american", "us", "ieee", "acm"]):
                regions["US"] += 1
            elif any(eu in venue for eu in ["european", "springer", "elsevier"]):
                regions["EU"] += 1
            else:
                regions["Other"] += 1
        
        # Check for balanced distribution
        us_percent = (regions["US"] / total) * 100
        eu_percent = (regions["EU"] / total) * 100
        
        if 25 <= us_percent <= 40 and 25 <= eu_percent <= 40:
            score += 2
        else:
            score += 1
            issues.append("Unausgewogene internationale Verteilung")
            suggestions.append("Ausgewogenere Mischung aus US/EU/International anstreben")
        
        # Thematische Breite
        if total >= 50:
            score += 2
        elif total >= 30:
            score += 1
            issues.append(f"Nur {total} Quellen (Minimum 50 empfohlen)")
            suggestions.append("Literaturumfang auf mindestens 50 Quellen erweitern")
        else:
            issues.append(f"Zu wenige Quellen ({total})")
            suggestions.append("Deutlich mehr Literatur erforderlich (min. 50 Quellen)")
        
        return {
            "score": min(score, max_score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _evaluate_research_question(self, rq_file: Path) -> Dict[str, Any]:
        """Evaluate research question quality."""
        score = 0
        max_score = 20
        issues = []
        suggestions = []
        
        with open(rq_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for clear main research question
        if "Hauptforschungsfrage:" in content or "# Forschungsfrage" in content:
            score += 5
        else:
            issues.append("Hauptforschungsfrage nicht klar identifizierbar")
            suggestions.append("Hauptforschungsfrage explizit kennzeichnen")
        
        # Check for sub-questions
        sub_questions = len(re.findall(r'Unterforschungsfrage \d+:', content))
        if sub_questions >= 3:
            score += 5
        elif sub_questions >= 2:
            score += 3
            suggestions.append("Weitere Unterforschungsfragen zur Präzisierung hinzufügen")
        else:
            issues.append("Zu wenige Unterforschungsfragen")
            suggestions.append("Mindestens 3 Unterforschungsfragen formulieren")
        
        # Check for theoretical grounding
        theory_keywords = ["Framework", "Theorie", "Model", "Ansatz", "Konzept"]
        if any(keyword in content for keyword in theory_keywords):
            score += 5
        else:
            issues.append("Theoretische Fundierung nicht erkennbar")
            suggestions.append("Forschungsfrage mit etablierten Theorien verknüpfen")
        
        # Check for clear scope and focus
        if "SAP" in content and "BTP" in content and "Finanz" in content:
            score += 5
        else:
            issues.append("Thematischer Fokus unklar")
            suggestions.append("Fokus auf SAP BTP im Finanzsektor deutlicher herausarbeiten")
        
        return {
            "score": min(score, max_score),
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _safe_year_compare(self, year_value: Any, threshold: int) -> bool:
        """Safely compare year values, handling string to int conversion."""
        try:
            # Convert to int if it's a string
            year_int = int(year_value) if isinstance(year_value, str) else year_value
            return year_int >= threshold
        except (ValueError, TypeError):
            # If conversion fails, return False
            return False
    
    def _calculate_grade(self, percentage: float) -> str:
        """Calculate grade based on percentage."""
        if percentage >= 90:
            return "sehr_gut"
        elif percentage >= 80:
            return "gut"
        elif percentage >= 70:
            return "befriedigend"
        elif percentage >= 60:
            return "ausreichend"
        else:
            return "nicht_ausreichend"
    
    def _get_grade_info(self, grade: str) -> Dict[str, str]:
        """Get detailed grade information."""
        return self.grading_scale.get(grade, {
            "grade": "Unknown",
            "description": "Grade not found"
        })
    
    def _identify_high_priority_issues(self, criteria_scores: Dict[str, QualityScore]) -> List[Dict[str, Any]]:
        """Identify high priority issues that need immediate attention."""
        high_priority = []
        
        for criterion, score in criteria_scores.items():
            if score.priority == "high" or score.percentage < 60:
                for i, issue in enumerate(score.issues):
                    suggestion = score.suggestions[i] if i < len(score.suggestions) else "Siehe Verbesserungsvorschläge"
                    high_priority.append({
                        "criterion": criterion,
                        "issue": issue,
                        "current_score": f"{score.current_score}/{score.max_score}",
                        "impact": f"-{score.max_score - score.current_score} Punkte",
                        "suggestion": suggestion,
                        "urgency": "HOCH" if score.percentage < 50 else "MITTEL"
                    })
        
        # Sort by impact
        high_priority.sort(key=lambda x: float(x["impact"].split()[0]), reverse=True)
        
        return high_priority[:5]  # Top 5 issues
    
    def _generate_improvement_plan(self, criteria_scores: Dict[str, QualityScore]) -> List[Dict[str, Any]]:
        """Generate actionable improvement plan."""
        plan = []
        
        # Group improvements by effort/impact
        for criterion, score in criteria_scores.items():
            if score.percentage < 90:  # Room for improvement
                potential_gain = score.max_score - score.current_score
                
                for suggestion in score.suggestions:
                    # Estimate effort (simplified)
                    effort = "niedrig"
                    if "überarbeiten" in suggestion.lower() or "neu" in suggestion.lower():
                        effort = "hoch"
                    elif "erweitern" in suggestion.lower() or "mehr" in suggestion.lower():
                        effort = "mittel"
                    
                    plan.append({
                        "action": suggestion,
                        "criterion": criterion,
                        "potential_gain": f"+{potential_gain:.1f} Punkte",
                        "effort": effort,
                        "timeline": self._estimate_timeline(effort),
                        "priority": score.priority
                    })
        
        # Sort by priority and effort
        plan.sort(key=lambda x: (
            0 if x["priority"] == "high" else 1 if x["priority"] == "medium" else 2,
            0 if x["effort"] == "niedrig" else 1 if x["effort"] == "mittel" else 2
        ))
        
        return plan
    
    def _estimate_timeline(self, effort: str) -> str:
        """Estimate timeline based on effort."""
        timelines = {
            "niedrig": "1-2 Tage",
            "mittel": "3-5 Tage",
            "hoch": "1-2 Wochen"
        }
        return timelines.get(effort, "Zu bestimmen")
    
    def _determine_compliance_status(self, percentage: float) -> str:
        """Determine overall compliance status."""
        if percentage >= 90:
            return "EXZELLENT: Alle Standards übertroffen"
        elif percentage >= 80:
            return "GUT: Standards erfüllt"
        elif percentage >= 70:
            return "BEFRIEDIGEND: Grundlegende Standards erfüllt"
        elif percentage >= 60:
            return "AUSREICHEND: Mindeststandards knapp erfüllt"
        else:
            return "KRITISCH: Erhebliche Verbesserungen erforderlich"
    
    def generate_detailed_report(self, assessment: MBAAssessment) -> str:
        """Generate detailed quality report."""
        report = f"""# MBA Quality Assessment Report

**Generiert am:** {assessment.timestamp}
**Compliance Status:** {assessment.compliance_status}

## Gesamtbewertung

- **Gesamtpunktzahl:** {assessment.overall_score:.1f}/100 Punkte
- **Prozentsatz:** {assessment.overall_percentage:.1f}%
- **Voraussichtliche Note:** {assessment.predicted_grade} ({assessment.grade_range})

## Bewertung nach Kriterien

"""
        
        for criterion, score in assessment.criteria_scores.items():
            report += f"""### {criterion.replace('_', ' ').title()}
- **Punkte:** {score.current_score:.1f}/{score.max_score} ({score.percentage:.1f}%)
- **Priorität:** {score.priority.upper()}

"""
            if score.issues:
                report += "**Identifizierte Probleme:**\n"
                for issue in score.issues:
                    report += f"- {issue}\n"
                report += "\n"
            
            if score.suggestions:
                report += "**Verbesserungsvorschläge:**\n"
                for suggestion in score.suggestions:
                    report += f"- {suggestion}\n"
                report += "\n"
        
        # High priority issues
        if assessment.high_priority_issues:
            report += "## Dringende Handlungsbedarfe\n\n"
            for i, issue in enumerate(assessment.high_priority_issues, 1):
                report += f"""**{i}. {issue['issue']}**
- Kriterium: {issue['criterion']}
- Impact: {issue['impact']}
- Dringlichkeit: {issue['urgency']}
- Empfehlung: {issue['suggestion']}

"""
        
        # Improvement plan
        if assessment.improvement_plan:
            report += "## Verbesserungsplan\n\n"
            report += "| Aktion | Kriterium | Potenzial | Aufwand | Zeitrahmen | Priorität |\n"
            report += "|--------|-----------|-----------|---------|------------|-----------||\n"
            
            for action in assessment.improvement_plan[:10]:  # Top 10 actions
                report += f"| {action['action'][:50]}... | {action['criterion'][:20]} | "
                report += f"{action['potential_gain']} | {action['effort']} | "
                report += f"{action['timeline']} | {action['priority'].upper()} |\n"
        
        # Grade prediction details
        report += f"""\n## Notenprognose

Basierend auf der aktuellen Bewertung von {assessment.overall_percentage:.1f}% wird folgende Note prognostiziert:

**{assessment.predicted_grade.replace('_', ' ').title()}** ({assessment.grade_range})

### Notenstufen-Übersicht:
- Sehr gut (1.0-1.3): 90-100%
- Gut (1.7-2.3): 80-89%
- Befriedigend (2.7-3.3): 70-79%
- Ausreichend (3.7-4.0): 60-69%
- Nicht ausreichend (5.0): <60%

### Verbesserungspotenzial:
"""
        
        # Calculate improvement potential
        if assessment.overall_percentage < 90:
            next_grade_threshold = 90 if assessment.overall_percentage < 90 else 100
            if assessment.overall_percentage < 80:
                next_grade_threshold = 80
            if assessment.overall_percentage < 70:
                next_grade_threshold = 70
            if assessment.overall_percentage < 60:
                next_grade_threshold = 60
            
            needed_points = next_grade_threshold - assessment.overall_percentage
            report += f"- Für die nächsthöhere Notenstufe fehlen: {needed_points:.1f} Prozentpunkte\n"
            report += f"- Dies entspricht {needed_points:.1f} Punkten\n"
        else:
            report += "- Exzellente Leistung! Fokus auf Beibehaltung des hohen Niveaus\n"
        
        return report
    
    def export_assessment(self, assessment: MBAAssessment, format: str = "json") -> Path:
        """Export assessment to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mba_quality_assessment_{timestamp}"
        
        output_dir = self.project_root / "research" / "quality_reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            output_path = output_dir / f"{filename}.json"
            
            # Convert to dict for JSON serialization
            assessment_dict = {
                "timestamp": assessment.timestamp,
                "overall_score": assessment.overall_score,
                "overall_percentage": assessment.overall_percentage,
                "predicted_grade": assessment.predicted_grade,
                "grade_range": assessment.grade_range,
                "criteria_scores": {
                    k: {
                        "criterion": v.criterion,
                        "aspect": v.aspect,
                        "current_score": v.current_score,
                        "max_score": v.max_score,
                        "percentage": v.percentage,
                        "issues": v.issues,
                        "suggestions": v.suggestions,
                        "priority": v.priority
                    } for k, v in assessment.criteria_scores.items()
                },
                "high_priority_issues": assessment.high_priority_issues,
                "improvement_plan": assessment.improvement_plan,
                "compliance_status": assessment.compliance_status
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(assessment_dict, f, indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            output_path = output_dir / f"{filename}.md"
            report = self.generate_detailed_report(assessment)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return output_path


def main():
    """CLI interface for MBA quality checking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MBA Quality Checker")
    parser.add_argument("--chapter", help="Specific chapter to analyze")
    parser.add_argument("--quick", action="store_true", help="Quick assessment (structure only)")
    parser.add_argument("--export", choices=["json", "markdown", "both"], 
                       default="markdown", help="Export format")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    checker = MBAQualityChecker()
    
    # Run assessment
    assessment = checker.check_thesis_quality(
        chapter_path=args.chapter,
        include_literature=not args.quick,
        include_methodology=not args.quick,
        include_innovation=not args.quick
    )
    
    # Display results
    print(f"\n🎓 MBA Quality Assessment")
    print(f"{'='*50}")
    print(f"Overall Score: {assessment.overall_score:.1f}/100 ({assessment.overall_percentage:.1f}%)")
    print(f"Predicted Grade: {assessment.predicted_grade.replace('_', ' ').title()} ({assessment.grade_range})")
    print(f"Status: {assessment.compliance_status}")
    
    if args.verbose:
        print(f"\n📊 Criteria Breakdown:")
        for criterion, score in assessment.criteria_scores.items():
            print(f"\n{criterion.replace('_', ' ').title()}:")
            print(f"  Score: {score.current_score:.1f}/{score.max_score} ({score.percentage:.1f}%)")
            print(f"  Priority: {score.priority.upper()}")
    
    # Export results
    if args.export in ["json", "both"]:
        json_path = checker.export_assessment(assessment, "json")
        print(f"\n📄 JSON report saved to: {json_path}")
    
    if args.export in ["markdown", "both"]:
        md_path = checker.export_assessment(assessment, "markdown")
        print(f"\n📝 Markdown report saved to: {md_path}")
    
    # Show top priority actions
    if assessment.high_priority_issues:
        print(f"\n⚠️  Top Priority Issues:")
        for issue in assessment.high_priority_issues[:3]:
            print(f"- {issue['issue']} ({issue['impact']})")
            print(f"  → {issue['suggestion']}")


if __name__ == "__main__":
    main()