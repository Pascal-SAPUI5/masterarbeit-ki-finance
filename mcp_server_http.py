#!/usr/bin/env python3
"""
HTTP wrapper for MCP Server - allows the MCP server to run as a web service
"""

import json
import asyncio
from aiohttp import web
from pathlib import Path
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the MCP server
sys.path.insert(0, str(Path(__file__).parent))
from mcp_server_claude import ClaudeMCPServer

class MCPHTTPServer:
    def __init__(self):
        self.mcp_server = ClaudeMCPServer()
        logger.info("MCP HTTP Server initialized")
    
    async def health(self, request):
        """Health check endpoint."""
        return web.json_response({"status": "healthy", "service": "mcp-server"})
    
    async def handle_request(self, request):
        """Handle MCP requests via HTTP POST."""
        try:
            data = await request.json()
            logger.info(f"Received request: {data.get('method', 'unknown')}")
            
            # Convert to JSON-RPC format if needed
            if "jsonrpc" not in data:
                data = {
                    "jsonrpc": "2.0",
                    "method": data.get("method", ""),
                    "params": data.get("params", {}),
                    "id": data.get("id", 1)
                }
            
            # Process through MCP server
            response_str = await self.mcp_server.handle_json_rpc(json.dumps(data))
            
            # Check if response is empty (for notifications)
            if not response_str or response_str.strip() == '':
                # For notifications (no id), don't return a response
                if "id" not in data:
                    return web.Response(status=204)
                # For regular requests with empty response
                return web.json_response({
                    "jsonrpc": "2.0",
                    "result": None,
                    "id": data.get("id")
                })
            
            try:
                response = json.loads(response_str)
                return web.json_response(response)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}, response was: {response_str}")
                # Return proper error structure instead of 204
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Response parsing error: {str(e)}"
                    },
                    "id": data.get("id")
                }, status=500)
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            logger.error(f"Request data was: {data}")
            # Check if this was a notification (no id field)
            if "id" not in data:
                # For notifications that errored, return proper error structure
                return web.json_response({
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Notification processing error: {str(e)}"
                    },
                    "id": data.get("id", 1)
                }, status=500)
            return web.json_response({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": data.get("id")
            }, status=500)
    
    async def capabilities(self, request):
        """Return server capabilities."""
        return web.json_response({
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "serverInfo": {
                    "name": "masterarbeit-ki-finance",
                    "version": "0.1.0"
                }
            },
            "id": "capabilities"
        })

async def create_app():
    """Create the web application."""
    server = MCPHTTPServer()
    
    app = web.Application()
    app.router.add_get('/health', server.health)
    app.router.add_get('/capabilities', server.capabilities)
    app.router.add_post('/', server.handle_request)
    app.router.add_post('/mcp', server.handle_request)
    
    return app

if __name__ == '__main__':
    logger.info("Starting MCP HTTP Server on port 3000...")
    app = asyncio.run(create_app())
    web.run_app(app, host='0.0.0.0', port=3000)