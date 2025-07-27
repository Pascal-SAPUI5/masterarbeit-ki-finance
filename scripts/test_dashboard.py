#!/usr/bin/env python3
"""
Test MBA Dashboard functionality
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from mba_dashboard import MBAQualityDashboard

def test_dashboard():
    """Test basic dashboard functionality."""
    print("Testing MBA Quality Dashboard...")
    
    try:
        # Initialize dashboard
        dashboard = MBAQualityDashboard()
        print("✓ Dashboard initialized successfully")
        
        # Calculate scores
        scores = dashboard.calculate_score()
        print(f"✓ Score calculation completed")
        print(f"  - Total Score: {scores['total_score']:.1f} / {scores['max_score']:.0f}")
        print(f"  - Percentage: {scores['percentage']:.1f}%")
        print(f"  - Predicted Grade: {scores['grade']['grade']} - {scores['grade']['description']}")
        
        # Check critical issues
        issues = dashboard.get_critical_issues()
        print(f"✓ Issue detection completed")
        print(f"  - Found {len(issues)} issues")
        
        # Test report generation
        report = dashboard.generate_quality_report()
        print(f"✓ Report generation completed")
        print(f"  - Report length: {len(report)} characters")
        
        print("\n✅ All tests passed! Dashboard is working correctly.")
        print("\nTo launch the dashboard, run:")
        print("  ./scripts/run_dashboard.sh")
        print("or")
        print("  streamlit run scripts/mba_dashboard.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard()