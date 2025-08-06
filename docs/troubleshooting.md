# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"
#   Timestamp: "2025-08-05T21:23:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "文档即代码 + 问题解决导向"
#   Quality_Check: "全面的故障排除指南，实用的解决方案，丰富的诊断工具"
# }}
# {{START_MODIFICATIONS}}
# FastMCP SSH Server - Troubleshooting Guide

## Common Issues and Solutions

### 🔌 Connection Issues

#### Issue: "Connection refused" Error

**Symptoms:**
```
SSHConnectionError: Failed to connect to server.com:22 - Connection refused
```

**Possible Causes & Solutions:**

1. **SSH service not running on target server**
   ```bash
   # Check if SSH service is running
   sudo systemctl status ssh
   sudo systemctl status sshd

   # Start SSH service if stopped
   sudo systemctl start ssh
   ```

2. **Incorrect host or port**
   ```bash
   # Test connection manually
   ssh user@host -p port

   # Check if custom SSH port is configured
   grep "Port" /etc/ssh/sshd_config
   ```

3. **Firewall blocking connection**
   ```bash
   # Test connectivity
   telnet host port
   nc -zv host port

   # Check local firewall
   sudo ufw status
   sudo iptables -L
   ```

4. **Network connectivity issues**
   ```bash
   # Test basic connectivity
   ping host

   # Check DNS resolution
   nslookup host
   dig host
   ```

**Fix:**
```bash
# Use correct host and port
fastmcp-ssh-server --host correct.host.com --port 22 --username user --password pass
```

#### Issue: "Connection timeout" Error

**Symptoms:**
```
SSHConnectionError: Connection timeout after 10 seconds
```

**Solutions:**

1. **Increase connection timeout (if available)**
2. **Check network latency**
   ```bash
   ping -c 5 host
   traceroute host
   ```

3. **Verify SSH configuration**
   ```bash
   # Test with verbose SSH
   ssh -v user@host
   ```

### 🔐 Authentication Issues

#### Issue: "Authentication failed" Error

**Symptoms:**
```
SSHAuthenticationError: Authentication failed for user@host
```

**Possible Causes & Solutions:**

1. **Incorrect username or password**
   ```bash
   # Verify credentials manually
   ssh user@host

   # Use correct credentials
   fastmcp-ssh-server --host host --username correct_user --password correct_pass
   ```

2. **Private key issues**
   ```bash
   # Check key permissions
   ls -la ~/.ssh/id_rsa
   chmod 600 ~/.ssh/id_rsa
   chmod 700 ~/.ssh

   # Test key manually
   ssh -i ~/.ssh/id_rsa user@host
   ```

3. **Key format issues**
   ```bash
   # Convert OpenSSH key to RSA format if needed
   ssh-keygen -p -m RFC4716 -f ~/.ssh/id_rsa

   # Generate new key if corrupted
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/new_key
   ```

4. **Passphrase required**
   ```bash
   # If private key has passphrase
   fastmcp-ssh-server --host host --username user \
     --private-key ~/.ssh/id_rsa --passphrase "your_passphrase"
   ```

#### Issue: "Permission denied (publickey)" Error

**Solutions:**

1. **Add public key to authorized_keys**
   ```bash
   # Copy public key to server
   ssh-copy-id -i ~/.ssh/id_rsa.pub user@host

   # Or manually
   cat ~/.ssh/id_rsa.pub | ssh user@host 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'
   ```

2. **Check SSH server configuration**
   ```bash
   # On SSH server, check config
   sudo grep -E "(PubkeyAuthentication|PasswordAuthentication)" /etc/ssh/sshd_config

   # Ensure public key auth is enabled
   # PubkeyAuthentication yes
   ```

