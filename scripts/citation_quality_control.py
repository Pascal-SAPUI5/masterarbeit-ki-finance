#!/usr/bin/env python3
"""
Citation Quality Control Module
Ensures citations meet academic standards
Integrated with MBA Quality Checker for comprehensive assessment
"""
import re
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from scripts.utils import get_project_root, load_json

class CitationQualityControl:
    def __init__(self):
        self.project_root = get_project_root()
        self.references = self._load_references()
        self.quality_criteria = {
            "min_year": 2020,
            "required_fields": ["authors", "year", "title", "journal"],
            "q1_journals": self._load_q1_journals()
        }
    
    def _load_references(self) -> List[Dict]:
        """Load validated references."""
        ref_file = self.project_root / "research" / "validated-literature.json"
        if ref_file.exists():
            return load_json(ref_file)
        return []
    
    def _load_q1_journals(self) -> List[str]:
        """Load list of Q1 journals."""
        # In production, this would load from a database
        return [
            "Nature", "Science", "Cell", "BMJ", "JAMA", "Lancet",
            "Journal of Finance", "Journal of Financial Economics",
            "Review of Financial Studies", "Journal of Banking & Finance",
            "Information Systems Research", "MIS Quarterly",
            "Journal of Management Information Systems"
        ]
    
    def verify_citation(self, text: str, source: str) -> Dict[str, any]:
        """Verify a citation and return formatted version."""
        result = {
            "original_text": text,
            "source": source,
            "valid": False,
            "formatted_citation": "",
            "issues": [],
            "suggestions": []
        }
        
        # Find matching reference
        ref = self._find_reference(source)
        if not ref:
            result["issues"].append("Reference not found in database")
            result["suggestions"].append("Add reference to validated literature first")
            return result
        
        # Check quality criteria
        quality_issues = self._check_quality(ref)
        if quality_issues:
            result["issues"].extend(quality_issues)
        
        # Format citation
        result["formatted_citation"] = self._format_citation(text, ref)
        result["full_reference"] = self._format_full_reference(ref)
        
        # Mark as valid if no critical issues
        result["valid"] = len([i for i in result["issues"] if "critical" in i.lower()]) == 0
        
        return result
    
    def _find_reference(self, source: str) -> Optional[Dict]:
        """Find reference by author/year pattern."""
        # Extract author and year from source
        match = re.search(r"(\w+).*?(\d{4})", source)
        if match:
            author, year = match.groups()
            for ref in self.references:
                ref_authors = ref.get("authors", [])
                if ref_authors and author.lower() in ref_authors[0].lower() and ref.get("year") == year:
                    return ref
        return None
    
    def _check_quality(self, ref: Dict) -> List[str]:
        """Check if reference meets quality criteria."""
        issues = []
        
        # Check year
        year = int(ref.get("year", 0))
        if year < self.quality_criteria["min_year"]:
            issues.append(f"Publication year {year} is before minimum {self.quality_criteria['min_year']}")
        
        # Check required fields
        for field in self.quality_criteria["required_fields"]:
            if not ref.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Check journal quality
        journal = ref.get("journal", "")
        if journal and journal not in self.quality_criteria["q1_journals"]:
            if ref.get("quartile") != "Q1" and ref.get("impact_factor", 0) < 3.0:
                issues.append("Journal may not meet Q1 quality criteria")
        
        return issues
    
    def _format_citation(self, text: str, ref: Dict) -> str:
        """Format in-text citation properly."""
        authors = ref.get("authors", [])
        year = ref.get("year", "n.d.")
        
        if len(authors) == 1:
            citation = f"({authors[0].split(',')[0]}, {year})"
        elif len(authors) == 2:
            author1 = authors[0].split(',')[0]
            author2 = authors[1].split(',')[0]
            citation = f"({author1} & {author2}, {year})"
        else:
            citation = f"({authors[0].split(',')[0]} et al., {year})"
        
        # Add page number if provided
        page_match = re.search(r"[Ss]\.\s*(\d+)", text)
        if page_match:
            citation = citation[:-1] + f", S. {page_match.group(1)})"
        
        return f"{text} {citation}"
    
    def _format_full_reference(self, ref: Dict) -> str:
        """Format full reference in APA style."""
        authors = ref.get("authors", [])
        
        # Format authors
        if len(authors) > 7:
            author_str = ", ".join(authors[:6]) + ", ... " + authors[-1]
        else:
            author_str = ", ".join(authors)
        
        # Basic format
        reference = f"{author_str} ({ref.get('year', 'n.d.')}). {ref.get('title', 'Untitled')}."
        
        # Add journal info
        if ref.get("journal"):
            reference += f" {ref.get('journal')}"
            if ref.get("volume"):
                reference += f", {ref.get('volume')}"
                if ref.get("issue"):
                    reference += f"({ref.get('issue')})"
                if ref.get("pages"):
                    reference += f", {ref.get('pages')}"
            reference += "."
        
        # Add DOI
        if ref.get("doi"):
            reference += f" https://doi.org/{ref.get('doi')}"
        
        return reference
    
    def analyze_text_citations(self, text: str) -> Dict[str, any]:
        """Analyze text for citation opportunities and quality."""
        analysis = {
            "total_citations": 0,
            "missing_citations": [],
            "suggestions": {},
            "quality_score": 0,
            "research_needed_count": 0
        }
        
        # Find existing citations
        citation_patterns = [
            r'\(([A-Za-z\s&]+,\s*\d{4})\)',  # (Author, 2020)
            r'\(([A-Za-z\s]+et al\.,\s*\d{4})\)',  # (Author et al., 2020)
            r'([A-Za-z\s&]+)\s*\((\d{4})\)',  # Author (2020)
        ]
        
        existing_citations = []
        for pattern in citation_patterns:
            existing_citations.extend(re.findall(pattern, text))
        
        analysis["total_citations"] = len(existing_citations)
        
        # Count [Research Needed] markers
        research_needed_markers = re.findall(r'\[Research Needed[:\s]*([^\]]*)\]', text)
        analysis["research_needed_count"] = len(research_needed_markers)
        
        # Identify sentences that might need citations
        sentences = re.split(r'[.!?]+', text)
        
        # Keywords that typically require citations
        citation_keywords = [
            "studies show", "research indicates", "according to", "has been shown",
            "demonstrated that", "evidence suggests", "findings reveal", "analysis shows",
            "previous work", "literature review", "systematic review", "meta-analysis",
            "empirical evidence", "theoretical framework", "conceptual model"
        ]
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if not sentence_lower:
                continue
                
            # Check if sentence needs citation
            needs_citation = False
            for keyword in citation_keywords:
                if keyword in sentence_lower:
                    needs_citation = True
                    break
            
            # Check if sentence already has citation
            has_citation = False
            for pattern in citation_patterns:
                if re.search(pattern, sentence):
                    has_citation = True
                    break
            
            if needs_citation and not has_citation:
                analysis["missing_citations"].append(sentence.strip())
        
        # Generate citation suggestions based on content topics
        topics = self._extract_topics(text)
        
        for topic in topics:
            # Find relevant references from our database
            relevant_refs = self._find_relevant_references(topic)
            if relevant_refs:
                analysis["suggestions"][topic] = {
                    "sources": relevant_refs[:5],  # Top 5 relevant sources
                    "citation_format": self._format_suggestions(relevant_refs[:3])
                }
        
        # Calculate quality score
        total_sentences = len([s for s in sentences if s.strip()])
        if total_sentences > 0:
            citation_density = analysis["total_citations"] / total_sentences
            missing_ratio = len(analysis["missing_citations"]) / total_sentences
            
            # Score based on citation density and missing citations
            analysis["quality_score"] = max(0, min(100, 
                int(100 * citation_density * 2 - missing_ratio * 50)))
        
        return analysis
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract main topics from text for citation suggestions."""
        topics = []
        
        # Common research topics in the field
        topic_keywords = {
            "AI agents": ["AI agent", "artificial intelligence agent", "intelligent agent"],
            "financial services": ["finance", "banking", "financial sector", "fintech"],
            "process automation": ["automation", "RPA", "process optimization"],
            "knowledge management": ["knowledge", "information management", "data governance"],
            "SAP BTP": ["SAP", "BTP", "business technology platform"],
            "systematic review": ["PRISMA", "systematic literature", "meta-analysis"]
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def _find_relevant_references(self, topic: str) -> List[Dict]:
        """Find references relevant to a topic."""
        relevant = []
        
        for ref in self.references:
            # Check title and abstract for topic relevance
            title = ref.get("title", "").lower()
            abstract = ref.get("abstract", "").lower()
            
            if topic.lower() in title or topic.lower() in abstract:
                relevant.append(ref)
        
        # Sort by quality (Q1 first) and year (newest first)
        relevant.sort(key=lambda x: (
            x.get("quartile") != "Q1",
            -int(x.get("year", 0))
        ))
        
        return relevant
    
    def _format_suggestions(self, refs: List[Dict]) -> List[str]:
        """Format citation suggestions."""
        suggestions = []
        
        for ref in refs:
            authors = ref.get("authors", [])
            year = ref.get("year", "n.d.")
            
            if len(authors) == 1:
                citation = f"({authors[0].split(',')[0]}, {year})"
            elif len(authors) == 2:
                author1 = authors[0].split(',')[0]
                author2 = authors[1].split(',')[0]
                citation = f"({author1} & {author2}, {year})"
            else:
                citation = f"({authors[0].split(',')[0]} et al., {year})"
            
            suggestions.append(citation)
        
        return suggestions
    
    def generate_quality_report(self, analysis: Dict[str, any]) -> str:
        """Generate a citation quality report."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.project_root / "output" / f"citation_report_{timestamp}.md"
        
        report = f"""# Citation Quality Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary
- Total Citations: {analysis['total_citations']}
- Quality Score: {analysis['quality_score']}/100
- Missing Citations: {len(analysis['missing_citations'])}

## Missing Citations
The following sentences appear to need citations:

"""
        
        for i, sentence in enumerate(analysis['missing_citations'], 1):
            report += f"{i}. {sentence}\n\n"
        
        if analysis['suggestions']:
            report += "\n## Citation Suggestions by Topic\n\n"
            
            for topic, data in analysis['suggestions'].items():
                report += f"### {topic}\n"
                report += "Suggested citations:\n"
                for citation in data['citation_format']:
                    report += f"- {citation}\n"
                report += "\n"
        
        # Save report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return str(report_path)
    
    def verify_source(self, source_info: Dict[str, any]) -> Dict[str, any]:
        """
        Verify a source citation and return verification details.
        
        Args:
            source_info: Dictionary containing source information with fields like:
                        title, authors, year, journal, doi, etc.
        
        Returns:
            Dictionary with verification results:
            {
                'verified': bool,     # Overall verification status
                'valid': bool,        # Alias for verified (backward compatibility)
                'issues': List[str],  # List of validation issues
                'details': Dict,      # Detailed verification information
                'errors': List[str]   # Deprecated alias for issues
            }
        """
        if not isinstance(source_info, dict):
            return {
                'verified': False,
                'valid': False,
                'issues': ['Invalid source format: expected dictionary'],
                'details': {'error': 'Source must be a dictionary'},
                'errors': ['Invalid source format: expected dictionary']
            }
        
        issues = []
        details = {
            'source_id': source_info.get('id', 'unknown'),
            'title': source_info.get('title', ''),
            'verification_timestamp': self._get_timestamp(),
            'quality_checks': {}
        }
        
        # Check required fields
        required_fields = self.quality_criteria.get("required_fields", ["authors", "year", "title", "journal"])
        missing_fields = []
        
        for field in required_fields:
            if not source_info.get(field):
                missing_fields.append(field)
                issues.append(f"Missing required field: {field}")
        
        details['quality_checks']['required_fields'] = {
            'required': required_fields,
            'missing': missing_fields,
            'passed': len(missing_fields) == 0
        }
        
        # Validate year
        year_valid = True
        try:
            year = source_info.get('year')
            if year:
                year_int = int(year) if isinstance(year, str) else year
                min_year = self.quality_criteria.get("min_year", 2020)
                
                if year_int < min_year:
                    issues.append(f"Publication year {year_int} is before minimum required year {min_year}")
                    year_valid = False
                elif year_int > 2025:  # Reasonable upper bound
                    issues.append(f"Publication year {year_int} appears to be in the future")
                    year_valid = False
        except (ValueError, TypeError):
            issues.append(f"Invalid year format: {source_info.get('year')}")
            year_valid = False
        
        details['quality_checks']['year'] = {
            'value': source_info.get('year'),
            'valid': year_valid,
            'min_required': self.quality_criteria.get("min_year", 2020)
        }
        
        # Validate authors
        authors = source_info.get('authors', [])
        authors_valid = True
        
        if not authors:
            issues.append("No authors specified")
            authors_valid = False
        elif not isinstance(authors, list):
            issues.append("Authors should be provided as a list")
            authors_valid = False
        elif len(authors) == 0:
            issues.append("Authors list is empty")
            authors_valid = False
        
        details['quality_checks']['authors'] = {
            'count': len(authors) if isinstance(authors, list) else 0,
            'valid': authors_valid,
            'names': authors if isinstance(authors, list) else []
        }
        
        # Validate journal quality
        journal = source_info.get('journal', '')
        journal_quality = self._assess_journal_quality(source_info)
        
        details['quality_checks']['journal'] = journal_quality
        
        if not journal_quality['is_quality_journal']:
            issues.append(journal_quality['message'])
        
        # Check DOI format if present
        doi = source_info.get('doi', '')
        doi_valid = True
        
        if doi:
            # Basic DOI format validation
            if not re.match(r'^10\.\d+/.+', doi):
                issues.append(f"Invalid DOI format: {doi}")
                doi_valid = False
        
        details['quality_checks']['doi'] = {
            'present': bool(doi),
            'valid': doi_valid,
            'value': doi
        }
        
        # Check for additional quality indicators
        quality_indicators = []
        if source_info.get('impact_factor'):
            try:
                impact_factor = float(source_info['impact_factor'])
                quality_indicators.append(f"Impact Factor: {impact_factor}")
                details['quality_checks']['impact_factor'] = impact_factor
            except (ValueError, TypeError):
                issues.append(f"Invalid impact factor: {source_info.get('impact_factor')}")
        
        if source_info.get('quartile'):
            quartile = source_info['quartile']
            quality_indicators.append(f"Quartile: {quartile}")
            details['quality_checks']['quartile'] = quartile
        
        details['quality_indicators'] = quality_indicators
        
        # Overall verification status
        verified = len(issues) == 0
        
        # Determine severity of issues
        critical_issues = [issue for issue in issues if any(keyword in issue.lower() 
                          for keyword in ['missing required', 'invalid format', 'no authors'])]
        
        if critical_issues:
            verified = False
            details['critical_issues'] = critical_issues
        
        result = {
            'verified': verified,
            'valid': verified,  # Backward compatibility
            'issues': issues,
            'details': details,
            'errors': issues  # Backward compatibility
        }
        
        return result
    
    def _assess_journal_quality(self, source_info: Dict[str, any]) -> Dict[str, any]:
        """Assess the quality of a journal."""
        journal = source_info.get('journal', '')
        
        # Check if it's in our Q1 journals list
        q1_journals = self.quality_criteria.get("q1_journals", [])
        is_q1_listed = any(q1_journal.lower() in journal.lower() for q1_journal in q1_journals)
        
        # Check quartile information
        quartile = source_info.get('quartile', '').upper()
        impact_factor = source_info.get('impact_factor', 0)
        
        try:
            impact_factor = float(impact_factor) if impact_factor else 0
        except (ValueError, TypeError):
            impact_factor = 0
        
        is_quality_journal = False
        message = ""
        
        if is_q1_listed:
            is_quality_journal = True
            message = f"Journal '{journal}' is in Q1 journals list"
        elif quartile == 'Q1':
            is_quality_journal = True
            message = f"Journal '{journal}' is marked as Q1"
        elif impact_factor >= 3.0:
            is_quality_journal = True
            message = f"Journal '{journal}' has high impact factor ({impact_factor})"
        else:
            message = f"Journal '{journal}' quality cannot be verified (not in Q1 list, impact factor: {impact_factor})"
        
        return {
            'journal_name': journal,
            'is_q1_listed': is_q1_listed,
            'quartile': quartile,
            'impact_factor': impact_factor,
            'is_quality_journal': is_quality_journal,
            'message': message
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for verification records."""
        from datetime import datetime
        return datetime.now().isoformat()

    def check_document_citations(self, file_path: str) -> Dict[str, any]:
        """Check all citations in a document."""
        path = Path(file_path)
        if not path.exists():
            path = self.project_root / "writing" / "chapters" / file_path
        
        if not path.exists():
            return {"error": "File not found"}
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all citations (various patterns)
        citation_patterns = [
            r'\(([A-Za-z\s&]+,\s*\d{4})\)',  # (Author, 2020)
            r'\(([A-Za-z\s]+et al\.,\s*\d{4})\)',  # (Author et al., 2020)
            r'([A-Za-z\s&]+)\s*\((\d{4})\)',  # Author (2020)
        ]
        
        citations = []
        for pattern in citation_patterns:
            citations.extend(re.findall(pattern, content))
        
        # Verify each citation
        results = {
            "file": str(file_path),
            "total_citations": len(citations),
            "valid_citations": 0,
            "issues": [],
            "details": []
        }
        
        for citation in citations:
            if isinstance(citation, tuple):
                citation = " ".join(citation)
            
            verification = self.verify_citation("", citation)
            if verification["valid"]:
                results["valid_citations"] += 1
            else:
                results["issues"].append(f"Invalid citation: {citation}")
            
            results["details"].append(verification)
        
        return results

def main():
    """CLI interface for citation quality control."""
    import argparse
    parser = argparse.ArgumentParser(description="Citation quality control")
    parser.add_argument("--verify", help="Verify a citation")
    parser.add_argument("--source", help="Source reference")
    parser.add_argument("--check-file", help="Check all citations in a file")
    
    args = parser.parse_args()
    
    qc = CitationQualityControl()
    
    if args.verify and args.source:
        result = qc.verify_citation(args.verify, args.source)
        print(f"Valid: {result['valid']}")
        print(f"Formatted: {result['formatted_citation']}")
        if result['issues']:
            print(f"Issues: {', '.join(result['issues'])}")
    
    elif args.check_file:
        result = qc.check_document_citations(args.check_file)
        print(f"Total citations: {result['total_citations']}")
        print(f"Valid citations: {result['valid_citations']}")
        if result['issues']:
            print("\nIssues found:")
            for issue in result['issues']:
                print(f"- {issue}")
    
    else:
        print("Citation Quality Control Tool")
        print("\nUsage:")
        print("  --verify <text> --source <reference> : Verify a single citation")
        print("  --check-file <path>                  : Check all citations in a file")
        print("\nFor comprehensive MBA quality checking, use:")
        print("  python scripts/mba_quality_checker.py --check-file <path> --full-report")

if __name__ == "__main__":
    main()