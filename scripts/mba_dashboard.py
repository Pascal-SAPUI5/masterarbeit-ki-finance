#!/usr/bin/env python3
"""
MBA Quality Dashboard
Real-time quality monitoring and grade prediction for master thesis
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

# Import quality control modules
try:
    from citation_quality_control import CitationQualityControl
    from utils import get_project_root, load_json
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from citation_quality_control import CitationQualityControl
    from utils import get_project_root, load_json

class MBAQualityDashboard:
    def __init__(self):
        self.project_root = get_project_root()
        self.config_file = self.project_root / "config" / "mba-standards.json"
        self.standards = self._load_standards()
        self.citation_qc = CitationQualityControl()
        
    def _load_standards(self) -> Dict:
        """Load MBA standards configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def calculate_score(self) -> Dict[str, any]:
        """Calculate overall quality score."""
        scores = {
            "aufbau_und_form": self._score_structure_form(),
            "forschungsfrage_und_literatur": self._score_research_literature(),
            "qualitaet_methodische_durchfuehrung": self._score_methodology(),
            "innovationsgrad_relevanz": self._score_innovation(),
        }
        
        # Calculate weighted total
        total_score = 0
        max_score = 0
        for category, category_scores in scores.items():
            if category in self.standards.get("evaluation_criteria", {}):
                weight = self.standards["evaluation_criteria"][category]["weight"]
                total_points = self.standards["evaluation_criteria"][category]["total_points"]
                
                category_score = sum(category_scores.values())
                total_score += category_score * weight
                max_score += total_points * weight
                
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        grade = self._calculate_grade(percentage)
        
        return {
            "category_scores": scores,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": percentage,
            "grade": grade,
            "timestamp": datetime.now()
        }
    
    def _score_structure_form(self) -> Dict[str, float]:
        """Score structure and form criteria."""
        scores = {}
        criteria = self.standards["evaluation_criteria"]["aufbau_und_form"]["aspects"]
        
        # Check thesis structure
        thesis_files = list((self.project_root / "writing" / "chapters").glob("*.md"))
        structure_score = min(len(thesis_files) / 10 * 5, 5)  # Max 5 points
        scores["schluessigkeit_aufbau"] = structure_score
        
        # Check formal presentation (based on file count and organization)
        formal_score = 7 if len(thesis_files) > 5 else 4
        scores["formale_praesentation"] = formal_score
        
        # Check citation quality
        citation_score = self._check_citation_quality() * 8  # Max 8 points
        scores["nachvollziehbarkeit_quellen"] = citation_score
        
        return scores
    
    def _score_research_literature(self) -> Dict[str, float]:
        """Score research and literature criteria."""
        scores = {}
        
        # Load validated literature
        lit_file = self.project_root / "research" / "validated-literature.json"
        if lit_file.exists():
            literature = load_json(lit_file)
        else:
            literature = []
        
        # Check literature breadth
        if len(literature) > 50:
            breadth_score = 10
        elif len(literature) > 30:
            breadth_score = 7
        elif len(literature) > 15:
            breadth_score = 5
        else:
            breadth_score = 3
        scores["breite_literatur"] = breadth_score
        
        # Check research question quality
        research_file = self.project_root / "writing" / "chapters" / "forschungsfrage_korrigiert.md"
        if research_file.exists():
            question_score = 15  # Assume good if corrected version exists
        else:
            question_score = 10
        scores["meta_problemstellung"] = question_score
        
        return scores
    
    def _score_methodology(self) -> Dict[str, float]:
        """Score methodology and execution."""
        scores = {}
        
        # Basic scoring based on project maturity
        # In a real implementation, this would analyze actual methodology files
        scores["durchfuehrung_methodik"] = 15  # Placeholder
        scores["qualitaet_empirische_ergebnisse"] = 12  # Placeholder
        
        return scores
    
    def _score_innovation(self) -> Dict[str, float]:
        """Score innovation and relevance."""
        scores = {}
        
        # Check for innovative aspects
        scores["innovationsgrad_nutzen"] = 4  # Placeholder
        scores["selbstaendigkeit_originalitaet"] = 3  # Placeholder
        
        return scores
    
    def _check_citation_quality(self) -> float:
        """Check overall citation quality (0-1 scale)."""
        # Check all chapter files
        chapter_dir = self.project_root / "writing" / "chapters"
        if not chapter_dir.exists():
            return 0.5
        
        total_valid = 0
        total_citations = 0
        
        for chapter_file in chapter_dir.glob("*.md"):
            result = self.citation_qc.check_document_citations(str(chapter_file))
            if "total_citations" in result:
                total_citations += result["total_citations"]
                total_valid += result["valid_citations"]
        
        if total_citations == 0:
            return 0.5
        
        return total_valid / total_citations
    
    def _calculate_grade(self, percentage: float) -> Dict[str, str]:
        """Calculate grade based on percentage."""
        grading_scale = self.standards.get("grading_scale", {})
        
        if percentage >= 90:
            return grading_scale.get("sehr_gut", {"grade": "1.0", "description": "Sehr gut"})
        elif percentage >= 80:
            return grading_scale.get("gut", {"grade": "1.7", "description": "Gut"})
        elif percentage >= 70:
            return grading_scale.get("befriedigend", {"grade": "2.7", "description": "Befriedigend"})
        elif percentage >= 60:
            return grading_scale.get("ausreichend", {"grade": "3.7", "description": "Ausreichend"})
        else:
            return grading_scale.get("nicht_ausreichend", {"grade": "5.0", "description": "Nicht ausreichend"})
    
    def get_critical_issues(self) -> List[Dict[str, str]]:
        """Identify critical issues that need immediate attention."""
        issues = []
        
        # Check literature count
        lit_file = self.project_root / "research" / "validated-literature.json"
        if lit_file.exists():
            literature = load_json(lit_file)
            if len(literature) < 20:
                issues.append({
                    "severity": "critical",
                    "category": "Literature",
                    "issue": f"Only {len(literature)} sources found. Minimum 30-50 required.",
                    "action": "Add more high-quality, recent sources from Q1 journals"
                })
        
        # Check citation quality
        citation_quality = self._check_citation_quality()
        if citation_quality < 0.8:
            issues.append({
                "severity": "warning",
                "category": "Citations",
                "issue": f"Citation quality at {citation_quality:.0%}. Should be above 80%.",
                "action": "Review and correct citation formatting"
            })
        
        # Check chapter completeness
        chapters = list((self.project_root / "writing" / "chapters").glob("*.md"))
        if len(chapters) < 5:
            issues.append({
                "severity": "critical",
                "category": "Structure",
                "issue": f"Only {len(chapters)} chapters found. Full thesis structure needed.",
                "action": "Complete all required thesis chapters"
            })
        
        return issues
    
    def generate_quality_report(self) -> str:
        """Generate a detailed quality report."""
        score_data = self.calculate_score()
        issues = self.get_critical_issues()
        
        report = f"""# MBA Thesis Quality Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Score
- **Total Points**: {score_data['total_score']:.1f} / {score_data['max_score']:.0f}
- **Percentage**: {score_data['percentage']:.1f}%
- **Predicted Grade**: {score_data['grade']['grade']} - {score_data['grade']['description']}

## Category Breakdown
"""
        
        for category, scores in score_data['category_scores'].items():
            category_info = self.standards['evaluation_criteria'].get(category, {})
            category_total = sum(scores.values())
            category_max = category_info.get('total_points', 0)
            
            report += f"\n### {category.replace('_', ' ').title()}\n"
            report += f"- Score: {category_total:.1f} / {category_max} points\n"
            report += f"- Weight: {category_info.get('weight', 0) * 100:.0f}%\n\n"
            
            for aspect, score in scores.items():
                aspect_info = category_info.get('aspects', {}).get(aspect, {})
                max_points = aspect_info.get('points', 0)
                report += f"  - {aspect}: {score:.1f} / {max_points} points\n"
        
        if issues:
            report += "\n## Critical Issues\n"
            for issue in issues:
                severity_icon = "🔴" if issue['severity'] == 'critical' else "🟡"
                report += f"\n{severity_icon} **{issue['category']}**: {issue['issue']}\n"
                report += f"   - Action: {issue['action']}\n"
        
        report += "\n## Recommendations for Grade Improvement\n"
        if score_data['percentage'] < 90:
            report += "1. **Expand Literature Base**: Add 10-15 more Q1 journal sources\n"
            report += "2. **Strengthen Methodology**: Document research approach in detail\n"
            report += "3. **Enhance Innovation**: Highlight unique contributions clearly\n"
            report += "4. **Perfect Citations**: Ensure 100% APA compliance\n"
        
        return report

