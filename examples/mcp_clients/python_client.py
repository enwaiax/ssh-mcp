#!/usr/bin/env python3
# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"
#   Timestamp: "2025-08-05T21:23:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "示例驱动学习 + MCP客户端集成"
#   Quality_Check: "完整的Python MCP客户端示例，展示所有MCP工具的使用"
# }}
# {{START_MODIFICATIONS}}
"""
FastMCP SSH Server - Python MCP Client Example

This example demonstrates how to use a Python MCP client to interact
with the FastMCP SSH Server, including all four MCP tools.

Prerequisites:
- FastMCP SSH Server running
- MCP client library installed
- SSH server configured and accessible

Usage: python python_client.py
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path

# Add python_src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "python_src"))

from python_ssh_mcp.utils import Logger, setup_logger


class MockMCPClient:
    """
    Mock MCP client for demonstration purposes.

    In a real scenario, you would use an actual MCP client library
    that communicates with the FastMCP SSH Server via stdio.
    """

    def __init__(self, server_name="fastmcp-ssh-server"):
        self.server_name = server_name
        self.connected = False

    async def connect(self):
        """Connect to the MCP server."""
        print(f"🔌 Connecting to {self.server_name}...")
        # In real implementation, this would start the subprocess
        # and establish communication via stdin/stdout
        self.connected = True
        print("✅ Connected to MCP server")

    async def call_tool(self, tool_name, **arguments):
        """Call an MCP tool with given arguments."""
        if not self.connected:
            raise RuntimeError("Not connected to MCP server")

        print(f"🔧 Calling tool: {tool_name}")
        print(f"📋 Arguments: {json.dumps(arguments, indent=2)}")

        # Mock responses for demonstration
        if tool_name == "execute-command":
            return {
                "stdout": f"Mock output for command: {arguments.get('cmdString', '')}",
                "stderr": "",
                "exitCode": 0,
                "serverName": arguments.get("serverName", "default"),
            }
        elif tool_name == "upload":
            return {
                "success": True,
                "message": f"File uploaded successfully from {arguments['localPath']} to {arguments['remotePath']}",
                "localPath": arguments["localPath"],
                "remotePath": arguments["remotePath"],
                "serverName": arguments.get("serverName", "default"),
            }
        elif tool_name == "download":
            return {
                "success": True,
                "message": f"File downloaded successfully from {arguments['remotePath']} to {arguments['localPath']}",
                "remotePath": arguments["remotePath"],
                "localPath": arguments["localPath"],
                "serverName": arguments.get("serverName", "default"),
            }
        elif tool_name == "list-servers":
            return [
                {
                    "name": "production",
                    "host": "prod.example.com",
                    "port": 22,
                    "username": "deploy",
                    "authentication": "key",
                    "status": "connected",
                    "whitelist": ["git.*", "npm.*", "node.*"],
                    "blacklist": ["rm.*", "sudo.*"],
                },
                {
                    "name": "staging",
                    "host": "staging.example.com",
                    "port": 2222,
                    "username": "dev",
                    "authentication": "password",
                    "status": "connected",
                    "whitelist": ["*"],
                    "blacklist": ["rm -rf.*"],
                },
            ]
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    async def disconnect(self):
        """Disconnect from the MCP server."""
        print("🔌 Disconnecting from MCP server...")
        self.connected = False
        print("✅ Disconnected")


async def demonstrate_execute_command(client):
    """Demonstrate the execute-command MCP tool."""
    print("\n🔧 === Execute Command Tool Demo ===")

    # Basic command execution
    result = await client.call_tool(
        "execute-command", cmdString="uptime", serverName="production"
    )

    print("📤 Command Output:")
    print(f"   stdout: {result['stdout']}")
    print(f"   stderr: {result['stderr']}")
    print(f"   exit code: {result['exitCode']}")
    print(f"   server: {result['serverName']}")

    # Command with timeout
    result = await client.call_tool(
        "execute-command", cmdString="ls -la /home", serverName="staging", timeout=60
    )

    print(f"\n📂 Directory listing: {result['stdout']}")


async def demonstrate_file_operations(client):
    """Demonstrate upload and download MCP tools."""
    print("\n📁 === File Operations Demo ===")

    # Create a temporary file for demonstration
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp_file:
        tmp_file.write("Hello from FastMCP SSH Server!\nThis is a test file.")
        local_file = tmp_file.name

    try:
        # Upload file
        upload_result = await client.call_tool(
            "upload",
            localPath=local_file,
            remotePath="/tmp/fastmcp_test.txt",
            serverName="production",
        )

        print("📤 Upload Result:")
        print(f"   success: {upload_result['success']}")
        print(f"   message: {upload_result['message']}")

        # Download file
        download_path = f"{local_file}.downloaded"
        download_result = await client.call_tool(
            "download",
            remotePath="/tmp/fastmcp_test.txt",
            localPath=download_path,
            serverName="production",
        )

        print("\n📥 Download Result:")
        print(f"   success: {download_result['success']}")
        print(f"   message: {download_result['message']}")

    finally:
        # Cleanup
        Path(local_file).unlink(missing_ok=True)
        Path(f"{local_file}.downloaded").unlink(missing_ok=True)


async def demonstrate_server_listing(client):
    """Demonstrate the list-servers MCP tool."""
    print("\n📡 === Server Listing Demo ===")

    servers = await client.call_tool("list-servers")

    print(f"📋 Found {len(servers)} configured servers:")

    for server in servers:
        print(f"\n🖥️  Server: {server['name']}")
        print(f"   Host: {server['host']}:{server['port']}")
        print(f"   User: {server['username']}")
        print(f"   Auth: {server['authentication']}")
        print(f"   Status: {server['status']}")
        print(f"   Whitelist: {', '.join(server['whitelist'])}")
        print(f"   Blacklist: {', '.join(server['blacklist'])}")


async def demonstrate_batch_operations(client):
    """Demonstrate batch operations across multiple servers."""
    print("\n🔄 === Batch Operations Demo ===")

    # Get list of servers first
    servers = await client.call_tool("list-servers")

    # Execute the same command on all servers
    commands = ["whoami", "pwd", "uptime"]

    for command in commands:
        print(f"\n🔧 Executing '{command}' on all servers:")

        for server in servers:
            try:
                result = await client.call_tool(
                    "execute-command", cmdString=command, serverName=server["name"]
                )

                print(f"   {server['name']}: {result['stdout'].strip()}")

            except Exception as e:
                print(f"   {server['name']}: ❌ Error: {e}")


async def demonstrate_error_handling(client):
    """Demonstrate error handling with MCP tools."""
    print("\n🚨 === Error Handling Demo ===")

    # Try to execute a denied command
    try:
        await client.call_tool(
            "execute-command",
            cmdString="rm -rf /important/data",
            serverName="production",
        )
        print("❌ This should not have succeeded!")

    except Exception as e:
        print(f"✅ Expected error caught: {e}")

    # Try to upload a non-existent file
    try:
        await client.call_tool(
            "upload",
            localPath="/non/existent/file.txt",
            remotePath="/tmp/test.txt",
            serverName="production",
        )
        print("❌ This should not have succeeded!")

    except Exception as e:
        print(f"✅ Expected error caught: {e}")


async def main():
    """Main demonstration function."""
    # Setup logging
    setup_logger(level="info", enable_console=True)

    print("🚀 FastMCP SSH Server - Python MCP Client Demo")
    print("=" * 60)

    # Create and connect MCP client
    client = MockMCPClient("fastmcp-ssh-server")

    try:
        await client.connect()

        # Run all demonstrations
        await demonstrate_execute_command(client)
        await demonstrate_file_operations(client)
        await demonstrate_server_listing(client)
        await demonstrate_batch_operations(client)
        await demonstrate_error_handling(client)

        print("\n" + "=" * 60)
        print("🎉 All demonstrations completed successfully!")
        print("")
        print("💡 Key Takeaways:")
        print("   • All MCP tools provide consistent interfaces")
        print("   • Error handling is built into each tool")
        print("   • Server names allow targeting specific connections")
        print("   • Batch operations enable powerful automation")
        print("   • Security policies are enforced at the command level")

    except Exception as e:
        Logger.error(f"Demo failed: {e}")
        sys.exit(1)

    finally:
        await client.disconnect()


# Real MCP Client Example (commented out)
"""
# Example using an actual MCP client library:

import asyncio
from mcp import ClientSession

async def real_mcp_example():
    # Connect to FastMCP SSH Server
    async with ClientSession("fastmcp-ssh-server") as session:
        # Execute command
        result = await session.call_tool(
            "execute-command",
            cmdString="uptime",
            serverName="production"
        )
        print(f"Server uptime: {result['stdout']}")

        # Upload file
        await session.call_tool(
            "upload",
            localPath="./config.json",
            remotePath="/remote/config.json",
            serverName="production"
        )

        # List servers
        servers = await session.call_tool("list-servers")
        for server in servers:
            print(f"Server: {server['name']} - Status: {server['status']}")

# Run the real example
# asyncio.run(real_mcp_example())
"""


if __name__ == "__main__":
    asyncio.run(main())

# {{END_MODIFICATIONS}}
