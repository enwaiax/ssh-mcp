# {{RIPER-5:

# Action: "Added"

# Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"

# Timestamp: "2025-08-05T21:23:20+08:00"

# Authoring_Role: "LD"

# Principle_Applied: "文档即代码 + 用户体验优先"

# Quality_Check: "完整的项目文档，清晰的安装使用指南，专业的部署配置"

# }}

# {{START_MODIFICATIONS}}

# FastMCP SSH Server - Python Implementation

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![FastMCP](https://img.shields.io/badge/FastMCP-2.0+-green.svg)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-ISC-blue.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-35%25-yellow.svg)](htmlcov/index.html)

> 🚀 **A modern, FastMCP-based SSH server implementation for Model Context Protocol (MCP)**

FastMCP SSH Server is a Python implementation of an SSH server for the Model Context Protocol, providing seamless SSH connection management and command execution capabilities for AI models. This is a complete re-implementation of the TypeScript version with enhanced features and improved performance.

## ✨ Features

### 🔌 **Core Capabilities**

- **Multi-SSH Connection Management**: Connect to multiple SSH servers simultaneously
- **FastMCP Integration**: Native integration with FastMCP framework for optimal performance
- **Authentication Methods**: Support for password and private key authentication
- **Security Validation**: Command whitelist/blacklist with regex pattern matching
- **File Transfer**: Secure SFTP upload and download operations
- **Async Architecture**: Full async/await support for high performance

### 🛡️ **Security Features**

- **Command Filtering**: Configurable whitelist and blacklist for command security
- **Connection Validation**: Comprehensive SSH connection parameter validation
- **Error Handling**: Robust error handling with detailed logging
- **Secure Credentials**: Support for private key authentication with passphrase protection

### 🚀 **Performance & Reliability**

- **Connection Pooling**: Efficient connection reuse and management
- **Singleton Pattern**: Centralized connection management
- **Timeout Controls**: Configurable timeouts for all operations
- **Resource Cleanup**: Automatic cleanup of connections and resources

## 📦 Installation

### Requirements

- **Python 3.12+** (recommended)
- **uv** package manager (recommended) or **pip**
- **AsyncSSH** for SSH connections
- **FastMCP** framework

### Using uv (Recommended)

```bash
# Install from source
git clone https://github.com/your-username/fastmcp-ssh-server.git
cd fastmcp-ssh-server

# Install with uv
uv sync

# Or install in development mode
uv sync --dev
```

### Using pip

```bash
# Install from source
git clone https://github.com/your-username/fastmcp-ssh-server.git
cd fastmcp-ssh-server

# Install dependencies
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

### From PyPI (Future)

```bash
# Will be available when published
pip install fastmcp-ssh-server
```

## 🚀 Quick Start

### 1. Basic Usage

```bash
# Single connection mode
fastmcp-ssh-server --host example.com --username myuser --password mypass

# Multiple connection mode using SSH connection strings
fastmcp-ssh-server user1@server1.com:22 user2@server2.com:2222

# With private key authentication
fastmcp-ssh-server --host server.com --username user --private-key ~/.ssh/id_rsa
```

### 2. Security Configuration

```bash
# With command restrictions
fastmcp-ssh-server \
    --host example.com \
    --username user \
    --password pass \
    --whitelist "ls,pwd,echo.*" \
    --blacklist "rm.*,sudo.*"
```

### 3. Configuration File (Coming Soon)

```yaml
# config.yaml
servers:
  production:
    host: prod.example.com
    port: 22
    username: deploy
    private_key: ~/.ssh/prod_key
    whitelist: ["git.*", "npm.*", "node.*"]
    blacklist: ["rm.*", "sudo.*"]

  staging:
    host: staging.example.com
    port: 2222
    username: dev
    password: dev_password
    whitelist: ["*"]
    blacklist: ["rm -rf"]
```

## 📖 Usage Guide

### Command Line Interface

The FastMCP SSH Server provides a flexible CLI with support for both single and multiple connection modes.

#### Single Connection Mode

```bash
fastmcp-ssh-server [OPTIONS]

Options:
  -h, --host TEXT          SSH hostname
  -p, --port INTEGER       SSH port (default: 22)
  -u, --username TEXT      SSH username
  -w, --password TEXT      SSH password
  -k, --private-key TEXT   SSH private key file path
  -P, --passphrase TEXT    SSH private key passphrase
  -W, --whitelist TEXT     Command whitelist patterns (comma-separated)
  -B, --blacklist TEXT     Command blacklist patterns (comma-separated)
  --help                   Show help and exit
```

#### Multiple Connection Mode

```bash
# Format: [user@]host[:port]
fastmcp-ssh-server user1@server1.com:22 user2@server2.com:2222
```

#### Global Security Options

```bash
# Apply security settings to all connections
fastmcp-ssh-server --whitelist "ls,pwd,cat" --blacklist "rm,sudo" \
    user1@server1.com user2@server2.com
```

### MCP Tools

The server provides four main MCP tools:

#### 1. `execute-command`

Execute commands on SSH servers with security validation.

```json
{
  "tool": "execute-command",
  "arguments": {
    "cmdString": "ls -la /home",
    "serverName": "production",
    "timeout": 30
  }
}
```

#### 2. `upload`

Upload files to SSH servers via SFTP.

```json
{
  "tool": "upload",
  "arguments": {
    "localPath": "/local/file.txt",
    "remotePath": "/remote/path/file.txt",
    "serverName": "production"
  }
}
```

#### 3. `download`

Download files from SSH servers via SFTP.

```json
{
  "tool": "download",
  "arguments": {
    "remotePath": "/remote/path/file.txt",
    "localPath": "/local/file.txt",
    "serverName": "production"
  }
}
```

#### 4. `list-servers`

List all configured SSH servers and their status.

```json
{
  "tool": "list-servers",
  "arguments": {}
}
```

## 🔧 Configuration

### Security Configuration

#### Command Whitelist

- Use regex patterns to allow specific commands
- `["ls.*", "echo.*", "pwd"]` - Allow ls, echo commands and pwd
- `["*"]` - Allow all commands (use with blacklist)

#### Command Blacklist

- Use regex patterns to deny specific commands
- `["rm.*", "sudo.*"]` - Deny rm and sudo commands
- `[".*--force.*"]` - Deny any command with --force flag

#### Example Security Configurations

```bash
# Development environment - restrictive
--whitelist "git.*,npm.*,node.*,python.*" \
--blacklist ".*--force.*,rm.*"

# Production environment - very restrictive
--whitelist "ls,pwd,cat,grep" \
--blacklist "rm.*,sudo.*,chmod.*"

# Staging environment - moderate
--whitelist "*" \
--blacklist "rm -rf.*,sudo su.*,dd.*"
```

### Authentication Methods

#### Password Authentication

```bash
fastmcp-ssh-server --host server.com --username user --password secret
```

#### Private Key Authentication

```bash
# Without passphrase
fastmcp-ssh-server --host server.com --username user --private-key ~/.ssh/id_rsa

# With passphrase
fastmcp-ssh-server --host server.com --username user \
    --private-key ~/.ssh/id_rsa --passphrase mypassphrase
```

#### Mixed Authentication for Multiple Servers

```bash
# Use global password for connection strings without explicit auth
fastmcp-ssh-server --password globalpass \
    user1@server1.com \
    user2@server2.com
```

## 🧪 Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/your-username/fastmcp-ssh-server.git
cd fastmcp-ssh-server

# Install with development dependencies
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests with coverage
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --unit          # Unit tests only
python tests/run_tests.py --integration   # Integration tests only
python tests/run_tests.py --fast          # Fast tests only

# Run with verbose output
python tests/run_tests.py --verbose

# Generate coverage report
python tests/run_tests.py --coverage
```

### Code Quality

```bash
# Run linting and formatting
python tests/run_tests.py --lint

# Or run tools individually
ruff check python_src/
black python_src/
isort python_src/
mypy python_src/
```

### Project Structure

```
fastmcp-ssh-server/
├── python_src/
│   └── python_ssh_mcp/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # Module entry point
│       ├── main.py              # Main application entry
│       ├── server.py            # SSH MCP server implementation
│       ├── ssh_manager.py       # SSH connection manager
│       ├── cli.py               # Command line interface
│       ├── models.py            # Pydantic data models
│       ├── tools/               # MCP tools implementation
│       │   ├── __init__.py
│       │   ├── execute_command.py
│       │   ├── upload.py
│       │   ├── download.py
│       │   └── list_servers.py
│       └── utils/               # Utility modules
│           ├── __init__.py
│           ├── logger.py        # Logging system
│           └── error_handling.py
├── tests/                       # Test suite
├── docs/                        # Documentation
├── examples/                    # Usage examples
├── pyproject.toml              # Project configuration
└── README_PYTHON.md           # This file
```

## 📚 Documentation

- **[API Documentation](docs/api.md)** - Detailed MCP tools API reference
- **[Migration Guide](docs/migration.md)** - Migrating from TypeScript version
- **[Examples](examples/)** - Usage examples and configurations
- **[Test Documentation](tests/README.md)** - Testing guide and coverage
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## 🔄 Migration from TypeScript Version

This Python implementation is designed to be fully compatible with the TypeScript version. See our [Migration Guide](docs/migration.md) for detailed instructions on switching from the TypeScript implementation.

### Key Differences

| Feature           | TypeScript    | Python             |
| ----------------- | ------------- | ------------------ |
| **Framework**     | Native TS     | FastMCP            |
| **Performance**   | Good          | Enhanced           |
| **Async Support** | Promise-based | Native async/await |
| **Type Safety**   | TypeScript    | Pydantic           |
| **Testing**       | Jest          | pytest             |
| **Packaging**     | npm           | pip/uv             |

### API Compatibility

All MCP tools maintain the same interface:

- ✅ `execute-command` - Full compatibility
- ✅ `upload` - Full compatibility
- ✅ `download` - Full compatibility
- ✅ `list-servers` - Full compatibility

## 🚀 Deployment

### Docker Deployment (Coming Soon)

```bash
# Build Docker image
docker build -t fastmcp-ssh-server .

# Run container
docker run -d --name ssh-mcp-server \
    -e SSH_HOST=example.com \
    -e SSH_USER=myuser \
    -e SSH_PASS=mypass \
    fastmcp-ssh-server
```

### Systemd Service

```ini
# /etc/systemd/system/fastmcp-ssh-server.service
[Unit]
Description=FastMCP SSH Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/fastmcp-ssh-server
ExecStart=/opt/fastmcp-ssh-server/.venv/bin/fastmcp-ssh-server \
    --host prod.example.com \
    --username deploy \
    --private-key /opt/fastmcp-ssh-server/keys/deploy.key
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Production Considerations

- **Security**: Use private key authentication in production
- **Logging**: Configure structured logging with log rotation
- **Monitoring**: Set up health checks and monitoring
- **Backup**: Regular backup of configuration and keys
- **Updates**: Automated update strategy

## 🛠️ Troubleshooting

### Common Issues

#### Connection Issues

```bash
# Test SSH connection manually
ssh user@host -p port

# Check SSH key permissions
chmod 600 ~/.ssh/id_rsa

# Verbose SSH debugging
ssh -v user@host
```

#### Permission Issues

```bash
# Check file permissions
ls -la /path/to/private/key

# Fix key permissions
chmod 600 /path/to/private/key
chmod 700 ~/.ssh
```

#### Command Execution Issues

```bash
# Test command validation
fastmcp-ssh-server --host server.com --username user --password pass \
    --whitelist "ls.*" --blacklist "rm.*"
```

For more detailed troubleshooting, see [docs/troubleshooting.md](docs/troubleshooting.md).

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards

- **Python 3.12+** compatibility
- **Type hints** for all functions
- **Comprehensive tests** with 90%+ coverage
- **Documentation** for all public APIs
- **Security first** approach

## 📄 License

This project is licensed under the ISC License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[FastMCP](https://github.com/jlowin/fastmcp)** - The excellent MCP framework
- **[AsyncSSH](https://github.com/ronf/asyncssh)** - Robust SSH implementation
- **[Pydantic](https://github.com/pydantic/pydantic)** - Data validation and settings
- **[Typer](https://github.com/tiangolo/typer)** - Modern CLI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/fastmcp-ssh-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/fastmcp-ssh-server/discussions)
- **Documentation**: [docs/](docs/)

---

**FastMCP SSH Server** - Empowering AI models with secure, efficient SSH connectivity 🚀

# {{END_MODIFICATIONS}}