def main():
    st.set_page_config(
        page_title="MBA Thesis Quality Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 MBA Thesis Quality Dashboard")
    st.markdown("Real-time quality monitoring and grade prediction")
    
    # Initialize dashboard
    dashboard = MBAQualityDashboard()
    
    # Calculate current scores
    score_data = dashboard.calculate_score()
    
    # Create layout columns
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Display overall grade with color coding
        grade = score_data['grade']['grade']
        grade_color = "green" if float(grade) <= 2.0 else "orange" if float(grade) <= 3.0 else "red"
        
        st.metric(
            label="Predicted Grade",
            value=grade,
            delta=score_data['grade']['description']
        )
        
        # Grade gauge chart
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score_data['percentage'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Score %"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 60], 'color': "lightgray"},
                    {'range': [60, 70], 'color': "yellow"},
                    {'range': [70, 80], 'color': "orange"},
                    {'range': [80, 90], 'color': "lightgreen"},
                    {'range': [90, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        st.metric(
            label="Total Score",
            value=f"{score_data['total_score']:.1f} / {score_data['max_score']:.0f}",
            delta=f"{score_data['percentage']:.1f}%"
        )
        
        # Critical issues
        issues = dashboard.get_critical_issues()
        critical_count = len([i for i in issues if i['severity'] == 'critical'])
        warning_count = len([i for i in issues if i['severity'] == 'warning'])
        
        st.metric(
            label="Critical Issues",
            value=critical_count,
            delta=f"{warning_count} warnings"
        )
        
        if issues:
            st.warning(f"Found {len(issues)} issues requiring attention")
    
    with col3:
        # Literature metrics
        lit_file = dashboard.project_root / "research" / "validated-literature.json"
        lit_count = len(load_json(lit_file)) if lit_file.exists() else 0
        
        st.metric(
            label="Literature Sources",
            value=lit_count,
            delta="30-50 recommended"
        )
        
        # Citation quality
        citation_quality = dashboard._check_citation_quality()
        st.metric(
            label="Citation Quality",
            value=f"{citation_quality:.0%}",
            delta="80%+ target"
        )
    
    # Category breakdown chart
    st.subheader("📈 Score Breakdown by Category")
    
    category_data = []
    for category, scores in score_data['category_scores'].items():
        category_info = dashboard.standards['evaluation_criteria'].get(category, {})
        category_total = sum(scores.values())
        category_max = category_info.get('total_points', 0)
        category_percentage = (category_total / category_max * 100) if category_max > 0 else 0
        
        category_data.append({
            'Category': category.replace('_', ' ').title(),
            'Score': category_total,
            'Max Score': category_max,
            'Percentage': category_percentage,
            'Weight': category_info.get('weight', 0) * 100
        })
    
    df_categories = pd.DataFrame(category_data)
    
    # Create stacked bar chart
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        name='Achieved Score',
        x=df_categories['Category'],
        y=df_categories['Score'],
        marker_color='lightblue',
        text=df_categories['Percentage'].round(1).astype(str) + '%',
        textposition='auto'
    ))
    
    fig_bar.add_trace(go.Bar(
        name='Remaining Points',
        x=df_categories['Category'],
        y=df_categories['Max Score'] - df_categories['Score'],
        marker_color='lightgray'
    ))
    
    fig_bar.update_layout(
        barmode='stack',
        title='Category Scores vs Maximum',
        xaxis_title='Category',
        yaxis_title='Points',
        height=400
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed category analysis
    st.subheader("📊 Detailed Category Analysis")
    
    tabs = st.tabs(list(score_data['category_scores'].keys()))
    
    for idx, (category, scores) in enumerate(score_data['category_scores'].items()):
        with tabs[idx]:
            category_info = dashboard.standards['evaluation_criteria'].get(category, {})
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Aspect scores
                aspect_data = []
                for aspect, score in scores.items():
                    aspect_info = category_info.get('aspects', {}).get(aspect, {})
                    max_points = aspect_info.get('points', 0)
                    percentage = (score / max_points * 100) if max_points > 0 else 0
                    
                    aspect_data.append({
                        'Aspect': aspect.replace('_', ' ').title(),
                        'Score': score,
                        'Max': max_points,
                        'Percentage': percentage
                    })
                
                df_aspects = pd.DataFrame(aspect_data)
                
                # Create horizontal bar chart
                fig_aspects = px.bar(
                    df_aspects,
                    x='Percentage',
                    y='Aspect',
                    orientation='h',
                    title=f'{category.replace("_", " ").title()} - Aspect Scores',
                    labels={'Percentage': 'Score %'},
                    text='Percentage'
                )
                
                fig_aspects.update_traces(
                    texttemplate='%{text:.1f}%',
                    textposition='outside'
                )
                
                fig_aspects.update_layout(
                    xaxis_range=[0, 105],
                    height=300
                )
                
                st.plotly_chart(fig_aspects, use_container_width=True)
            
            with col2:
                # Category description and tips
                st.markdown(f"**Weight**: {category_info.get('weight', 0) * 100:.0f}%")
                st.markdown(f"**Total Points**: {category_info.get('total_points', 0)}")
                
                # Improvement tips
                st.markdown("**Improvement Tips:**")
                for aspect, score in scores.items():
                    aspect_info = category_info.get('aspects', {}).get(aspect, {})
                    max_points = aspect_info.get('points', 0)
                    if score < max_points * 0.8:
                        st.markdown(f"- Improve {aspect.replace('_', ' ')}")
    
    # Critical issues section
    issues = dashboard.get_critical_issues()
    if issues:
        st.subheader("⚠️ Critical Issues & Warnings")
        
        for issue in issues:
            severity_color = "red" if issue['severity'] == 'critical' else "orange"
            with st.expander(f"{issue['category']} - {issue['severity'].upper()}", expanded=True):
                st.markdown(f"**Issue**: {issue['issue']}")
                st.markdown(f"**Recommended Action**: {issue['action']}")
    
    # Export functionality
    st.subheader("📄 Export Quality Report")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("Generate and download a comprehensive quality report with all metrics and recommendations.")
    
    with col2:
        if st.button("Generate Report", type="primary"):
            report = dashboard.generate_quality_report()
            
            # Save report
            report_path = dashboard.project_root / "research" / "quality_reports" / f"quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            
            st.success(f"Report saved to: {report_path}")
            
            # Download button
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"mba_quality_report_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
    
    # Auto-refresh option
    with st.sidebar:
        st.header("Settings")
        auto_refresh = st.checkbox("Auto-refresh (30s)")
        
        if auto_refresh:
            st.markdown("Dashboard will refresh every 30 seconds")
            st.experimental_rerun()
        
        # Threshold settings
        st.subheader("Quality Thresholds")
        min_literature = st.slider("Min. Literature Sources", 20, 100, 50)
        min_citation_quality = st.slider("Min. Citation Quality %", 50, 100, 80)
        
        # Last update time
        st.markdown(f"**Last Update**: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()