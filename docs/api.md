# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"
#   Timestamp: "2025-08-05T21:23:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "文档即代码 + API规范化"
#   Quality_Check: "完整的API文档，详细的接口说明，丰富的使用示例"
# }}
# {{START_MODIFICATIONS}}
# FastMCP SSH Server - API Documentation

## Overview

The FastMCP SSH Server provides four core MCP tools for SSH operations. All tools follow the Model Context Protocol (MCP) specification and provide consistent error handling and response formats.

## MCP Tools

### 1. execute-command

Execute commands on remote SSH servers with security validation.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cmdString` | string | ✅ | - | Command to execute on the remote server |
| `serverName` | string | ❌ | "default" | Name of the SSH server to execute on |
| `timeout` | integer | ❌ | 30 | Command timeout in seconds |

#### Request Example

```json
{
  "tool": "execute-command",
  "arguments": {
    "cmdString": "ls -la /home/user",
    "serverName": "production",
    "timeout": 60
  }
}
```

#### Response Format

**Success Response:**
```json
{
  "stdout": "total 24\ndrwxr-xr-x 3 user user 4096 Aug  5 13:23 .\ndrwxr-xr-x 3 root root 4096 Aug  1 10:15 ..",
  "stderr": "",
  "exitCode": 0,
  "serverName": "production"
}
```

**Error Response:**
```json
{
  "isError": true,
  "error": {
    "error_type": "SSHCommandError",
    "message": "Command denied by security policy: rm not allowed",
    "timestamp": "2025-08-05T21:23:20+08:00"
  },
  "message": "Command execution failed: Command denied by security policy"
}
```

#### Security Validation

Commands are validated against the configured whitelist and blacklist:

- **Whitelist**: Commands must match at least one pattern
- **Blacklist**: Commands must not match any pattern
- **Patterns**: Support regular expressions

**Example Security Configurations:**

```bash
# Allow only safe commands
--whitelist "ls.*,pwd,echo.*,cat.*"

# Deny dangerous commands
--blacklist "rm.*,sudo.*,chmod.*,dd.*"

# Complex patterns
--whitelist "git (status|log|show).*"
--blacklist "git (reset --hard|push --force).*"
```

### 2. upload

Upload files to remote SSH servers via SFTP.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `localPath` | string | ✅ | - | Local file path to upload |
| `remotePath` | string | ✅ | - | Remote destination path |
| `serverName` | string | ❌ | "default" | Name of the SSH server |

#### Request Example

```json
{
  "tool": "upload",
  "arguments": {
    "localPath": "/local/config.json",
    "remotePath": "/remote/app/config.json",
    "serverName": "staging"
  }
}
```

#### Response Format

**Success Response:**
```json
{
  "success": true,
  "message": "File uploaded successfully from /local/config.json to staging:/remote/app/config.json",
  "localPath": "/local/config.json",
  "remotePath": "/remote/app/config.json",
  "serverName": "staging"
}
```

**Error Response:**
```json
{
  "isError": true,
  "error": {
    "error_type": "SFTPError",
    "message": "Local file not found: /local/missing.json",
    "timestamp": "2025-08-05T21:23:20+08:00"
  },
  "message": "Upload failed: Local file not found"
}
```

#### File Path Handling

- **Local Paths**: Supports absolute and relative paths, tilde expansion
- **Remote Paths**: Absolute paths recommended, relative to user home if relative
- **Permissions**: Inherits parent directory permissions on remote
- **Overwrite**: Existing files are overwritten without warning

### 3. download

Download files from remote SSH servers via SFTP.

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `remotePath` | string | ✅ | - | Remote file path to download |
| `localPath` | string | ✅ | - | Local destination path |
| `serverName` | string | ❌ | "default" | Name of the SSH server |

#### Request Example

```json
{
  "tool": "download",
  "arguments": {
    "remotePath": "/remote/logs/app.log",
    "localPath": "/local/logs/app.log",
    "serverName": "production"
  }
}
```

#### Response Format

**Success Response:**
```json
{
  "success": true,
  "message": "File downloaded successfully from production:/remote/logs/app.log to /local/logs/app.log",
  "remotePath": "/remote/logs/app.log",
  "localPath": "/local/logs/app.log",
  "serverName": "production"
}
```

**Error Response:**
```json
{
  "isError": true,
  "error": {
    "error_type": "SFTPError",
    "message": "Remote file not found: /remote/missing.log",
    "timestamp": "2025-08-05T21:23:20+08:00"
  },
  "message": "Download failed: Remote file not found"
}
```

#### File Path Handling

- **Remote Paths**: Must be accessible by the SSH user
- **Local Paths**: Parent directories are created automatically
- **Permissions**: Downloaded files inherit local umask
- **Overwrite**: Existing local files are overwritten

### 4. list-servers

List all configured SSH servers and their connection status.

#### Parameters

No parameters required.

#### Request Example

```json
{
  "tool": "list-servers",
  "arguments": {}
}
```

#### Response Format

**Success Response:**
```json
[
  {
    "name": "production",
    "host": "prod.example.com",
    "port": 22,
    "username": "deploy",
    "authentication": "key",
    "status": "connected",
    "whitelist": ["git.*", "npm.*", "node.*"],
    "blacklist": ["rm.*", "sudo.*"]
  },
  {
    "name": "staging",
    "host": "staging.example.com",
    "port": 2222,
    "username": "dev",
    "authentication": "password",
    "status": "disconnected",
    "whitelist": ["*"],
    "blacklist": ["rm -rf.*"]
  }
]
```

**Error Response:**
```json
{
  "isError": true,
  "error": {
    "error_type": "RuntimeError",
    "message": "SSH manager not initialized",
    "timestamp": "2025-08-05T21:23:20+08:00"
  },
  "message": "Server listing failed: SSH manager not initialized"
}
```

#### Server Status Values

- **`connected`**: Active SSH connection established
- **`disconnected`**: No active connection
- **`error`**: Connection failed or authentication error
- **`unknown`**: Status not yet determined

## Error Handling

### Common Error Types

#### SSHConnectionError
- **Cause**: Network connectivity issues, incorrect host/port
- **Resolution**: Verify network connectivity and server details

#### SSHAuthenticationError
- **Cause**: Invalid credentials, missing/incorrect private key
- **Resolution**: Verify username, password, or private key

#### SSHCommandError
- **Cause**: Command denied by security policy, command not found
- **Resolution**: Check whitelist/blacklist configuration

#### SFTPError
- **Cause**: File not found, permission denied, disk space
- **Resolution**: Verify file paths and permissions

#### ConfigurationError
- **Cause**: Invalid configuration parameters
- **Resolution**: Check CLI arguments and configuration

### Error Response Format

All errors follow a consistent format:

```json
{
  "isError": true,
  "error": {
    "error_type": "ErrorClassName",
    "message": "Detailed error description",
    "timestamp": "ISO 8601 timestamp",
    "context": {
      "additional": "context information"
    }
  },
  "message": "User-friendly error message"
}
```

## Usage Examples

### Basic Command Execution

```python
# Using Python MCP client
import asyncio
from mcp import ClientSession

