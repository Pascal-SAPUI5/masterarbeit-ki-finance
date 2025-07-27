#!/bin/bash
# Run MBA Quality Dashboard

echo "🚀 Starting MBA Quality Dashboard..."
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install required packages if not already installed
echo "Checking dependencies..."
pip install -q streamlit pandas plotly numpy

# Create quality reports directory if it doesn't exist
mkdir -p research/quality_reports

# Run the dashboard
echo ""
echo "📊 Dashboard starting..."
echo "Open your browser at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo "=================================="

# Run streamlit
streamlit run scripts/mba_dashboard.py --server.port 8501 --server.headless true