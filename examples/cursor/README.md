# Cursor IDE MCP Integration Guide

## 📋 Overview

This guide shows how to integrate the FastMCP SSH Server with Cursor IDE for AI-powered remote server management.

## ✅ **Working Configuration Format**

**Important:** Use `--directory` parameter instead of `cwd` field for reliable operation:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ssh-mcp-server",
        "run",
        "fastmcp-ssh-server",
        "--host", "your-server.com",
        "--port", "22",
        "--username", "your-username",
        "--password", "your-password"
      ]
    }
  }
}
```

**Key Points:**
- ✅ Use `--directory` in args array (not `cwd` field)
- ✅ Always specify `--port` explicitly
- ✅ Args order: `--directory` → `run` → tool arguments

## 🔧 Configuration Options

### Basic SSH Connection

```json
{
  "mcpServers": {
    "my-ssh-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ssh-mcp-server",
        "run", 
        "fastmcp-ssh-server",
        "--host", "your-server.com",
        "--port", "22",
        "--username", "your-username",
        "--password", "your-password"
      ],
      "description": "SSH server for remote operations"
    }
  }
}
```

### SSH Key Authentication

```json
{
  "mcpServers": {
    "production-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ssh-mcp-server",
        "run", 
        "fastmcp-ssh-server",
        "--host", "prod-server.company.com",
        "--port", "22",
        "--username", "deploy",
        "--private-key", "~/.ssh/production_key",
        "--passphrase", "your-key-passphrase"
      ],
      "description": "Production server access"
    }
  }
}
```

### Multiple SSH Connections

```json
{
  "mcpServers": {
    "multi-ssh-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ssh-mcp-server",
        "run", 
        "fastmcp-ssh-server",
        "--ssh", "name=prod,host=prod.example.com,port=22,user=admin,password=xxx",
        "--ssh", "name=dev,host=dev.example.com,port=22,user=developer,privateKey=~/.ssh/dev_key",
        "--ssh", "name=staging,host=staging.example.com,port=22,user=staging,password=yyy"
      ],
      "description": "Multiple environment access"
    }
  }
}
```

### With Command Filtering

```json
{
  "mcpServers": {
    "secure-ssh-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ssh-mcp-server",
        "run", 
        "fastmcp-ssh-server",
        "--host", "secure-server.com",
        "--port", "22",
        "--username", "limited-user",
        "--password", "secure-password",
        "--whitelist", "ls,pwd,cat,grep,find,ps,top,df,du,whoami",
        "--blacklist", "rm.*,sudo.*,su.*,chmod.*,chown.*"
      ],
      "description": "Secure SSH with command restrictions"
    }
  }
}
```

## 🚀 Setup Instructions

### Step 1: Install Cursor (if not already installed)

Download from: https://cursor.sh

### Step 2: Locate Cursor MCP Configuration

The configuration file location depends on your OS:

- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/mcp.json`  
- **Windows**: `%APPDATA%/Cursor/User/globalStorage/mcp.json`

### Step 3: Create or Update Configuration

1. Create the configuration file if it doesn't exist
2. Add your SSH MCP server configuration
3. Restart Cursor IDE

### Step 4: Verify Integration

1. Open Cursor IDE
2. Look for MCP status in the status bar
3. Try asking the AI: "List files in my remote server"
4. The AI should be able to use SSH commands through MCP

## 🛠️ Available MCP Tools

Your SSH MCP server provides these tools to Cursor's AI:

| Tool | Description | Example Usage |
|------|-------------|---------------|
| `execute-command` | Run commands on remote server | "Run `ps aux` on the server" |
| `upload` | Upload files to remote server | "Upload this file to /tmp/" |
| `download` | Download files from remote server | "Download /var/log/app.log" |
| `list-servers` | Show available SSH connections | "Show me all configured servers" |

## 💡 Usage Examples

### Remote System Monitoring

"Can you check the disk usage on my production server?"

### Log Analysis

"Download and analyze the latest error logs from the web server"

### File Management

"Upload this configuration file to all my staging servers"

### Command Execution

"Run a system update on the development server and show me the output"

## 🔒 Security Considerations

1. **Credential Management**: Consider using SSH keys instead of passwords
2. **Command Restrictions**: Use whitelist/blacklist to limit available commands
3. **Network Access**: Ensure SSH connections are properly secured
4. **Audit Logging**: Monitor SSH MCP usage for security compliance

## 🐛 Troubleshooting

### Common Issues

1. **Server Not Starting**: Check uv and python environments
2. **SSH Connection Failed**: Verify credentials and network connectivity
3. **MCP Not Detected**: Restart Cursor after configuration changes
4. **Permission Denied**: Check SSH user permissions and command restrictions

### Debug Commands

```bash
# Test server manually
uv run fastmcp-ssh-server --host your-server.com --username user --password pass

# Check server connectivity
uv run python tests/test_mcp_integration.py

# Verify configuration
cat cursor-mcp-config.json | jq .
```

## 📚 Additional Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Cursor IDE Documentation](https://cursor.sh/docs)