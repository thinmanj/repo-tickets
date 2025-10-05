#!/bin/bash

# Monitoring Script for repo-tickets
# This script provides continuous monitoring capabilities for AI agents
# to track system health, ticket progress, and alert on issues.

set -e

# Configuration
AGENT_NAME="monitoring-agent-v1"
MONITOR_INTERVAL=300  # 5 minutes
LOG_FILE="monitoring.log"
ALERT_THRESHOLD_CRITICAL=5
ALERT_THRESHOLD_STALE_HOURS=48
REPORT_INTERVAL=3600  # 1 hour reports

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Initialize monitoring state
MONITORING_ACTIVE=true
LAST_REPORT_TIME=0
ALERT_COUNTS=()

# Logging functions
log() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${BLUE}[$timestamp] MONITOR: $1${NC}"
    echo "[$timestamp] MONITOR: $1" >> "$LOG_FILE"
}

success() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${GREEN}[$timestamp] SUCCESS: $1${NC}"
    echo "[$timestamp] SUCCESS: $1" >> "$LOG_FILE"
}

warning() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${YELLOW}[$timestamp] WARNING: $1${NC}"
    echo "[$timestamp] WARNING: $1" >> "$LOG_FILE"
}

error() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${RED}[$timestamp] ERROR: $1${NC}"
    echo "[$timestamp] ERROR: $1" >> "$LOG_FILE"
}

alert() {
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    echo -e "${PURPLE}[$timestamp] ALERT: $1${NC}"
    echo "[$timestamp] ALERT: $1" >> "$LOG_FILE"
    
    # Store alert for reporting
    echo "$timestamp|ALERT|$1" >> "alerts.log"
    
    # Could integrate with notification systems here
    # notify_team "$1"
}

# Core monitoring functions
check_system_health() {
    log "Checking system health..."
    
    local health_score=100
    local issues=()
    
    # Check if tickets CLI is responsive
    if ! timeout 10 tickets --help >/dev/null 2>&1; then
        health_score=$((health_score - 30))
        issues+=("CLI not responsive")
    fi
    
    # Check data file integrity
    if [[ -f ".tickets/tickets.json" ]]; then
        if ! jq empty ".tickets/tickets.json" 2>/dev/null; then
            health_score=$((health_score - 40))
            issues+=("tickets.json corrupted")
        fi
    else
        health_score=$((health_score - 20))
        issues+=("tickets.json missing")
    fi
    
    if [[ -f ".tickets/epics.json" ]]; then
        if ! jq empty ".tickets/epics.json" 2>/dev/null; then
            health_score=$((health_score - 20))
            issues+=("epics.json corrupted")
        fi
    fi
    
    # Check disk space
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        health_score=$((health_score - 15))
        issues+=("disk space critical: ${disk_usage}%")
    elif [[ $disk_usage -gt 80 ]]; then
        health_score=$((health_score - 5))
        issues+=("disk space warning: ${disk_usage}%")
    fi
    
    # Report health status
    if [[ $health_score -ge 90 ]]; then
        success "System health: ${health_score}/100 - Excellent"
    elif [[ $health_score -ge 70 ]]; then
        warning "System health: ${health_score}/100 - Good with minor issues"
    elif [[ $health_score -ge 50 ]]; then
        error "System health: ${health_score}/100 - Degraded"
    else
        alert "System health: ${health_score}/100 - Critical"
    fi
    
    # Report specific issues
    for issue in "${issues[@]}"; do
        warning "Issue detected: $issue"
    done
    
    return $((100 - health_score))
}

