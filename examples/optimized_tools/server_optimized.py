#!/usr/bin/env python3
"""
优化的SSH MCP服务器实现
使用FastMCP最佳实践的服务器代码
"""

import asyncio
import sys
from pathlib import Path

from ssh_tools_optimized import initialize_server

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from ssh_mcp.models import SSHConfig


async def main():
    """主函数 - 演示优化的服务器启动"""

    # SSH配置示例
    ssh_configs = {
        "production": SSHConfig(
            name="production",
            host="prod-server.example.com",
            port=22,
            username="deploy",
            private_key_path="~/.ssh/prod_key",
        ),
        "staging": SSHConfig(
            name="staging",
            host="staging-server.example.com",
            port=22,
            username="deploy",
            password="staging_password",
        ),
    }

    # 初始化服务器（自动注册所有工具）
    server = await initialize_server(ssh_configs)

    # 运行服务器
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
