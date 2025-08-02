#!/bin/bash
# Wrapper script for MCP server to suppress warnings

# Set environment variables to suppress warnings
export TRANSFORMERS_NO_ADVISORY_WARNINGS=true
export HF_HUB_DISABLE_SYMLINKS_WARNING=1
export TOKENIZERS_PARALLELISM=false

# Change to project directory
cd /home/a503038/Projects/masterarbeit-ki-finance

# Run the MCP server with stderr redirected to null
exec python3 mcp_server_claude.py 2>/dev/null