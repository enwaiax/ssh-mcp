#!/bin/bash
# {{RIPER-5:
#   Action: "Added"
#   Task_ID: "3702898f-86db-43bb-aae0-0161b6a8eedf"
#   Timestamp: "2025-08-05T21:23:20+08:00"
#   Authoring_Role: "LD"
#   Principle_Applied: "部署自动化 + 系统服务配置"
#   Quality_Check: "完整的SystemD服务配置，包含安全配置和监控"
# }}
# {{START_MODIFICATIONS}}

# FastMCP SSH Server - SystemD Service Deployment
#
# This script sets up FastMCP SSH Server as a SystemD service
# for production deployment with proper security and monitoring.
#
# Usage: sudo ./systemd_service.sh

set -e  # Exit on any error

echo "🚀 FastMCP SSH Server - SystemD Service Setup"
echo "=" * 50

# Configuration
SERVICE_NAME="fastmcp-ssh-server"
INSTALL_DIR="/opt/fastmcp-ssh-server"
USER="mcp"
GROUP="mcp"

# SSH configuration (modify as needed)
SSH_HOST="${SSH_HOST:-prod.example.com}"
SSH_PORT="${SSH_PORT:-22}"
SSH_USERNAME="${SSH_USERNAME:-deploy}"
SSH_PRIVATE_KEY="${SSH_PRIVATE_KEY:-/opt/fastmcp-ssh-server/keys/deploy.key}"
WHITELIST="${WHITELIST:-git.*,npm.*,node.*,ls,pwd,echo.*}"
BLACKLIST="${BLACKLIST:-rm.*,sudo.*,chmod.*,dd.*}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

echo "📋 Deployment Configuration:"
echo "   Service: $SERVICE_NAME"
echo "   Install Dir: $INSTALL_DIR"
echo "   User: $USER"
echo "   SSH Host: $SSH_HOST"
echo "   SSH Key: $SSH_PRIVATE_KEY"

# Step 1: Create system user
echo ""
echo "👤 Creating system user and group..."
if ! id "$USER" &>/dev/null; then
    useradd --system --home-dir "$INSTALL_DIR" --shell /bin/false "$USER"
    echo "✅ Created user: $USER"
else
    echo "ℹ️  User already exists: $USER"
fi

# Step 2: Create installation directory
echo ""
echo "📁 Setting up installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/keys"
mkdir -p "$INSTALL_DIR/logs"

# Set ownership
chown -R "$USER:$GROUP" "$INSTALL_DIR"
chmod 750 "$INSTALL_DIR"
chmod 700 "$INSTALL_DIR/keys"

echo "✅ Installation directory ready: $INSTALL_DIR"

# Step 3: Install FastMCP SSH Server
echo ""
echo "📦 Installing FastMCP SSH Server..."

# Copy application files (assumes we're in the project directory)
if [[ -d "python_src" ]]; then
    cp -r python_src "$INSTALL_DIR/"
    cp pyproject.toml "$INSTALL_DIR/"

    # Install dependencies
    cd "$INSTALL_DIR"

    # Install uv if not present
    if ! command -v uv &> /dev/null; then
        echo "Installing uv package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
    fi

    # Install dependencies as the mcp user
    sudo -u "$USER" uv sync --no-dev

    echo "✅ FastMCP SSH Server installed"
else
    echo "❌ Error: python_src directory not found. Run this script from the project root."
    exit 1
fi

# Step 4: Create systemd service file
echo ""
echo "⚙️ Creating SystemD service file..."

cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=FastMCP SSH Server
Documentation=https://github.com/your-username/fastmcp-ssh-server
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$INSTALL_DIR

# Environment variables
Environment=PYTHONPATH=$INSTALL_DIR/python_src
Environment=SSH_HOST=$SSH_HOST
Environment=SSH_PORT=$SSH_PORT
Environment=SSH_USERNAME=$SSH_USERNAME
Environment=SSH_PRIVATE_KEY=$SSH_PRIVATE_KEY

