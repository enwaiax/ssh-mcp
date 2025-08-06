# {{RIPER-5:
#   Action: "Modified"
#   Task_ID: "5bd0accf-48b9-42a7-ba37-2e87da1cce95"
#   Timestamp: "2025-08-05T20:12:54+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则) + 高内聚低耦合"
#   Quality_Check: "完整集成v2 SSHMCPServer，CLI解析，MCP工具注册，服务器启动，优雅错误处理"
# }}
# {{START_MODIFICATIONS}}
#!/usr/bin/env python3
"""
FastMCP SSH Server - Main Entry Point

This module provides the main entry point for the FastMCP SSH server.
It handles CLI argument parsing, server initialization, and startup.
Compatible with TypeScript version architecture.
"""

import asyncio
import sys
from typing import NoReturn

from . import SSHMCPServer, __version__
from .cli import app as cli_app
from .utils import Logger, setup_logger


def display_startup_banner(server_count: int, transport: str = "stdio") -> None:
    """
    Display startup banner with server information.
    Only displays for non-stdio transports to avoid interfering with MCP JSON protocol.

    Args:
        server_count: Number of configured SSH servers
        transport: Transport protocol being used
    """
    # Skip banner for stdio transport to avoid JSON protocol interference
    if transport.lower() == "stdio":
        return

    print("\n" + "=" * 60)
    print("🚀 FastMCP SSH Server")
    print("=" * 60)
    print(f"📊 Version: {__version__}")
    print(f"🔧 SSH Connections: {server_count} configured")
    print("🛠️  MCP Tools: execute-command, upload, download, list-servers")
    print("🌐 Protocol: Model Context Protocol (MCP)")
    print(f"📡 Transport: {transport}")
    print("=" * 60)
    print("✅ Server ready for MCP connections!")
    print("💡 Press Ctrl+C to shutdown gracefully")
    print()


async def start_server_with_config(ssh_configs):
    """
    Start the SSH MCP server with the given configuration.

    This function is called from the CLI command handler.

    Args:
        ssh_configs: SSH connection configuration map
    """
    ssh_server = None

    try:
        # Setup logging system
        setup_logger(level="info", enable_console=True)
        Logger.info(
            "FastMCP SSH Server starting",
            {"version": __version__, "servers": len(ssh_configs)},
        )

        # FastMCP will handle banner display for stdio transport
        # Custom banner skipped to avoid JSON protocol interference

        # Create SSH MCP server (unified implementation)
        server_name = "fastmcp-ssh-server"
        ssh_server = SSHMCPServer(server_name)
        Logger.info("SSH MCP Server instance created")
        Logger.info("Using unified SSH MCP tools implementation")

        # Initialize server with SSH configurations
        Logger.info("Initializing SSH connections", {"server_count": len(ssh_configs)})
        try:
            await ssh_server.initialize(ssh_configs)
            Logger.info("SSH connections initialized successfully")
        except Exception as init_error:
            Logger.handle_error(
                init_error, "SSH initialization failed", include_traceback=True
            )
            print(f"\n❌ SSH initialization failed: {init_error}", file=sys.stderr)
            print(
                "🚪 Server cannot start without valid SSH connections. Exiting...",
                file=sys.stderr,
            )
            sys.exit(1)

        Logger.info("MCP tools registration completed")
        Logger.info("Starting FastMCP server")

        # Start the FastMCP server (FastMCP handles signals internally)
        Logger.info("FastMCP server ready, starting main loop")
        await ssh_server.run()

    except KeyboardInterrupt:
        print("\n👋 Server shutdown requested", file=sys.stderr)
        print("🔄 Cleaning up resources...", file=sys.stderr)
        Logger.info("Server shutdown requested by user")

        # Graceful cleanup
        if ssh_server:
            try:
                Logger.info("Starting cleanup process")
                await ssh_server.cleanup()
                print("✅ Cleanup completed", file=sys.stderr)
                Logger.info("Cleanup completed successfully")
            except Exception as cleanup_error:
                print(f"⚠️  Cleanup warning: {cleanup_error}", file=sys.stderr)
                Logger.warning("Cleanup warning", {"error": str(cleanup_error)})

        print("👋 FastMCP SSH Server stopped gracefully", file=sys.stderr)
        Logger.info("FastMCP SSH Server stopped gracefully")

        # Give a brief moment for final cleanup
        await asyncio.sleep(0.1)

    except Exception as e:
        print(f"\n❌ Server startup failed: {e}", file=sys.stderr)
        Logger.handle_error(e, "Server startup failed", include_traceback=True)

        # Attempt cleanup on error
        if ssh_server:
            try:
                await ssh_server.cleanup()
                Logger.info("Error cleanup completed")
            except Exception as cleanup_error:
                Logger.debug(
                    "Error during error cleanup", {"error": str(cleanup_error)}
                )

        sys.exit(1)


def main() -> NoReturn:
    """
    Main entry point for the CLI application.

    This function is called when the package is executed as a script
    or when the 'fastmcp-ssh-server' command is run.

    Delegates to the Typer CLI application for argument parsing and execution.
    """
    try:
        # Run the Typer CLI application
        cli_app()
    except SystemExit as e:
        # Typer raises SystemExit on help, version, or other control flow
        sys.exit(e.code)
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Fatal error: {e}", file=sys.stderr)
        print("🔍 Please check your configuration and try again", file=sys.stderr)
        # Try to log the fatal error if logging is set up
        try:
            Logger.critical("Fatal error in main", {"error": str(e)})
        except Exception:
            pass  # Logging may not be initialized yet
        sys.exit(1)

    # Should not reach here
    sys.exit(0)


if __name__ == "__main__":
    main()
# {{END_MODIFICATIONS}}
