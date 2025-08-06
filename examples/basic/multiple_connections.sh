#!/bin/bash
# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"
#   Timestamp: "2025-08-05T21:23:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "示例驱动学习 + 多连接管理"
#   Quality_Check: "多连接示例，展示SSH连接字符串格式，包含全局安全配置"
# }}
# {{START_MODIFICATIONS}}

# FastMCP SSH Server - Multiple Connections Example
# 
# This example demonstrates how to connect to multiple SSH servers
# simultaneously using SSH connection string format.
#
# Usage: ./multiple_connections.sh

set -e  # Exit on any error

echo "🚀 FastMCP SSH Server - Multiple Connections Example"
echo "=" * 50

# Multiple server configurations
# Format: [user@]host[:port]
SERVER1=${SSH_SERVER1:-"user1@server1.example.com:22"}
SERVER2=${SSH_SERVER2:-"user2@server2.example.com:2222"}
SERVER3=${SSH_SERVER3:-"server3.example.com"}  # No user specified

echo "📋 Server Configurations:"
echo "   Server 1: $SERVER1"
echo "   Server 2: $SERVER2" 
echo "   Server 3: $SERVER3"

# Global security configuration (applies to all servers)
WHITELIST="ls.*,pwd,echo.*,uptime,whoami,date,git status,git log"
BLACKLIST="rm.*,sudo.*,chmod.*,dd.*,mkfs.*"

echo ""
echo "🔒 Global Security Configuration:"
echo "   Whitelist: $WHITELIST"
echo "   Blacklist: $BLACKLIST"

echo ""
echo "🔌 Starting FastMCP SSH Server with multiple connections..."

# Start the FastMCP SSH server with multiple connections
# Global security settings are applied to all connections
fastmcp-ssh-server \
    --whitelist "$WHITELIST" \
    --blacklist "$BLACKLIST" \
    "$SERVER1" \
    "$SERVER2" \
    "$SERVER3"

echo ""
echo "✅ FastMCP SSH Server started successfully!"
echo ""
echo "📡 Connected Servers:"
echo "   • $(echo $SERVER1 | cut -d'@' -f2 | cut -d':' -f1) (as $(echo $SERVER1 | cut -d'@' -f1))"
echo "   • $(echo $SERVER2 | cut -d'@' -f2 | cut -d':' -f1) (as $(echo $SERVER2 | cut -d'@' -f1))"
echo "   • $SERVER3 (default user)"
echo ""
echo "💡 Tips:"
echo "   • Each server gets a unique name based on hostname"
echo "   • Use 'list-servers' MCP tool to see all connections"
echo "   • Specify serverName in MCP tool calls to target specific servers"
echo "   • All servers share the same security policy"

# {{END_MODIFICATIONS}}