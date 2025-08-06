# ✅ **Confirmed Working Cursor MCP Configuration**

## 🎯 **Tested and Verified Configuration**

This configuration has been **tested and confirmed working** in production:

```json
{
  "mcpServers": {
    "my-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/raid/user/xiangw/workspace/toys/ssh-mcp-server",
        "run",
        "fastmcp-ssh-server",
        "--host", "viking-prod-527.ipp4a1.colossus.nvidia.com",
        "--port", "22",
        "--username", "local-xiangw",
        "--password", "b*!j1Lvo*@A#2A"
      ]
    }
  }
}
```

## 🔑 **Critical Success Factors**

### 1. **Use `--directory` Parameter**
```bash
"--directory", "/path/to/your/project"
```
❌ **Don't use:** `"cwd": "/path/to/project"`  
✅ **Use:** `--directory` in the args array

### 2. **Explicit Port Specification**
```bash
"--port", "22"
```
❌ **Don't skip** the port parameter  
✅ **Always specify** `--port` explicitly

### 3. **Correct Argument Order**
```bash
[
  "--directory", "/path/to/project",  # 1. Set working directory
  "run",                             # 2. UV command
  "fastmcp-ssh-server",             # 3. Our MCP server
  "--host", "hostname",             # 4. SSH parameters
  "--port", "22",
  "--username", "user",
  "--password", "pass"
]
```

## 🏃 **Quick Setup Steps**

1. **Copy your working config** to `~/.cursor/mcp.json` (Linux) or equivalent path
2. **Update the paths** to match your system:
   - Replace `/raid/user/xiangw/workspace/toys/ssh-mcp-server` with your actual project path
   - Update SSH credentials
3. **Restart Cursor IDE**
4. **Verify** MCP appears in status bar

## 🧪 **Test Your Configuration**

Before using in Cursor, test manually:

```bash
cd /your/project/path
uv run fastmcp-ssh-server --host your-host --port 22 --username your-user --password your-pass
```

If this works, your Cursor config will work too!

## 🔍 **Common Issues and Solutions**

| Issue | Solution |
|-------|----------|
| "Command not found" | Check `--directory` path is correct |
| "Connection failed" | Verify SSH credentials and network |
| "MCP not loading" | Restart Cursor after config changes |
| "Permission denied" | Check SSH user permissions |

## 📚 **Related Files**

- `basic-config.json` - Template configuration
- `README.md` - Complete setup guide
- `setup-cursor-mcp.sh` - Automated setup script

## 🙏 **Acknowledgment**

This working configuration was discovered and validated by the community. Thank you for sharing the solution that works!