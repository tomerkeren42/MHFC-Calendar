#!/bin/bash

# Maccabi Haifa Calendar Auto-Sync Script
# Automatically monitors and updates Maccabi Haifa matches in Google Calendar

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_sync.py"
LOG_FILE="$SCRIPT_DIR/sync.log"
PID_FILE="$SCRIPT_DIR/sync.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if script is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warning "Sync script is already running (PID: $PID)"
            exit 1
        else
            # Remove stale PID file
            rm -f "$PID_FILE"
        fi
    fi
}

# Function to cleanup on exit
cleanup() {
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Function to check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        log_error "auto_sync.py not found in $SCRIPT_DIR"
        exit 1
    fi
    
    # Check if credentials exist
    if [ ! -f "$SCRIPT_DIR/credentials.json" ]; then
        log_error "credentials.json not found"
        log_error "Please download it from Google Cloud Console and place it in $SCRIPT_DIR"
        exit 1
    fi
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if required Python packages are installed
    if ! python3 -c "import requests, bs4, google.auth" &> /dev/null; then
        log_warning "Some required Python packages may be missing"
        log_info "Installing required packages..."
        pip3 install requests beautifulsoup4 google-auth google-auth-oauthlib google-api-python-client pytz
    fi
    
    log_success "Prerequisites check passed"
}

# Function to run sync
run_sync() {
    log_info "Starting Maccabi Haifa calendar sync..."
    log_info "Working directory: $SCRIPT_DIR"
    log_info "Log file: $LOG_FILE"
    
    # Store PID
    echo $$ > "$PID_FILE"
    
    # Change to script directory
    cd "$SCRIPT_DIR"
    
    # Run Python script
    if python3 "$PYTHON_SCRIPT"; then
        log_success "Sync completed successfully"
        return 0
    else
        log_error "Sync failed - check log file for details"
        return 1
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  run        Run sync once (default)"
    echo "  cron       Run in cron mode (silent, suitable for cron jobs)"
    echo "  daemon     Run continuously every 30 minutes"
    echo "  status     Show sync status and recent log entries"
    echo "  setup      Setup cron job for automatic syncing"
    echo "  logs       Show recent log entries"
    echo "  help       Show this help message"
    echo ""
    echo "Setup frequencies:"
    echo "  daily      Once per day at 9:00 AM (default)"
    echo "  hourly     Every hour"
    echo "  twice-daily Morning (9:00 AM) and evening (9:00 PM)"
    echo "  weekly     Weekly on Mondays at 9:00 AM"
    echo ""
    echo "Examples:"
    echo "  $0 run                    # Run sync once"
    echo "  $0 setup daily            # Setup daily sync (default)"
    echo "  $0 setup hourly           # Setup hourly sync"
    echo "  $0 setup twice-daily      # Setup twice daily sync"
    echo "  $0 daemon                 # Run continuously"
}

# Function to show status
show_status() {
    log_info "Maccabi Haifa Calendar Sync Status"
    echo "=================================="
    
    if [ -f "$SCRIPT_DIR/sync_state.json" ]; then
        echo "Last sync information:"
        python3 -c "
import json
try:
    with open('$SCRIPT_DIR/sync_state.json', 'r') as f:
        state = json.load(f)
    print('  Last sync: ' + state.get('last_sync', 'Never'))
    print('  Match count: ' + str(state.get('last_match_count', 'Unknown')))
    print('  Data hash: ' + str(state.get('last_hash', 'None'))[:16] + '...')
except Exception as e:
    print('  Error reading state: ' + str(e))"
        echo ""
    fi
    
    if [ -f "$LOG_FILE" ]; then
        echo "Recent log entries:"
        tail -10 "$LOG_FILE"
    else
        echo "No log file found"
    fi
}

# Function to setup cron job
setup_cron() {
    local frequency="${1:-hourly}"
    
    case "$frequency" in
        "hourly")
            CRON_JOB="0 * * * * cd $SCRIPT_DIR && ./sync_maccabi.sh cron >> sync.log 2>&1"
            DESCRIPTION="every hour"
            ;;
        "daily")
            CRON_JOB="0 12 * * * cd $SCRIPT_DIR && ./sync_maccabi.sh cron >> sync.log 2>&1"
            DESCRIPTION="daily at 12:00 PM"
            ;;
        "twice-daily")
            CRON_JOB="0 9,21 * * * cd $SCRIPT_DIR && ./sync_maccabi.sh cron >> sync.log 2>&1"
            DESCRIPTION="twice daily (9:00 AM and 9:00 PM)"
            ;;
        "weekly")
            CRON_JOB="0 9 * * 1 cd $SCRIPT_DIR && ./sync_maccabi.sh cron >> sync.log 2>&1"
            DESCRIPTION="weekly on Mondays at 9:00 AM"
            ;;
        *)
            log_error "Unknown frequency: $frequency"
            log_info "Available frequencies: hourly, daily, twice-daily, weekly"
            return 1
            ;;
    esac
    
    log_info "Setting up automatic sync $DESCRIPTION..."
    
    # Check if cron job already exists
    if crontab -l 2>/dev/null | grep -q "sync_maccabi.sh"; then
        log_warning "Cron job already exists"
        log_info "Current cron jobs:"
        crontab -l | grep "sync_maccabi.sh"
        
        read -p "Replace existing cron job? (y/N): " replace
        if [[ $replace =~ ^[Yy]$ ]]; then
            # Remove existing cron job
            crontab -l 2>/dev/null | grep -v "sync_maccabi.sh" | crontab -
            log_info "Removed existing cron job"
        else
            log_info "Keeping existing cron job"
            return 0
        fi
    fi
    
    # Add new cron job
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    log_success "Cron job added - will sync $DESCRIPTION"
    log_success $(crontab -l)
    log_info "To remove: crontab -e and delete the line with sync_maccabi.sh"
    log_info "To view: crontab -l"
}

# Function to run in daemon mode
run_daemon() {
    log_info "Starting daemon mode - syncing every 30 minutes"
    log_info "Press Ctrl+C to stop"
    
    while true; do
        run_sync
        log_info "Waiting 30 minutes until next sync..."
        sleep 1800  # 30 minutes
    done
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "=== Recent Sync Logs ==="
        tail -50 "$LOG_FILE"
    else
        log_warning "No log file found at $LOG_FILE"
    fi
}

# Main script logic
main() {
    case "${1:-run}" in
        "run")
            check_running
            check_prerequisites
            run_sync
            ;;
        "cron")
            # Silent mode for cron - no colored output
            RED=""
            GREEN=""
            YELLOW=""
            BLUE=""
            NC=""
            check_running
            cd "$SCRIPT_DIR"
            python3 "$PYTHON_SCRIPT" 2>&1
            ;;
        "daemon")
            check_running
            check_prerequisites
            run_daemon
            ;;
        "status")
            show_status
            ;;
        "setup")
            frequency="${2:-daily}"
            setup_cron "$frequency"
            ;;
        "logs")
            show_logs
            ;;
        "help"|"--help"|"-h")
            show_usage
            ;;
        *)
            log_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"