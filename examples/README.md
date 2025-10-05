# Agent Automation Examples

This directory contains practical examples and scripts that demonstrate how AI agents can autonomously work with the repo-tickets system.

## 📋 Available Examples

### 🤖 agent_workflow.sh
**Complete autonomous agent workflow demonstration**

This script shows a full end-to-end workflow where an AI agent:
- Checks system health and initializes if needed
- Creates epics with goals and success criteria  
- Populates product backlog with prioritized items
- Converts high-priority backlog items to tickets
- Creates implementation tickets with task breakdown
- Sets up subtask relationships
- Simulates work progress and status updates
- Generates comprehensive reports and analytics

```bash
# Run the complete workflow
./examples/agent_workflow.sh

# The script will create:
# - An "AI Features Enhancement" epic
# - 8 prioritized backlog items
# - Implementation tickets with time estimates
# - Subtasks for complex work items
# - Progress simulation and status updates
# - JSON reports and log files
```

**Generated Artifacts:**
- `agent_workflow.log` - Detailed execution log
- `agent_report.json` - Structured status report  
- `workflow_archives/` - Archived workflow results
- Epic and ticket structure for AI feature development

### 🐍 bulk_operations.py
**Python automation library for bulk ticket operations**

A comprehensive Python script that provides:
- Bulk ticket updates with flexible filtering
- Template-based ticket creation
- Automated ticket assignment based on content analysis
- Backlog prioritization algorithms
- Advanced analytics and reporting
- Performance metrics and recommendations

```bash
# Bulk update tickets
./examples/bulk_operations.py --operation bulk-update \
  --filters '{"status": "todo", "priority": "high"}' \
  --updates '{"assignee": "team-lead", "add_comment": "Escalated for urgent review"}'

# Create tickets from template
./examples/bulk_operations.py --operation create-from-template \
  --template '{"title": "Code Review", "priority": "medium", "status": "todo"}' \
  --count 5

# Auto-assign tickets based on content
./examples/bulk_operations.py --operation auto-assign

# Generate comprehensive analytics report
./examples/bulk_operations.py --operation generate-report --output-file analytics.json
```

**Features:**
- Smart content-based assignment rules
- Priority scoring algorithms  
- Team performance analytics
- Automated recommendations
- Extensible filtering and querying

### 📊 monitoring.sh
**Continuous system monitoring and alerting**

A monitoring agent that provides:
- Real-time system health checks
- Ticket metrics and trend analysis
- Epic progress monitoring
- Backlog health assessment
- Automated maintenance tasks
- Alert generation and reporting

```bash
# Run continuous monitoring (5-minute intervals)
./examples/monitoring.sh

# Single monitoring check
./examples/monitoring.sh --single-check

# Generate health summary
./examples/monitoring.sh --health-summary

# Run maintenance tasks
./examples/monitoring.sh --cleanup
```

**Monitoring Capabilities:**
- System health scoring (0-100)
- Critical ticket threshold alerts
- Stale ticket detection
- Epic completion tracking
- Backlog size and age analysis
- Automated backup and cleanup
- JSON reports and metrics logging

## 🛠️ Usage Patterns for Agents

### 1. Initial System Setup
```bash
# Check if system exists, initialize if needed
if [[ ! -d ".tickets" ]]; then
    tickets init
fi

# Verify system health
tickets list --format json >/dev/null 2>&1 || echo "System needs attention"
```

### 2. Epic-Driven Development
```bash
# Create epic and break down into tickets
epic_id=$(tickets epic create --name "Feature X" --format json | jq -r '.id')
tickets create --title "Feature X - Backend" --epic-id "$epic_id" --format json
tickets create --title "Feature X - Frontend" --epic-id "$epic_id" --format json
```

### 3. Backlog Management
```bash
# Add to backlog with scoring
tickets backlog add --title "New Feature" --priority-score 85 --business-value high --format json

# Convert high-priority items to tickets
tickets backlog list --format json | jq -r '.[] | select(.priority_score > 80) | .id' | \
  xargs -I {} tickets create --from-backlog {}
```

### 4. Batch Operations
```bash
# Update multiple tickets
tickets list --status todo --assignee "" --format json | jq -r '.[].id' | \
  xargs -I {} tickets update {} --assignee "agent" --add-comment "Auto-assigned by agent"
```

### 5. Progress Monitoring
```bash
# Check completion rates
total=$(tickets list --format json | jq length)
done_count=$(tickets list --status done --format json | jq length)
completion=$((done_count * 100 / total))
echo "Project completion: ${completion}%"
```

## 🔧 Customization Guide

### Extending agent_workflow.sh
Add your own phases by creating functions like:
```bash
my_custom_phase() {
    log "Phase X: Custom Operations"
    # Your custom logic here
    success "Custom phase completed"
}
```

### Extending bulk_operations.py
Add new operations by extending the TicketSystemAgent class:
```python
def my_custom_operation(self, params):
    """Custom bulk operation"""
    # Your implementation
    return results
```

### Extending monitoring.sh
Add custom health checks:
```bash
check_custom_metric() {
    log "Checking custom metric..."
    # Your monitoring logic
}
```

## 📊 Output Formats

All scripts generate structured output for easy agent consumption:

### JSON Reports
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "agent": "agent-name",
  "operation": "workflow",
  "results": {
    "tickets_created": 15,
    "epics_created": 1,
    "completion_rate": 75.5
  },
  "recommendations": [
    "Consider reviewing high-priority tickets",
    "Update stale in-progress items"
  ]
}
```

### Log Files
All scripts generate detailed logs with timestamps and structured information for audit trails and debugging.

## 🚨 Safety Guidelines

### For Production Use
1. **Test First**: Always test scripts in development environments
2. **Backup Data**: Ensure `.tickets/` directory is backed up
3. **Gradual Rollout**: Start with small batches for bulk operations
4. **Monitor Resources**: Watch system resource usage during bulk operations
5. **Validate Results**: Check outputs before applying at scale

### Error Handling
All scripts include comprehensive error handling and rollback capabilities where possible.

## 🤝 Integration Tips

### With CI/CD Pipelines
```yaml
# Example GitHub Actions integration
- name: Run Agent Workflow
  run: |
    ./examples/agent_workflow.sh
    
- name: Generate Reports
  run: |
    ./examples/bulk_operations.py --operation generate-report --output-file ${{ github.workspace }}/reports/agent-report.json
```

### With Monitoring Systems
The monitoring script can integrate with external systems by modifying the alert functions to send notifications to Slack, email, or other channels.

### With Team Workflows
Scripts can be adapted to work with existing team processes by customizing assignment rules, status transitions, and notification patterns.

---

These examples provide a solid foundation for building autonomous ticket management workflows. They demonstrate best practices for error handling, logging, and system integration while maintaining the flexibility to adapt to specific organizational needs.