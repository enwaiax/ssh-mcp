#!/usr/bin/env python3
"""
Integration test for SSH MCP server components using in-memory FastMCP.

This test verifies:
- SSHMCPServer initialization and tool registration
- FastMCP client integration
- MCP tool availability and basic functionality
- No actual SSH connections required
"""

import asyncio

import pytest
from fastmcp import Client
from python_src.python_ssh_mcp import SSHMCPServer
from python_src.python_ssh_mcp.models import SSHConfig


@pytest.mark.asyncio
async def test_ssh_mcp_server_integration():
    """Test SSH MCP server integration with FastMCP."""

    # Create SSH MCP server instance
    ssh_server = SSHMCPServer("test-ssh-server")
    assert ssh_server is not None
    assert ssh_server.mcp is not None

    # Initialize with dummy SSH config to register tools
    dummy_ssh_configs = {
        "test": SSHConfig(
            name="test", host="localhost", port=22, username="test", password="test"
        )
    }

    # Initialize server (SSH connection may fail, that's expected)
    try:
        await ssh_server.initialize(dummy_ssh_configs)
    except Exception:
        # SSH connection failure is expected in test environment
        # Tools should still be registered
        pass

    # Create an in-memory client for testing
    client = Client(ssh_server.mcp)
    assert client is not None

    async with client:
        # Test ping
        await client.ping()  # Should not raise exception

        # List available tools
        tool_list = await client.list_tools()
        tool_names = [tool.name for tool in tool_list]

        # Verify expected tools are present
        expected_tools = ["execute-command", "upload", "download", "list-servers"]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"Tool {expected_tool} not registered"

        # Test list-servers tool functionality
        result = await client.call_tool("list-servers", {})
        assert result is not None
        assert hasattr(result, "data")

        # Cleanup
        if ssh_server:
            try:
                await ssh_server.cleanup()
            except Exception:
                pass  # Cleanup failure is acceptable in tests


if __name__ == "__main__":
    asyncio.run(test_ssh_mcp_server_integration())
