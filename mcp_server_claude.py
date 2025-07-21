#!/usr/bin/env python3
"""
MCP Server für Claude Code - Masterarbeit KI Finance

Dieser Server implementiert das vollständige Workflow-Framework für die Masterarbeit
mit automatischer MBA-Standards Compliance und Memory System Integration.
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Importiere die Projekt-Module
sys.path.insert(0, str(Path(__file__).parent))

from mcp_server import MasterarbeitMCPServer

class ClaudeMCPServer(MasterarbeitMCPServer):
    """MCP Server angepasst für Claude Code."""
    
    async def handle_json_rpc(self, data: str) -> str:
        """Handle JSON-RPC 2.0 protocol."""
        try:
            request = json.loads(data)
            
            # JSON-RPC 2.0 Format
            method = request.get("method", "")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # Map to internal format
            internal_request = {
                "method": method,
                "params": params
            }
            
            # Handle request
            result = await self.handle_request(internal_request)
            
            # Format response
            if "error" in result:
                response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": result["error"]
                    },
                    "id": request_id
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }
            
            return json.dumps(response)
            
        except json.JSONDecodeError as e:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                    "data": str(e)
                },
                "id": None
            }
            return json.dumps(response)
        except Exception as e:
            response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                },
                "id": request_id if 'request_id' in locals() else None
            }
            return json.dumps(response)

async def main():
    """Main function for Claude Code MCP Server."""
    server = ClaudeMCPServer()
    
    # Send initialization response
    init_response = {
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "tools": True,
                "resources": True,
                "prompts": True
            },
            "serverInfo": {
                "name": "masterarbeit-ki-finance",
                "version": "1.0.0"
            }
        },
        "id": "init"
    }
    print(json.dumps(init_response))
    sys.stdout.flush()
    
    # Process requests
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            response = await server.handle_json_rpc(line.strip())
            print(response)
            sys.stdout.flush()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Server error: {str(e)}"
                },
                "id": None
            }
            print(json.dumps(error_response))
            sys.stdout.flush()

if __name__ == "__main__":
    asyncio.run(main())