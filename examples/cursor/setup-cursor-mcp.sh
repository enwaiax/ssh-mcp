#!/bin/bash
# Setup script for Cursor MCP integration

set -e

echo "🔧 Setting up Cursor MCP Integration for SSH Server"
echo "=================================================="

# Detect OS and set config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Cursor/User/globalStorage"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_DIR="$HOME/.config/Cursor/User/globalStorage"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

CONFIG_FILE="$CONFIG_DIR/mcp.json"

echo "📂 Config directory: $CONFIG_DIR"
echo "📄 Config file: $CONFIG_FILE"

# Create directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Check if config file exists
if [[ -f "$CONFIG_FILE" ]]; then
    echo "⚠️  MCP config file already exists"
    echo "Creating backup..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Get current project path
PROJECT_PATH=$(pwd)
echo "📁 Project path: $PROJECT_PATH"

# Prompt for SSH details
echo ""
echo "🔑 Please enter your SSH connection details:"
read -p "SSH Host: " SSH_HOST
read -p "SSH Username: " SSH_USERNAME
read -s -p "SSH Password: " SSH_PASSWORD
echo ""

# Create MCP configuration
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "ssh-server": {
      "command": "uv",
      "args": [
        "--directory",
        "$PROJECT_PATH",
        "run", 
        "fastmcp-ssh-server",
        "--host", "$SSH_HOST",
        "--port", "22",
        "--username", "$SSH_USERNAME",
        "--password", "$SSH_PASSWORD"
      ],
      "description": "SSH MCP Server for remote operations"
    }
  }
}
EOF

echo "✅ MCP configuration created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Restart Cursor IDE"
echo "2. Look for MCP status in the status bar"
echo "3. Try asking AI: 'List files in my remote server'"
echo ""
echo "🔧 Test your configuration:"
echo "   uv run fastmcp-ssh-server --host $SSH_HOST --username $SSH_USERNAME --password '***'"
echo ""
echo "📚 For more examples, see: examples/cursor/README.md"