3. **Verify authorized_keys permissions**
   ```bash
   # On SSH server
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

### 🚫 Command Execution Issues

#### Issue: "Command denied by security policy" Error

**Symptoms:**
```
SSHCommandError: Command denied by security policy: rm not allowed
```

**Solutions:**

1. **Check whitelist configuration**
   ```bash
   # Allow specific commands
   fastmcp-ssh-server --host host --username user --password pass \
     --whitelist "ls,pwd,echo.*,git.*"
   ```

2. **Review blacklist patterns**
   ```bash
   # Remove overly restrictive patterns
   fastmcp-ssh-server --host host --username user --password pass \
     --whitelist "*" --blacklist "rm -rf.*,sudo su.*"
   ```

3. **Test command patterns**
   ```python
   # Test regex patterns
   import re

   patterns = ["ls.*", "echo.*"]
   command = "ls -la"

   matches = any(re.search(pattern, command) for pattern in patterns)
   print(f"Command '{command}' matches: {matches}")
   ```

#### Issue: "Command not in allowed list" Error

**Solutions:**

1. **Add command to whitelist**
   ```bash
   # Add missing command pattern
   fastmcp-ssh-server --host host --username user --password pass \
     --whitelist "ls.*,pwd,echo.*,cat.*,your_command.*"
   ```

2. **Use wildcard for testing**
   ```bash
   # Allow all commands (use cautiously)
   fastmcp-ssh-server --host host --username user --password pass \
     --whitelist "*"
   ```

### 📁 File Transfer Issues

#### Issue: "Local file not found" Error

**Symptoms:**
```
SFTPError: Local file not found: /path/to/file.txt
```

**Solutions:**

1. **Verify file path**
   ```bash
   # Check if file exists
   ls -la /path/to/file.txt

   # Use absolute path
   realpath /path/to/file.txt
   ```

2. **Check permissions**
   ```bash
   # Ensure read permissions
   chmod 644 /path/to/file.txt
   ```

#### Issue: "Remote file not found" Error

**Solutions:**

1. **Verify remote path**
   ```bash
   # Check remote file manually
   ssh user@host "ls -la /remote/path/file.txt"
   ```

2. **Use proper path format**
   ```bash
   # Use absolute paths
   /home/user/file.txt  # Good
   ~/file.txt           # May not work as expected
   ```

#### Issue: "Permission denied" for File Operations

**Solutions:**

1. **Check directory permissions**
   ```bash
   # Ensure write permissions on target directory
   ssh user@host "ls -la /target/directory/"

   # Create directory if needed
   ssh user@host "mkdir -p /target/directory/"
   ```

2. **Verify user permissions**
   ```bash
   # Check user's access
   ssh user@host "touch /target/directory/test_file"
   ```

### ⚙️ Configuration Issues

#### Issue: "SSH manager not initialized" Error

**Symptoms:**
```
RuntimeError: SSH manager not initialized
```

**Solutions:**

1. **Ensure proper initialization**
   ```python
   # In Python code
   from python_ssh_mcp.ssh_manager import SSHConnectionManager
   from python_ssh_mcp.models import SSHConfig

   # Create configuration
   config = SSHConfig(
       name="server1",
       host="example.com",
       username="user",
       password="pass"
   )

   # Initialize manager
   manager = await SSHConnectionManager.get_instance()
   manager.set_config({"server1": config})
   ```

#### Issue: "Invalid port number" Error

**Solutions:**

1. **Use valid port range**
   ```bash
   # Port must be 1-65535
   fastmcp-ssh-server --host host --port 22  # Good
   fastmcp-ssh-server --host host --port 99999  # Bad
   ```

### 🔍 Debug Mode

#### Enable Debug Logging

```bash
# Set environment variable
export PYTHONPATH=python_src

# Run with debug logging
python -c "
from python_ssh_mcp.utils import setup_logger, Logger
setup_logger(level='debug', enable_console=True)
Logger.debug('Debug mode enabled')
"
```

#### Verbose SSH Debugging

```python
# Enable AsyncSSH debug logging
import logging
logging.getLogger('asyncssh').setLevel(logging.DEBUG)

# Custom debug wrapper
from python_ssh_mcp.utils import Logger

async def debug_command(manager, command, server="default"):
    Logger.debug(f"Executing command: {command}", {"server": server})
    try:
        result = await manager.execute_command(command, server)
        Logger.debug(f"Command result: {result}")
        return result
    except Exception as e:
        Logger.error(f"Command failed: {e}")
        raise
```

### 🧪 Diagnostic Tools

#### Create Diagnostic Script

```python
#!/usr/bin/env python3
"""
FastMCP SSH Server Diagnostic Tool
"""

import asyncio
import subprocess
import sys
from pathlib import Path

