"""Compatibility entrypoint exposing the configured MCP server instance."""

from leap_docweaver_mcp.app import create_mcp

mcp = create_mcp()
