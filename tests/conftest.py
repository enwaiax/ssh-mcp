# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "ec47c2ec-fcf4-4fba-9582-ee4c0dba3d77"
#   Timestamp: "2025-08-05T17:01:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "DRY (Don't Repeat Yourself)"
#   Quality_Check: "测试配置清晰，提供通用的测试夹具和配置"
# }}
# {{START_MODIFICATIONS}}
"""
Pytest Configuration and Fixtures

This module provides common test fixtures and configuration for all tests.
"""

import asyncio

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_ssh_config():
    """Provide mock SSH configuration for testing."""
    return {
        "test_server": {
            "name": "test_server",
            "host": "localhost",
            "port": 22,
            "username": "testuser",
            "password": "testpass",
        }
    }


@pytest.fixture
def mock_fastmcp_server():
    """Provide mock FastMCP server for testing."""
    # This will be implemented when FastMCP tools are added
    pass


# {{END_MODIFICATIONS}}
