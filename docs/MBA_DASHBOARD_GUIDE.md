# MBA Quality Dashboard Guide

## Overview
The MBA Quality Dashboard provides real-time monitoring of your master thesis quality, with automatic grade prediction based on official MBA evaluation criteria.

## Features

### 1. Real-Time Quality Scoring
- **Overall Score**: Continuous calculation of thesis quality (0-100 points)
- **Grade Prediction**: Automatic grade calculation (1.0 - 5.0 scale)
- **Category Breakdown**: Detailed scoring for each evaluation criterion

### 2. Visual Analytics
- **Grade Gauge**: Visual representation of overall performance
- **Category Charts**: Stacked bar charts showing achievement vs. potential
- **Aspect Analysis**: Detailed breakdown of sub-criteria performance
- **Progress Tracking**: Monitor improvements over time

### 3. Critical Issues Detection
- **Automatic Issue Detection**: Identifies problems requiring immediate attention
- **Severity Classification**: Critical (🔴) and Warning (🟡) levels
- **Actionable Recommendations**: Specific steps to resolve each issue

### 4. Quality Metrics
- **Literature Count**: Tracks number of validated sources
- **Citation Quality**: Percentage of properly formatted citations
- **Structure Completeness**: Monitors thesis chapter completion
- **Innovation Score**: Measures originality and contribution

## Evaluation Categories

### 1. Aufbau und Form (20%)
- Schlüssigkeit des Aufbaus (5 points)
- Formale Präsentation (7 points)
- Nachvollziehbarkeit der Quellen (8 points)

### 2. Forschungsfrage und Literatur (30%)
- Breite der Literatur (10 points)
- Meta-Problemstellung (20 points)

### 3. Qualität der methodischen Durchführung (40%)
- Durchführung und Methodik (20 points)
- Qualität der empirischen Ergebnisse (20 points)

### 4. Innovationsgrad und Relevanz (10%)
- Innovationsgrad und Nutzen (5 points)
- Selbständigkeit und Originalität (5 points)

## Usage

### Starting the Dashboard
```bash
# From project root
./scripts/run_dashboard.sh

# Or manually
streamlit run scripts/mba_dashboard.py
```

### Dashboard URL
Once started, access the dashboard at: http://localhost:8501

### Navigation
1. **Main View**: Overall scores and critical metrics
2. **Category Tabs**: Detailed analysis of each evaluation criterion
3. **Export**: Generate and download quality reports
4. **Settings**: Configure thresholds and auto-refresh

## Quality Report Export

The dashboard can generate comprehensive quality reports including:
- Overall score and grade prediction
- Detailed category breakdowns
- Critical issues and warnings
- Specific improvement recommendations
- Timestamp and tracking information

Reports are saved to: `research/quality_reports/`

## Improvement Strategies

### To Achieve "Sehr Gut" (90%+)
1. **Literature**: 50+ sources, 80%+ from Q1 journals, 90%+ from 2020+
2. **Citations**: 100% APA compliance, all DOIs available
3. **Structure**: Complete thesis with clear transitions
4. **Methodology**: Systematic, transparent approach
5. **Innovation**: Clear unique contributions

### Common Issues and Solutions
- **Low Literature Score**: Add more recent Q1 journal sources
- **Citation Errors**: Use citation quality control tool
- **Structure Issues**: Complete all required chapters
- **Innovation Gap**: Highlight unique SAP BTP applications

## Integration with Other Tools

The dashboard integrates with:
- `citation_quality_control.py`: Validates citation formatting
- `manage_references.py`: Manages literature database
- `research_assistant.py`: Helps find quality sources
- MBA standards configuration: `config/mba-standards.json`

## Technical Requirements
- Python 3.8+
- Streamlit
- Plotly
- Pandas
- NumPy

## Troubleshooting

### Dashboard Won't Start
- Check virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install streamlit plotly pandas numpy`

### No Data Showing
- Ensure literature database exists: `research/validated-literature.json`
- Check thesis chapters: `writing/chapters/`

### Grade Calculation Issues
- Verify MBA standards file: `config/mba-standards.json`
- Check evaluation criteria weights sum to 1.0

## Future Enhancements
- Historical tracking with trend analysis
- Peer comparison benchmarks
- AI-powered improvement suggestions
- Integration with citation managers
- Automated daily reports