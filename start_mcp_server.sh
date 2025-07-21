#!/bin/bash
# Start MCP Server for Masterarbeit KI Finance

# Activate virtual environment
source venv/bin/activate

# Export project root
export PYTHONPATH=$PWD

# Start the MCP server
python mcp_server_claude.py