async def run_diagnostics():
    print("🔍 FastMCP SSH Server Diagnostics")
    print("=" * 50)

    # Check 1: Python version
    print("1. Python Version Check:")
    version = sys.version_info
    if version >= (3, 12):
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (need 3.12+)")

    # Check 2: Dependencies
    print("\n2. Dependencies Check:")
    deps = ["asyncssh", "fastmcp", "pydantic", "typer", "loguru"]

    for dep in deps:
        try:
            __import__(dep.replace("-", "_"))
            print(f"   ✅ {dep}")
        except ImportError:
            print(f"   ❌ {dep} - not installed")

    # Check 3: SSH connectivity test
    print("\n3. SSH Test (if host provided):")
    if len(sys.argv) > 1:
        host = sys.argv[1]
        try:
            result = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", host, "echo", "test"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                print(f"   ✅ SSH connection to {host}")
            else:
                print(f"   ❌ SSH connection failed: {result.stderr.decode()}")
        except Exception as e:
            print(f"   ❌ SSH test error: {e}")
    else:
        print("   ⏭️  Skipped (no host provided)")

    # Check 4: FastMCP SSH Server
    print("\n4. FastMCP SSH Server Check:")
    try:
        # Try to import main modules
        from python_ssh_mcp.ssh_manager import SSHConnectionManager
        from python_ssh_mcp.models import SSHConfig
        from python_ssh_mcp.server import SSHMCPServer

        print("   ✅ Core modules import successfully")

        # Test basic functionality
        config = SSHConfig(
            name="test",
            host="localhost",
            username="test",
            password="test"
        )
        print("   ✅ Configuration model working")

    except Exception as e:
        print(f"   ❌ FastMCP SSH Server error: {e}")

    print("\n🎯 Diagnostic Summary:")
    print("   If all checks pass, the server should work correctly.")
    print("   If any check fails, resolve the issue before proceeding.")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
```

#### Usage:
```bash
# Run diagnostics
python diagnostic.py

# Run with SSH test
python diagnostic.py user@host
```

### 📊 Performance Issues

#### Issue: Slow Command Execution

**Solutions:**

1. **Check network latency**
   ```bash
   ping -c 10 host
   ```

2. **Optimize commands**
   ```bash
   # Use efficient commands
   ls -1 instead of ls -la  # Less output

   # Avoid unnecessary verbosity
   git status --porcelain  # Shorter output
   ```

3. **Use connection pooling**
   ```python
   # Reuse connections for multiple commands
   manager = await SSHConnectionManager.get_instance()
   # Multiple commands use the same connection automatically
   ```

#### Issue: High Memory Usage

**Solutions:**

1. **Monitor memory usage**
   ```python
   import psutil
   import os

   process = psutil.Process(os.getpid())
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

2. **Cleanup connections**
   ```python
   # Ensure proper cleanup
   await manager.cleanup()
   ```

### 🆘 Emergency Procedures

#### Complete Reset

```bash
# Stop all SSH connections
pkill -f fastmcp-ssh-server

# Clear SSH agent
ssh-add -D

# Reset SSH connection state
rm -f ~/.ssh/known_hosts.tmp
```

#### Backup Configuration

```bash
# Backup SSH keys
cp -r ~/.ssh ~/.ssh.backup

# Backup configuration
cp pyproject.toml pyproject.toml.backup
```

### 📞 Getting Help

#### Collect Debug Information

```bash
# Create debug report
cat > debug_report.txt << EOF
FastMCP SSH Server Debug Report
Generated: $(date)

Python Version: $(python --version)
OS: $(uname -a)

Error Details:
[Paste your error message here]

Configuration:
[Paste your command line or configuration here]

Network Test:
$(ping -c 3 your-host 2>&1)

SSH Test:
$(ssh -v your-user@your-host 'echo test' 2>&1)
EOF
```

#### Where to Get Help

1. **GitHub Issues**: [Report bugs](https://github.com/your-username/fastmcp-ssh-server/issues)
2. **Discussions**: [Ask questions](https://github.com/your-username/fastmcp-ssh-server/discussions)
3. **Documentation**: [docs/](../docs/)
4. **Examples**: [examples/](../examples/)

#### Information to Include

When reporting issues, please include:

- **Error message** (full traceback)
- **Command used** (with sensitive data removed)
- **Operating system** and Python version
- **Network configuration** (if relevant)
- **SSH server configuration** (if relevant)
- **Debug output** (if available)

---

## Quick Reference

### Diagnostic Commands

```bash
# Test SSH connection
ssh -v user@host

# Test with timeout
timeout 10 ssh user@host 'echo test'

# Check SSH service
sudo systemctl status ssh

# Test port connectivity
nc -zv host port

# Check DNS resolution
nslookup host
```

### Common Fix Commands

```bash
# Fix SSH key permissions
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh

# Restart SSH service
sudo systemctl restart ssh

# Clear known_hosts
rm ~/.ssh/known_hosts

# Test with minimal SSH config
ssh -F /dev/null user@host
```

Remember: Most issues are related to SSH configuration, network connectivity, or authentication. Start with basic SSH troubleshooting before investigating FastMCP-specific issues.
# {{END_MODIFICATIONS}}
