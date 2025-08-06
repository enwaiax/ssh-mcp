# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "5bd0accf-48b9-42a7-ba37-2e87da1cce95"
#   Timestamp: "2025-08-05T20:12:54+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "SOLID-S (单一职责原则)"
#   Quality_Check: "Python模块入口点，支持python -m ssh_mcp运行"
# }}
# {{START_MODIFICATIONS}}
"""
FastMCP SSH Server - Module Entry Point

This module allows the package to be run as a module:
    python -m ssh_mcp

It simply imports and calls the main function from the main module.
"""

from .main import main

if __name__ == "__main__":
    main()
# {{END_MODIFICATIONS}}
