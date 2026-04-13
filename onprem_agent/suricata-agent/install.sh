#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Suricata + Agent Installer
# Supports: Ubuntu/Debian, RHEL/Rocky/Alma/CentOS, Fedora, Arch
# Run as root: sudo bash install.sh
# ─────────────────────────────────────────────────────────────
set -euo pipefail

AGENT_DIR="/opt/suricata-agent"
CONFIG_DIR="/etc/suricata-agent"
LOG_DIR="/var/log/suricata-agent"
SERVICE_NAME="suricata-agent"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[+]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
error()   { echo -e "${RED}[x]${NC} $*"; exit 1; }

[[ $EUID -ne 0 ]] && error "Please run as root (sudo bash install.sh)"

# ── Detect distro ──────────────────────────────────────────────
detect_distro() {
    if   [[ -f /etc/os-release ]]; then source /etc/os-release; echo "${ID:-unknown}"
    elif command -v lsb_release &>/dev/null; then lsb_release -si | tr '[:upper:]' '[:lower:]'
    else echo "unknown"
    fi
}

DISTRO=$(detect_distro)
info "Detected distro: $DISTRO"

# ── Install Suricata ───────────────────────────────────────────
install_suricata() {
    if command -v suricata &>/dev/null; then
        warn "Suricata already installed — skipping"
        return
    fi

    info "Installing Suricata..."
    case "$DISTRO" in
        ubuntu|debian|linuxmint|pop)
            apt-get update -qq
            apt-get install -y software-properties-common
            add-apt-repository -y ppa:oisf/suricata-stable 2>/dev/null || true
            apt-get update -qq
            apt-get install -y suricata
            ;;
        rhel|centos|rocky|almalinux|ol)
            dnf install -y epel-release
            dnf install -y suricata
            ;;
        fedora)
            dnf install -y suricata
            ;;
        arch|manjaro)
            pacman -Sy --noconfirm suricata
            ;;
        *)
            warn "Unknown distro '$DISTRO'. Attempting generic install..."
            if command -v apt-get &>/dev/null; then
                apt-get update -qq && apt-get install -y suricata
            elif command -v dnf &>/dev/null; then
                dnf install -y suricata
            elif command -v yum &>/dev/null; then
                yum install -y suricata
            else
                error "Cannot install Suricata automatically. Please install it manually then re-run."
            fi
            ;;
    esac
    info "Suricata installed: $(suricata --version 2>&1 | head -1)"
}

# ── Install Python deps ────────────────────────────────────────
install_python_deps() {
    info "Installing Python dependencies..."
    if ! command -v pip3 &>/dev/null; then
        case "$DISTRO" in
            ubuntu|debian|linuxmint|pop) apt-get install -y python3-pip ;;
            rhel|centos|rocky|almalinux|fedora|ol) dnf install -y python3-pip ;;
            arch|manjaro) pacman -Sy --noconfirm python-pip ;;
        esac
    fi
    pip3 install --quiet requests pyyaml
}

# ── Auto-detect primary network interface ─────────────────────
detect_interface() {
    ip route show default 2>/dev/null | awk '/default/ {print $5; exit}' || \
    ip link show | awk -F': ' '/^[0-9]+: (eth|ens|enp|em|bond|eno)/ {print $2; exit}'
}

# ── Configure Suricata ─────────────────────────────────────────
configure_suricata() {
    IFACE=$(detect_interface)
    [[ -z "$IFACE" ]] && { warn "Could not detect interface. Defaulting to eth0."; IFACE="eth0"; }
    info "Using network interface: $IFACE"

    SURICATA_CONF="/etc/suricata/suricata.yaml"
    [[ ! -f "$SURICATA_CONF" ]] && error "Suricata config not found at $SURICATA_CONF"

    # Set interface in suricata.yaml (af-packet section)
    sed -i "s/interface: .*/interface: $IFACE/" "$SURICATA_CONF" 2>/dev/null || true

    # Ensure EVE JSON logging is enabled
    if ! grep -q '"eve-log"' "$SURICATA_CONF" 2>/dev/null; then
        warn "EVE JSON logging may not be enabled. Please verify /etc/suricata/suricata.yaml manually."
    fi

    # Update community rules
    info "Updating Suricata rules (this may take a moment)..."
    suricata-update 2>&1 | tail -5 || warn "suricata-update failed — rules may be stale"
}

# ── Install agent ──────────────────────────────────────────────
install_agent() {
    info "Installing agent to $AGENT_DIR..."
    mkdir -p "$AGENT_DIR" "$CONFIG_DIR" "$LOG_DIR"

    cp "$(dirname "$0")/agent.py" "$AGENT_DIR/agent.py"
    chmod +x "$AGENT_DIR/agent.py"

    # Only copy config if one doesn't exist yet (don't overwrite user config)
    if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
        cp "$(dirname "$0")/config.yaml" "$CONFIG_DIR/config.yaml"
        warn "Config written to $CONFIG_DIR/config.yaml — edit api_endpoint and api_key before starting"
    else
        info "Existing config found at $CONFIG_DIR/config.yaml — not overwriting"
    fi

    cp "$(dirname "$0")/suricata-agent.service" /etc/systemd/system/
    systemctl daemon-reload
}

# ── Enable services ────────────────────────────────────────────
enable_services() {
    info "Enabling Suricata..."
    systemctl enable suricata
    systemctl restart suricata || warn "Could not start Suricata — check config"

    info "Enabling agent (not starting yet — configure API key first)..."
    systemctl enable "$SERVICE_NAME"

    echo ""
    echo "────────────────────────────────────────────────────"
    echo -e "${GREEN}Installation complete.${NC}"
    echo ""
    echo "  1. Edit your API key and endpoint:"
    echo "     ${YELLOW}nano $CONFIG_DIR/config.yaml${NC}"
    echo ""
    echo "  2. Start the agent:"
    echo "     ${YELLOW}systemctl start $SERVICE_NAME${NC}"
    echo ""
    echo "  3. Watch logs:"
    echo "     ${YELLOW}journalctl -fu $SERVICE_NAME${NC}"
    echo "────────────────────────────────────────────────────"
}

# ── Run ────────────────────────────────────────────────────────
install_suricata
install_python_deps
configure_suricata
install_agent
enable_services