async def execute_command():
    async with ClientSession("fastmcp-ssh-server") as session:
        result = await session.call_tool(
            "execute-command",
            cmdString="uptime",
            serverName="production"
        )
        print(f"Server uptime: {result['stdout']}")

asyncio.run(execute_command())
```

### File Operations

```python
async def backup_logs():
    async with ClientSession("fastmcp-ssh-server") as session:
        # Download current log
        await session.call_tool(
            "download",
            remotePath="/var/log/app.log",
            localPath="./backup/app.log",
            serverName="production"
        )
        
        # Upload new configuration
        await session.call_tool(
            "upload",
            localPath="./config/new-app.conf",
            remotePath="/etc/app/app.conf",
            serverName="production"
        )

asyncio.run(backup_logs())
```

### Server Management

```python
async def check_servers():
    async with ClientSession("fastmcp-ssh-server") as session:
        servers = await session.call_tool("list-servers")
        
        for server in servers:
            print(f"Server: {server['name']}")
            print(f"Status: {server['status']}")
            print(f"Host: {server['host']}:{server['port']}")
            print("---")

asyncio.run(check_servers())
```

## Rate Limiting and Timeouts

### Default Timeouts

- **Command Execution**: 30 seconds (configurable)
- **File Upload**: No timeout (depends on file size)
- **File Download**: No timeout (depends on file size)
- **Connection Establishment**: 10 seconds

### Timeout Configuration

```json
{
  "tool": "execute-command",
  "arguments": {
    "cmdString": "long-running-task",
    "timeout": 300  // 5 minutes
  }
}
```

### Connection Pooling

- Connections are reused across multiple tool calls
- Idle connections are maintained for 5 minutes
- Maximum of 10 concurrent connections per server
- Automatic reconnection on connection loss

## Security Considerations

### Command Security

1. **Always use whitelist patterns** for production environments
2. **Avoid overly permissive patterns** like `.*` or `*`
3. **Test security policies** before deployment
4. **Regular audit** of allowed commands

### Authentication Security

1. **Use private key authentication** for production
2. **Protect private keys** with strong passphrases
3. **Rotate credentials** regularly
4. **Limit SSH user permissions** on target servers

### Network Security

1. **Use SSH key-based authentication**
2. **Disable password authentication** on SSH servers
3. **Use non-standard SSH ports** when possible
4. **Implement network firewalls**

## Performance Optimization

### Connection Management

- **Reuse connections** for multiple operations
- **Configure appropriate timeouts** based on use case
- **Monitor connection health** regularly

### File Transfer Optimization

- **Use streaming** for large files
- **Compress files** before transfer when possible
- **Parallel transfers** for multiple files

### Command Execution

- **Batch related commands** when possible
- **Use efficient commands** (avoid unnecessary verbosity)
- **Cache frequently accessed data**

## Debugging and Logging

### Enable Debug Logging

```bash
# Set log level to debug
export PYTHONPATH=python_src
python -c "
from python_ssh_mcp.utils import setup_logger
setup_logger(level='debug', enable_console=True)
"
```

### Log Levels

- **DEBUG**: Detailed operation information
- **INFO**: General operation status
- **WARNING**: Recoverable issues
- **ERROR**: Operation failures
- **CRITICAL**: System failures

### Common Debug Scenarios

```python
# Enable verbose SSH debugging
import logging
logging.getLogger('asyncssh').setLevel(logging.DEBUG)

# Custom error handler
from python_ssh_mcp.utils import Logger

def debug_tool_call(tool_name, **kwargs):
    Logger.debug(f"Calling tool: {tool_name}", kwargs)
    # Your tool call here
```

---

For more examples and advanced usage patterns, see the [examples/](../examples/) directory.
# {{END_MODIFICATIONS}}