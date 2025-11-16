#!/usr/bin/env python3
"""
MCP Server for Claude Desktop - Remote Server Version
Connects to Agnovat Analyst backend running on remote server via HTTPS

This wrapper runs on your LOCAL machine and communicates with the remote
Docker backend over HTTPS.

Architecture:
    Claude Desktop (stdio) → mcp_server_remote.py (HTTP) → Remote Server (HTTPS)
"""

import sys
import json
import asyncio
from typing import Any, Dict
import httpx
from loguru import logger

# Configure logger to stderr only (MCP uses stdio for communication)
logger.remove()
logger.add(sys.stderr, level="INFO")

# Remote server URL - CHANGE THIS TO YOUR DOMAIN
BACKEND_URL = "https://your-domain.com"

# Timeout for API requests (in seconds)
REQUEST_TIMEOUT = 300.0

# Import the MCP server base class
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from mcp_server import MCPStdioServer
except ImportError:
    logger.error("Could not import mcp_server module. Ensure mcp_server.py is in the same directory.")
    sys.exit(1)


class MCPRemoteServer(MCPStdioServer):
    """
    MCP Server for remote HTTPS backend connection.

    This class extends the base MCP server to connect to a remote
    Agnovat backend over HTTPS instead of localhost.
    """

    def __init__(self):
        """Initialize with remote backend URL."""
        super().__init__(base_url=BACKEND_URL)
        logger.info(f"Initializing MCP Remote Server")
        logger.info(f"Backend URL: {BACKEND_URL}")
        logger.info(f"Request timeout: {REQUEST_TIMEOUT}s")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to remote backend with proper error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload

        Returns:
            Response data as dictionary

        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT, verify=True) as client:
                if method.upper() == "GET":
                    response = await client.get(url)
                elif method.upper() == "POST":
                    response = await client.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Request timeout: {url}")
            raise Exception(f"Request to {url} timed out after {REQUEST_TIMEOUT}s")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise Exception(f"HTTP {e.response.status_code}: {e.response.text}")
        except httpx.ConnectError:
            logger.error(f"Connection failed: {url}")
            raise Exception(
                f"Cannot connect to remote server at {BACKEND_URL}. "
                "Please check:\n"
                "1. Server is running\n"
                "2. Domain is correct\n"
                "3. SSL certificate is valid\n"
                "4. Firewall allows HTTPS (port 443)"
            )
        except Exception as e:
            logger.error(f"Request failed: {url} - {str(e)}")
            raise


async def main():
    """Start MCP server connected to remote backend."""
    logger.info("=" * 50)
    logger.info("Agnovat Analyst MCP Server (Remote Mode)")
    logger.info("=" * 50)
    logger.info(f"Remote backend: {BACKEND_URL}")
    logger.info("Connecting to Claude Desktop via stdio...")

    # Verify backend is accessible before starting
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=True) as client:
            response = await client.get(f"{BACKEND_URL}/health")
            response.raise_for_status()
            health = response.json()
            logger.info(f"Backend health check: {health.get('status', 'unknown')}")
            logger.info("✅ Remote backend is accessible")
    except Exception as e:
        logger.error("❌ Cannot reach remote backend")
        logger.error(f"Error: {str(e)}")
        logger.error("")
        logger.error("Please verify:")
        logger.error(f"1. BACKEND_URL is correct: {BACKEND_URL}")
        logger.error("2. Server is running and accessible")
        logger.error("3. SSL certificate is valid")
        logger.error("4. Firewall allows HTTPS traffic")
        logger.error("")
        logger.error("Test manually with:")
        logger.error(f"  curl {BACKEND_URL}/health")
        sys.exit(1)

    # Start MCP server
    server = MCPRemoteServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
