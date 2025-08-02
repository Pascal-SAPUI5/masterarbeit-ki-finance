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
    
    async def initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the initialize method according to MCP protocol."""
        return {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "serverInfo": {
                "name": "masterarbeit-ki-finance",
                "version": "0.1.0"
            }
        }
    
    async def shutdown(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle the shutdown method gracefully."""
        # Perform any cleanup if needed
        return {}
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Override to handle initialize and shutdown methods."""
        method = request.get("method", "")
        params = request.get("params", {})
        
        # Handle initialize and shutdown before delegating to parent
        if method == "initialize":
            return await self.initialize(params)
        elif method == "shutdown":
            return await self.shutdown(params)
        elif method == "notifications/initialized":
            # This is a notification, just acknowledge it
            return {}
        else:
            # Delegate to parent class for all other methods
            return await super().handle_request(request)
    
    async def handle_json_rpc(self, data: str) -> str:
        """Handle JSON-RPC 2.0 protocol."""
        try:
            request = json.loads(data)
            
            # JSON-RPC 2.0 Format
            method = request.get("method", "")
            params = request.get("params", {})
            request_id = request.get("id")
            
            # Check if this is a notification (no id field)
            # Notifications should not receive a response
            is_notification = "id" not in request
            
            # Special handling for notifications
            if is_notification and method.startswith("notifications/"):
                # Process the notification but don't return a response
                # For now, we just acknowledge it internally
                return ""  # No response for notifications
            
            # Map to internal format
            internal_request = {
                "method": method,
                "params": params
            }
            
            # Handle request
            result = await self.handle_request(internal_request)
            
            # Don't send response for notifications
            if is_notification:
                return ""
            
            # Format response according to JSON-RPC 2.0 spec
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
                # For tools/call, wrap the result properly
                if method == "tools/call":
                    response = {
                        "jsonrpc": "2.0",
                        "result": {
                            "content": [
                                {
                                    "type": "text", 
                                    "text": json.dumps(result, indent=2, ensure_ascii=False)
                                }
                            ]
                        },
                        "id": request_id
                    }
                else:
                    # For other methods (list_tools, etc.), return result directly
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
    # Redirect stderr to prevent ML model loading messages from interfering
    import os
    import logging
    
    # Disable HuggingFace warnings
    os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = 'true'
    logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
    
    server = ClaudeMCPServer()
    
    # Don't send initialization response automatically - wait for request
    # Process requests
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            response = await server.handle_json_rpc(line.strip())
            # Only print non-empty responses (notifications don't get responses)
            if response:
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