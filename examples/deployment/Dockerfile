# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"
#   Timestamp: "2025-08-05T21:23:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "容器化部署 + 安全最佳实践"
#   Quality_Check: "完整的Docker配置，多阶段构建，安全配置"
# }}
# {{START_MODIFICATIONS}}

# FastMCP SSH Server - Docker Deployment
# 
# Multi-stage Docker build for production deployment
# 
# Build: docker build -t fastmcp-ssh-server .
# Run:   docker run -d --name ssh-mcp-server \
#          -e SSH_HOST=example.com \
#          -e SSH_USERNAME=user \
#          -e SSH_PASSWORD=pass \
#          fastmcp-ssh-server

# Stage 1: Build environment
FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY python_src/ ./python_src/

# Install dependencies
RUN uv sync --no-dev

# Stage 2: Production runtime
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r mcp && useradd -r -g mcp -d /app -s /bin/false mcp

# Set working directory
WORKDIR /app

# Copy application and virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/python_src /app/python_src
COPY --from=builder /app/pyproject.toml /app/pyproject.toml

# Create directories for SSH keys and logs
RUN mkdir -p /app/keys /app/logs && \
    chown -R mcp:mcp /app && \
    chmod 700 /app/keys

# Set environment variables
ENV PYTHONPATH=/app/python_src
ENV PATH="/app/.venv/bin:$PATH"

# Default configuration
ENV SSH_HOST=localhost
ENV SSH_PORT=22
ENV SSH_USERNAME=user
ENV SSH_PASSWORD=
ENV SSH_PRIVATE_KEY=/app/keys/id_rsa
ENV SSH_PASSPHRASE=
ENV WHITELIST="ls,pwd,echo.*,uptime,whoami"
ENV BLACKLIST="rm.*,sudo.*,chmod.*"
ENV LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "
import sys
sys.path.insert(0, '/app/python_src')
from python_ssh_mcp.utils import Logger
Logger.info('Health check')
" || exit 1

# Switch to non-root user
USER mcp

# Expose any ports if needed (none for MCP over stdin/stdout)
# EXPOSE 8080

# Volume for SSH keys and configuration
VOLUME ["/app/keys", "/app/logs"]

# Entry point script
COPY --chown=mcp:mcp <<'EOF' /app/entrypoint.sh
#!/bin/bash
set -e

echo "🐳 FastMCP SSH Server - Docker Container"
echo "=================================="

# Display configuration
echo "📋 Configuration:"
echo "   SSH Host: ${SSH_HOST}"
echo "   SSH Port: ${SSH_PORT}"
echo "   SSH User: ${SSH_USERNAME}"
echo "   SSH Key:  ${SSH_PRIVATE_KEY}"
echo "   Whitelist: ${WHITELIST}"
echo "   Blacklist: ${BLACKLIST}"
echo "   Log Level: ${LOG_LEVEL}"

# Check SSH key if using key authentication
if [[ -n "$SSH_PRIVATE_KEY" && -f "$SSH_PRIVATE_KEY" ]]; then
    echo "🔑 Using SSH private key: $SSH_PRIVATE_KEY"
    # Check key permissions
    if [[ "$(stat -c %a "$SSH_PRIVATE_KEY")" != "600" ]]; then
        echo "⚠️  Warning: SSH key permissions should be 600"
    fi
elif [[ -z "$SSH_PASSWORD" ]]; then
    echo "❌ Error: No SSH password or private key provided"
    echo "   Set SSH_PASSWORD or mount SSH key to ${SSH_PRIVATE_KEY}"
    exit 1
fi

# Build command arguments
ARGS=(
    --host "$SSH_HOST"
    --port "$SSH_PORT"
    --username "$SSH_USERNAME"
)

# Add authentication
if [[ -n "$SSH_PASSWORD" ]]; then
    ARGS+=(--password "$SSH_PASSWORD")
elif [[ -f "$SSH_PRIVATE_KEY" ]]; then
    ARGS+=(--private-key "$SSH_PRIVATE_KEY")
    if [[ -n "$SSH_PASSPHRASE" ]]; then
        ARGS+=(--passphrase "$SSH_PASSPHRASE")
    fi
fi

# Add security settings
ARGS+=(
    --whitelist "$WHITELIST"
    --blacklist "$BLACKLIST"
)

echo "🚀 Starting FastMCP SSH Server..."
exec fastmcp-ssh-server "${ARGS[@]}"
EOF

RUN chmod +x /app/entrypoint.sh

# Default command
ENTRYPOINT ["/app/entrypoint.sh"]

# Metadata
LABEL \
    org.opencontainers.image.title="FastMCP SSH Server" \
    org.opencontainers.image.description="FastMCP-based SSH server for Model Context Protocol" \
    org.opencontainers.image.version="0.1.0" \
    org.opencontainers.image.vendor="FastMCP SSH Server Project" \
    org.opencontainers.image.licenses="ISC" \
    org.opencontainers.image.source="https://github.com/your-username/fastmcp-ssh-server"

# {{END_MODIFICATIONS}}