# Command to run
ExecStart=$INSTALL_DIR/.venv/bin/fastmcp-ssh-server \\
    --host $SSH_HOST \\
    --port $SSH_PORT \\
    --username $SSH_USERNAME \\
    --private-key $SSH_PRIVATE_KEY \\
    --whitelist "$WHITELIST" \\
    --blacklist "$BLACKLIST"

# Restart policy
Restart=always
RestartSec=3
StartLimitBurst=5
StartLimitInterval=60

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$INSTALL_DIR/logs

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

echo "✅ SystemD service file created"

# Step 5: Set up SSH keys (if needed)
echo ""
echo "🔑 SSH Key Setup:"
if [[ ! -f "$SSH_PRIVATE_KEY" ]]; then
    echo "⚠️  SSH private key not found: $SSH_PRIVATE_KEY"
    echo "   Please copy your SSH private key to: $SSH_PRIVATE_KEY"
    echo "   Example: sudo cp ~/.ssh/id_rsa $SSH_PRIVATE_KEY"
    echo "   Remember to set proper permissions: sudo chmod 600 $SSH_PRIVATE_KEY"
else
    # Set proper permissions
    chown "$USER:$GROUP" "$SSH_PRIVATE_KEY"
    chmod 600 "$SSH_PRIVATE_KEY"
    echo "✅ SSH private key configured"
fi

# Step 6: Configure log rotation
echo ""
echo "📋 Setting up log rotation..."

cat > /etc/logrotate.d/${SERVICE_NAME} << EOF
$INSTALL_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    su $USER $GROUP
}
EOF

echo "✅ Log rotation configured"

# Step 7: Enable and start service
echo ""
echo "🔄 Configuring SystemD service..."

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable ${SERVICE_NAME}.service

echo "✅ Service enabled for startup"

# Step 8: Display management commands
echo ""
echo "🎛️ Service Management Commands:"
echo "   Start:    sudo systemctl start $SERVICE_NAME"
echo "   Stop:     sudo systemctl stop $SERVICE_NAME"
echo "   Restart:  sudo systemctl restart $SERVICE_NAME"
echo "   Status:   sudo systemctl status $SERVICE_NAME"
echo "   Logs:     sudo journalctl -u $SERVICE_NAME -f"

# Step 9: Firewall configuration (optional)
echo ""
echo "🔥 Firewall Configuration:"
if command -v ufw &> /dev/null; then
    echo "   UFW detected. Consider allowing SSH if needed:"
    echo "   sudo ufw allow ssh"
    echo "   sudo ufw allow $SSH_PORT/tcp"
elif command -v firewall-cmd &> /dev/null; then
    echo "   firewalld detected. Consider allowing SSH if needed:"
    echo "   sudo firewall-cmd --permanent --add-service=ssh"
    echo "   sudo firewall-cmd --permanent --add-port=$SSH_PORT/tcp"
    echo "   sudo firewall-cmd --reload"
fi

# Step 10: Security recommendations
echo ""
echo "🔒 Security Recommendations:"
echo "   1. Review and restrict SSH key permissions"
echo "   2. Configure SSH server to disable password authentication"
echo "   3. Use firewall to restrict access to SSH ports"
echo "   4. Monitor service logs regularly"
echo "   5. Keep system and dependencies updated"

# Step 11: Testing
echo ""
echo "🧪 Testing:"
echo "   To test the installation:"
echo "   1. sudo systemctl start $SERVICE_NAME"
echo "   2. sudo systemctl status $SERVICE_NAME"
echo "   3. sudo journalctl -u $SERVICE_NAME --no-pager"

echo ""
echo "✅ FastMCP SSH Server SystemD deployment completed!"
echo ""
echo "📝 Next Steps:"
echo "   1. Copy your SSH private key to: $SSH_PRIVATE_KEY"
echo "   2. Set proper key permissions: sudo chmod 600 $SSH_PRIVATE_KEY"
echo "   3. Start the service: sudo systemctl start $SERVICE_NAME"
echo "   4. Check status: sudo systemctl status $SERVICE_NAME"
echo ""
echo "🎉 Happy deploying!"

# {{END_MODIFICATIONS}}