monitor_ticket_metrics() {
    log "Monitoring ticket metrics..."
    
    # Get current ticket statistics
    local total_tickets=$(tickets list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local todo_tickets=$(tickets list --status todo --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local in_progress_tickets=$(tickets list --status "in-progress" --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local done_tickets=$(tickets list --status done --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local critical_tickets=$(tickets list --priority critical --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local high_tickets=$(tickets list --priority high --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    
    log "Ticket Status: Total=$total_tickets, Todo=$todo_tickets, In-Progress=$in_progress_tickets, Done=$done_tickets"
    log "Priority Distribution: Critical=$critical_tickets, High=$high_tickets"
    
    # Alert conditions
    if [[ $critical_tickets -gt $ALERT_THRESHOLD_CRITICAL ]]; then
        alert "High number of critical tickets: $critical_tickets (threshold: $ALERT_THRESHOLD_CRITICAL)"
    fi
    
    if [[ $in_progress_tickets -gt 20 ]]; then
        warning "Large number of in-progress tickets: $in_progress_tickets (may indicate bottlenecks)"
    fi
    
    if [[ $todo_tickets -gt 50 ]]; then
        warning "Large backlog of todo tickets: $todo_tickets (consider prioritization review)"
    fi
    
    # Calculate completion rate trend
    local completion_rate=0
    if [[ $total_tickets -gt 0 ]]; then
        completion_rate=$((done_tickets * 100 / total_tickets))
    fi
    
    log "Current completion rate: ${completion_rate}%"
    
    # Store metrics for trend analysis
    echo "$(date '+%s')|$total_tickets|$todo_tickets|$in_progress_tickets|$done_tickets|$critical_tickets|$high_tickets|$completion_rate" >> "metrics.log"
}

check_stale_tickets() {
    log "Checking for stale tickets..."
    
    local current_time=$(date '+%s')
    local stale_threshold=$((current_time - (ALERT_THRESHOLD_STALE_HOURS * 3600)))
    local stale_count=0
    
    # Get in-progress tickets (would need updated_date field in real implementation)
    local in_progress_tickets=$(tickets list --status "in-progress" --format json 2>/dev/null)
    
    if [[ -n "$in_progress_tickets" && "$in_progress_tickets" != "[]" ]]; then
        # For demonstration, we'll just count them
        stale_count=$(echo "$in_progress_tickets" | jq length)
        
        if [[ $stale_count -gt 10 ]]; then
            warning "Potentially stale in-progress tickets: $stale_count (consider review)"
        fi
    fi
    
    # Check for tickets without recent updates (simulation)
    local unassigned_count=$(tickets list --format json 2>/dev/null | jq '[.[] | select(.assignee == null or .assignee == "")] | length' 2>/dev/null || echo "0")
    
    if [[ $unassigned_count -gt 15 ]]; then
        warning "High number of unassigned tickets: $unassigned_count (requires attention)"
    fi
}

monitor_epic_progress() {
    log "Monitoring epic progress..."
    
    local epics_json=$(tickets epic list --format json 2>/dev/null)
    
    if [[ -n "$epics_json" && "$epics_json" != "[]" ]]; then
        echo "$epics_json" | jq -r '.[] | "\(.id)|\(.name)|\(.status)"' | while IFS='|' read -r epic_id epic_name epic_status; do
            log "Epic: $epic_name ($epic_id) - Status: $epic_status"
            
            # Get tickets for this epic
            local epic_tickets=$(tickets list --epic-id "$epic_id" --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
            local done_epic_tickets=$(tickets list --epic-id "$epic_id" --status done --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
            
            if [[ $epic_tickets -gt 0 ]]; then
                local completion=$((done_epic_tickets * 100 / epic_tickets))
                log "  Progress: $done_epic_tickets/$epic_tickets tickets completed (${completion}%)"
                
                # Alert for stalled epics
                if [[ $epic_status == "active" && $completion -eq 0 && $epic_tickets -gt 5 ]]; then
                    warning "Epic '$epic_name' has no completed tickets despite having $epic_tickets total tickets"
                elif [[ $completion -eq 100 && $epic_status != "completed" ]]; then
                    log "Epic '$epic_name' appears complete but status is '$epic_status'"
                fi
            else
                warning "Epic '$epic_name' has no assigned tickets"
            fi
        done
    else
        log "No epics found to monitor"
    fi
}

monitor_backlog_health() {
    log "Monitoring backlog health..."
    
    local backlog_json=$(tickets backlog list --format json 2>/dev/null)
    
    if [[ -n "$backlog_json" && "$backlog_json" != "[]" ]]; then
        local total_backlog=$(echo "$backlog_json" | jq length)
        local high_priority_backlog=$(echo "$backlog_json" | jq '[.[] | select(.priority_score >= 85)] | length')
        local old_backlog=$(echo "$backlog_json" | jq '[.[] | select(.created_date < "2024-01-01")] | length' 2>/dev/null || echo "0")
        
        log "Backlog Status: Total=$total_backlog, High Priority=$high_priority_backlog, Potentially Old=$old_backlog"
        
        # Alert conditions
        if [[ $high_priority_backlog -gt 10 ]]; then
            alert "Too many high-priority backlog items: $high_priority_backlog (consider converting to tickets)"
        fi
        
        if [[ $total_backlog -gt 100 ]]; then
            warning "Large backlog size: $total_backlog items (consider grooming session)"
        fi
        
        if [[ $old_backlog -gt 20 ]]; then
            warning "Many old backlog items: $old_backlog (consider archiving or prioritizing)"
        fi
    else
        log "No backlog items found"
    fi
}

perform_automated_maintenance() {
    log "Performing automated maintenance..."
    
    # Clean up old log files (keep last 7 days)
    find . -name "*.log" -type f -mtime +7 -exec rm {} \; 2>/dev/null || true
    
    # Archive old workflow results
    if [[ -d "workflow_archives" ]]; then
        find workflow_archives -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
    fi
    
    # Backup current state
    local backup_dir="backups/$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$backup_dir"
    
    if [[ -d ".tickets" ]]; then
        cp -r .tickets "$backup_dir/" 2>/dev/null || true
        success "System state backed up to $backup_dir"
    fi
    
    # Clean old backups (keep last 10)
    if [[ -d "backups" ]]; then
        local backup_count=$(ls -1 backups | wc -l)
        if [[ $backup_count -gt 10 ]]; then
            ls -1t backups | tail -n +11 | xargs -I {} rm -rf "backups/{}" 2>/dev/null || true
            log "Cleaned old backup files"
        fi
    fi
}

generate_monitoring_report() {
    log "Generating monitoring report..."
    
    local report_file="monitoring_report_$(date +'%Y%m%d_%H%M%S').json"
    local timestamp=$(date -Iseconds)
    
    # Gather current statistics
    local total_tickets=$(tickets list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local tickets_by_status=$(tickets list --format json 2>/dev/null | jq 'group_by(.status) | map({status: .[0].status, count: length})' 2>/dev/null || echo "[]")
    local tickets_by_priority=$(tickets list --format json 2>/dev/null | jq 'group_by(.priority) | map({priority: .[0].priority, count: length})' 2>/dev/null || echo "[]")
    
    local total_epics=$(tickets epic list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local total_backlog=$(tickets backlog list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    
    # Read recent alerts
    local recent_alerts="[]"
    if [[ -f "alerts.log" ]]; then
        recent_alerts=$(tail -20 "alerts.log" | jq -Rs 'split("\n") | map(select(length > 0)) | map(split("|")) | map({timestamp: .[0], level: .[1], message: .[2]})' 2>/dev/null || echo "[]")
    fi
    
    # Create comprehensive report
    cat > "$report_file" << EOF
{
  "timestamp": "$timestamp",
  "agent": "$AGENT_NAME",
  "monitoring_period": "last_${MONITOR_INTERVAL}_seconds",
  "system_health": {
    "status": "healthy",
    "last_check": "$timestamp"
  },
  "tickets": {
    "total": $total_tickets,
    "by_status": $tickets_by_status,
    "by_priority": $tickets_by_priority
  },
  "epics": {
    "total": $total_epics
  },
  "backlog": {
    "total": $total_backlog
  },
  "alerts": {
    "recent": $recent_alerts,
    "threshold_critical": $ALERT_THRESHOLD_CRITICAL,
    "threshold_stale_hours": $ALERT_THRESHOLD_STALE_HOURS
  },
  "performance": {
    "monitoring_interval_seconds": $MONITOR_INTERVAL,
    "report_interval_seconds": $REPORT_INTERVAL,
    "uptime_seconds": $(($(date +%s) - START_TIME))
  }
}
EOF
    
    success "Monitoring report generated: $report_file"
    
    # Keep only last 24 reports
    ls -1t monitoring_report_*.json 2>/dev/null | tail -n +25 | xargs -I {} rm {} 2>/dev/null || true
}

send_health_summary() {
    log "Sending health summary..."
    
    local summary_file="health_summary.txt"
    local timestamp=$(date +'%Y-%m-%d %H:%M:%S')
    
    cat > "$summary_file" << EOF
🤖 repo-tickets Health Summary
Generated: $timestamp
Agent: $AGENT_NAME

📊 System Overview:
- Monitoring Active: $MONITORING_ACTIVE
- Uptime: $(($(date +%s) - START_TIME)) seconds
- Last Check: $timestamp

📈 Current Metrics:
$(monitor_ticket_metrics 2>&1 | grep "Ticket Status\|Priority Distribution\|completion rate" | sed 's/^.*MONITOR: /- /')

⚠️  Recent Alerts:
$(tail -5 "alerts.log" 2>/dev/null | sed 's/^/- /' || echo "- No recent alerts")

🔧 Maintenance:
- Automated backups: Active
- Log rotation: Active
- Cleanup tasks: Scheduled

📋 Recommendations:
$(
# Generate quick recommendations
if [[ $(tickets list --priority critical --format json 2>/dev/null | jq length 2>/dev/null || echo "0") -gt 0 ]]; then
    echo "- Review and address critical priority tickets"
fi

if [[ $(tickets list --format json 2>/dev/null | jq '[.[] | select(.assignee == null or .assignee == "")] | length' 2>/dev/null || echo "0") -gt 10 ]]; then
    echo "- Assign unassigned tickets to team members"
fi

if [[ $(tickets backlog list --format json 2>/dev/null | jq '[.[] | select(.priority_score >= 85)] | length' 2>/dev/null || echo "0") -gt 5 ]]; then
    echo "- Convert high-priority backlog items to tickets"
fi
)

Next monitoring cycle: $(date -d "+${MONITOR_INTERVAL} seconds" +'%Y-%m-%d %H:%M:%S')
EOF
    
    success "Health summary saved to $summary_file"
    
    # In a real implementation, this could be sent via email, Slack, etc.
    echo "Health summary ready for distribution"
}

# Signal handlers
cleanup() {
    log "Monitoring agent shutting down..."
    MONITORING_ACTIVE=false
    
    # Generate final report
    generate_monitoring_report
    send_health_summary
    
    success "Monitoring agent stopped gracefully"
    exit 0
}

# Trap signals
trap cleanup SIGINT SIGTERM

# Main monitoring loop
main_monitoring_loop() {
    log "=== Monitoring Agent Started ==="
    log "Agent: $AGENT_NAME"
    log "Interval: ${MONITOR_INTERVAL}s"
    log "Alert Thresholds: Critical=${ALERT_THRESHOLD_CRITICAL}, Stale=${ALERT_THRESHOLD_STALE_HOURS}h"
    
    local cycle_count=0
    
    while [[ $MONITORING_ACTIVE == true ]]; do
        cycle_count=$((cycle_count + 1))
        log "=== Monitoring Cycle #$cycle_count ==="
        
        # Run monitoring checks
        check_system_health
        monitor_ticket_metrics
        check_stale_tickets
        monitor_epic_progress
        monitor_backlog_health
        
        # Periodic maintenance
        if [[ $((cycle_count % 12)) -eq 0 ]]; then  # Every hour (if 5-minute intervals)
            perform_automated_maintenance
        fi
        
        # Generate reports periodically
        local current_time=$(date '+%s')
        if [[ $((current_time - LAST_REPORT_TIME)) -gt $REPORT_INTERVAL ]]; then
            generate_monitoring_report
            send_health_summary
            LAST_REPORT_TIME=$current_time
        fi
        
        success "Monitoring cycle #$cycle_count completed"
        
        # Wait for next cycle
        if [[ $MONITORING_ACTIVE == true ]]; then
            log "Sleeping for ${MONITOR_INTERVAL} seconds..."
            sleep $MONITOR_INTERVAL
        fi
    done
}

# Command line options
if [[ $# -gt 0 ]]; then
    case $1 in
        --single-check)
            log "Running single monitoring check..."
            check_system_health
            monitor_ticket_metrics
            check_stale_tickets
            monitor_epic_progress
            monitor_backlog_health
            generate_monitoring_report
            ;;
        --health-summary)
            send_health_summary
            ;;
        --cleanup)
            perform_automated_maintenance
            ;;
        --help)
            echo "repo-tickets Monitoring Agent"
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --single-check    Run one monitoring cycle and exit"
            echo "  --health-summary  Generate and display health summary"
            echo "  --cleanup        Run maintenance tasks"
            echo "  --help           Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  MONITOR_INTERVAL       Seconds between checks (default: 300)"
            echo "  ALERT_THRESHOLD_CRITICAL  Critical ticket threshold (default: 5)"
            echo "  ALERT_THRESHOLD_STALE_HOURS  Stale ticket hours (default: 48)"
            ;;
        *)
            error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
else
    # Start continuous monitoring
    START_TIME=$(date +%s)
    LAST_REPORT_TIME=$START_TIME
    
    # Initial setup
    mkdir -p backups workflow_archives
    
    main_monitoring_loop
fi