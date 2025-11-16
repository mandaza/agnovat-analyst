#!/usr/bin/env python3
"""
MCP Server Wrapper for Claude Desktop
Wraps the Agnovat Analyst FastAPI server for stdio MCP communication
"""

import sys
import json
import asyncio
import httpx
from typing import Any, Dict
from loguru import logger

# Configure logger to stderr only (stdout is for MCP protocol)
logger.remove()
logger.add(sys.stderr, level="INFO")


class MCPStdioServer:
    """MCP Server that communicates via stdio with Claude Desktop"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = None

    async def initialize(self):
        """Initialize HTTP client"""
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        logger.info(f"MCP Server initialized, connecting to {self.base_url}")

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request from Claude Desktop"""
        try:
            method = request.get("method")
            params = request.get("params", {})

            logger.info(f"Handling MCP request: {method}")

            # Handle notifications (no response needed)
            if method and method.startswith("notifications/"):
                logger.info(f"Received notification: {method}, no response needed")
                return None  # No response for notifications

            if method == "initialize":
                return await self.handle_initialize(params)
            elif method == "tools/list":
                return await self.handle_list_tools(params)
            elif method == "tools/call":
                return await self.handle_call_tool(params)
            else:
                return {
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}",
                    }
                }

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {"error": {"code": -32603, "message": f"Internal error: {str(e)}"}}

    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request"""
        logger.info("Initializing MCP server")

        # Get client's protocol version
        client_version = params.get("protocolVersion", "2024-11-05")
        logger.info(f"Client protocol version: {client_version}")

        # Check if FastAPI server is running
        try:
            response = await self.client.get("/health")
            if response.status_code != 200:
                raise Exception("FastAPI server not healthy")
            logger.info("Backend server is healthy")
        except Exception as e:
            logger.error(f"FastAPI server not available: {e}")
            return {
                "error": {
                    "code": -32002,
                    "message": "Backend server not available. Please start: uvicorn app.main:app --reload",
                }
            }

        return {
            "result": {
                "protocolVersion": client_version,  # Match client's version
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "agnovat-analyst",
                    "version": "1.0.0",
                },
            }
        }

    async def handle_list_tools(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all available tools"""
        logger.info("Listing tools")

        try:
            # Fetch OpenAPI spec from FastAPI
            response = await self.client.get("/openapi.json")
            if response.status_code != 200:
                raise Exception("Cannot fetch tools")

            spec = response.json()
            paths = spec.get("paths", {})

            # Convert API endpoints to MCP tools
            tools = []
            for path, methods in paths.items():
                if path.startswith("/api/"):
                    for method, details in methods.items():
                        if method.lower() == "post":
                            tool_name = path.split("/")[-1]
                            description = details.get("summary", "")

                            tools.append(
                                {
                                    "name": tool_name,
                                    "description": description,
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": details.get("requestBody", {})
                                        .get("content", {})
                                        .get("application/json", {})
                                        .get("schema", {})
                                        .get("properties", {}),
                                    },
                                }
                            )

            logger.info(f"Found {len(tools)} tools")
            return {"result": {"tools": tools}}

        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return {"error": {"code": -32603, "message": str(e)}}

    async def handle_call_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Calling tool: {tool_name}")

        try:
            # Map tool name to endpoint
            endpoint_map = {
                # PDF Processing
                "extract-text": "/api/pdf/extract-text",
                "generate-hash": "/api/pdf/generate-hash",
                "verify-integrity": "/api/pdf/verify-integrity",
                "extract-metadata": "/api/pdf/extract-metadata",
                # Analysis
                "analyze-racism-bias": "/api/analysis/analyze-racism-bias",
                "detect-inconsistencies": "/api/analysis/detect-inconsistencies",
                "detect-template-reuse": "/api/analysis/detect-template-reuse",
                "detect-omitted-context": "/api/analysis/detect-omitted-context",
                "detect-non-evidence-based": "/api/analysis/detect-non-evidence-based",
                "extract-family-support": "/api/analysis/extract-family-support",
                "extract-pg-limitations": "/api/analysis/extract-pg-limitations",
                "compare-documents": "/api/analysis/compare-documents",
                "analyze-and-compare": "/api/analysis/analyze-and-compare",
                "extract-timeline": "/api/analysis/extract-timeline",
                "contradiction-matrix": "/api/analysis/contradiction-matrix",
                # Legal Framework
                "human-rights-breaches": "/api/legal/human-rights-breaches",
                "guardianship-risk-assessment": "/api/legal/guardianship-risk-assessment",
                "detect-state-guardianship-bias": "/api/legal/detect-state-guardianship-bias",
                "professional-language-compliance": "/api/legal/professional-language-compliance",
                "goals-guardianship-alignment": "/api/legal/goals-guardianship-alignment",
                # Reports
                "guardianship-argument": "/api/reports/guardianship-argument",
                "qcat-evidence-summary": "/api/reports/qcat-evidence-summary",
                "qcat-bundle": "/api/reports/qcat-bundle",
            }

            endpoint = endpoint_map.get(tool_name)
            if not endpoint:
                return {
                    "error": {"code": -32602, "message": f"Unknown tool: {tool_name}"}
                }

            # Call the FastAPI endpoint
            response = await self.client.post(endpoint, json=arguments)

            if response.status_code == 200:
                result = response.json()
                # Format result as text for Claude
                formatted_result = json.dumps(result, indent=2)
                return {
                    "result": {
                        "content": [{"type": "text", "text": formatted_result}]
                    }
                }
            else:
                error_detail = response.text
                logger.error(f"Tool call failed: {error_detail}")
                return {
                    "error": {
                        "code": response.status_code,
                        "message": f"Tool execution failed: {error_detail}",
                    }
                }

        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": {"code": -32603, "message": str(e)}}

    async def run(self):
        """Main loop - read from stdin, write to stdout"""
        await self.initialize()

        logger.info("MCP Server ready, listening on stdio")

        # Read JSON-RPC messages from stdin
        try:
            logger.info("Starting message loop, waiting for messages...")
            while True:
                try:
                    logger.info("Waiting for next message from stdin...")
                    line = sys.stdin.readline()
                    logger.info(f"readline() returned, length: {len(line) if line else 0}")

                    # Empty line means EOF - stdin is closed
                    if not line:
                        logger.info("stdin closed (EOF), shutting down")
                        break

                    # Skip empty lines
                    line = line.strip()
                    if not line:
                        logger.info("Empty line received, skipping")
                        continue

                    logger.info(f"Received message: {line[:100]}...")

                    request = json.loads(line)
                    request_id = request.get("id")
                    method = request.get("method")
                    logger.info(f"Processing request: method={method}, id={request_id}")

                    response = await self.handle_request(request)

                    # Skip response for notifications (None response)
                    if response is None:
                        logger.info(f"No response needed for {method}")
                        continue

                    # Add request ID to response
                    if request_id is not None:
                        response["id"] = request_id
                        response["jsonrpc"] = "2.0"

                    # Write response to stdout
                    response_str = json.dumps(response)
                    logger.info(f"Sending response for {method}: {response_str[:100]}...")
                    sys.stdout.write(response_str + "\n")
                    sys.stdout.flush()
                    logger.info(f"Response sent successfully, waiting for next message...")

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    # Don't break - continue processing other messages
                    continue
                except Exception as e:
                    logger.error(f"Error processing message: {e}", exc_info=True)
                    # Don't break on errors - keep server running
                    continue

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}", exc_info=True)
        finally:
            logger.info("MCP Server shutting down")
            await self.client.aclose()


async def main():
    """Start MCP server"""
    server = MCPStdioServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
