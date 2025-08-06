#!/bin/bash
# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"
#   Timestamp: "2025-08-05T21:23:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "示例驱动学习 + 简单易懂"
#   Quality_Check: "基础单连接示例，适合初学者，包含详细注释"
# }}
# {{START_MODIFICATIONS}}

# FastMCP SSH Server - Single Connection Example
# 
# This example demonstrates how to connect to a single SSH server
# with basic authentication and security configuration.
#
# Usage: ./single_connection.sh

set -e  # Exit on any error

echo "🚀 FastMCP SSH Server - Single Connection Example"
echo "=" * 50

# Configuration - modify these values for your setup
HOST=${SSH_HOST:-"example.com"}
PORT=${SSH_PORT:-22}
USERNAME=${SSH_USERNAME:-"myuser"}
PASSWORD=${SSH_PASSWORD:-"mypass"}

echo "📋 Connection Configuration:"
echo "   Host: $HOST"
echo "   Port: $PORT"
echo "   Username: $USERNAME"
echo "   Password: [hidden]"

# Basic security configuration
WHITELIST="ls,pwd,echo.*,uptime,whoami,date"
BLACKLIST="rm.*,sudo.*,chmod.*"

echo ""
echo "🔒 Security Configuration:"
echo "   Whitelist: $WHITELIST"
echo "   Blacklist: $BLACKLIST"

echo ""
echo "🔌 Starting FastMCP SSH Server..."

# Start the FastMCP SSH server with single connection
fastmcp-ssh-server \
    --host "$HOST" \
    --port "$PORT" \
    --username "$USERNAME" \
    --password "$PASSWORD" \
    --whitelist "$WHITELIST" \
    --blacklist "$BLACKLIST"

echo ""
echo "✅ FastMCP SSH Server started successfully!"
echo ""
echo "💡 Tips:"
echo "   • Server is now ready to accept MCP tool calls"
echo "   • Use MCP clients to interact with the server"
echo "   • Press Ctrl+C to stop the server"
echo "   • Check logs for detailed operation information"

# {{END_MODIFICATIONS}}