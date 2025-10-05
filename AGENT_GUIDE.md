# Agent Guide for repo-tickets

This guide enables AI agents to understand, interact with, and autonomously manage the repo-tickets system. The system is designed to be agent-friendly with clear CLI interfaces, structured data formats, and predictable workflows.

## 🤖 Overview for Agents

repo-tickets is a comprehensive project management system that handles:
- **Tickets**: Individual tasks and issues
- **Epics**: Large features composed of multiple tickets  
- **Backlogs**: Prioritized collections of work items
- **Requirements**: Detailed specifications linked to tickets

The system is built for autonomous operation with:
- Consistent CLI interface with `tickets` command
- JSON-based data storage for easy parsing
- Predictable file structure and naming conventions
- Machine-readable output formats

## 🚀 Quick Agent Start

### 1. System Check
First, verify the system is available:
```bash
# Check if repo-tickets is installed
tickets --help

# Check current directory for ticket system
ls -la | grep -E "\.(tickets|json|md)$"

# Initialize if needed
tickets init
```

### 2. Basic Agent Operations
```bash
# List all tickets (parseable output)
tickets list --format json

# Create a ticket programmatically  
tickets create --title "Agent Task" --description "Automated task creation" --priority high --status todo

# Check epic system
tickets epic list --format json

# Check backlog
tickets backlog list --format json
```

## 📋 Core Concepts for Agents

### Ticket Lifecycle
1. **Created** → Initial state
2. **Todo** → Ready for work
3. **In Progress** → Active development
4. **Done** → Completed
5. **Closed** → Archived

### Priority System
- **Critical**: P0 - System down, blocking
- **High**: P1 - Important features
- **Medium**: P2 - Standard work
- **Low**: P3 - Nice to have

### Epic-Ticket Relationships
```
Epic (Strategic Goal)
├── Ticket 1 (Implementation Task)
├── Ticket 2 (Testing Task)  
└── Ticket 3 (Documentation Task)
```

## 🛠️ Agent CLI Patterns

### Standard Command Structure
```bash
tickets <entity> <action> [options]
```

Where:
- `entity`: ticket, epic, backlog, requirement
- `action`: create, list, show, update, delete
- `options`: --format, --filter, --sort, etc.

### Essential Agent Commands

#### Ticket Management
```bash
# Create tickets
tickets create --title "Task" --description "Description" --priority high

# List with filtering
tickets list --status todo --priority high --format json

# Update tickets  
tickets update <id> --status "in-progress" --assignee "agent"

# Bulk operations
tickets list --status todo --format json | jq -r '.[] | .id' | xargs -I {} tickets update {} --assignee "agent"
```

#### Epic Management
```bash
# Create epic
tickets epic create --name "Feature Development" --description "Complete feature X"

# Add tickets to epic
tickets epic add-ticket <epic_id> <ticket_id>

# List epic tickets
tickets epic show <epic_id> --format json
```

#### Backlog Management
```bash
# Add to backlog
tickets backlog add --title "Feature Request" --description "User story" --priority_score 85

# Convert backlog to tickets
tickets backlog list --format json | jq -r '.[] | select(.priority_score > 80) | .id' | xargs -I {} tickets create --from-backlog {}
```

## 📊 Data Formats for Agents

### Ticket JSON Structure
```json
{
  "id": "TICK-001",
  "title": "Task Title",
  "description": "Task description",
  "status": "todo",
  "priority": "high", 
  "created_date": "2024-01-15",
  "assignee": null,
  "epic_id": null,
  "parent_ticket_id": null,
  "child_ticket_ids": [],
  "requirements": [],
  "tags": [],
  "estimated_hours": null,
  "actual_hours": null
}
```

### Epic JSON Structure  
```json
{
  "id": "EPIC-001",
  "name": "Epic Name",
  "description": "Epic description", 
  "goals": ["Goal 1", "Goal 2"],
  "success_criteria": ["Criteria 1", "Criteria 2"],
  "status": "active",
  "priority": "high",
  "start_date": "2024-01-15",
  "due_date": "2024-03-15",
  "assigned_tickets": ["TICK-001", "TICK-002"],
  "stakeholders": ["Product Owner"],
  "metadata": {}
}
```

### Backlog Item JSON Structure
```json
{
  "id": "BACK-001",
  "title": "Backlog Item",
  "description": "Item description",
  "priority_score": 75,
  "business_value": "high",
  "effort_estimate": "medium", 
  "created_date": "2024-01-15",
  "tags": ["feature"],
  "metadata": {}
}
```

## 🔄 Agent Workflow Patterns

### 1. Autonomous Ticket Creation
```bash
# Agent analyzes requirements and creates tickets
analyze_requirements() {
    # Read requirements file
    requirements=$(cat requirements.md)
    
    # Create tickets for each requirement
    echo "$requirements" | grep "^- " | while read -r req; do
        tickets create --title "$(echo $req | cut -d' ' -f2-)" --description "Auto-generated from requirements" --priority medium
    done
}
```

### 2. Epic-Driven Development  
```bash
# Agent creates epic and related tickets
create_feature_epic() {
    local feature_name="$1"
    
    # Create epic
    epic_id=$(tickets epic create --name "$feature_name" --description "Complete $feature_name development" --format json | jq -r '.id')
    
    # Create related tickets
    tickets create --title "$feature_name - API Development" --epic_id "$epic_id"
    tickets create --title "$feature_name - Frontend Implementation" --epic_id "$epic_id"  
    tickets create --title "$feature_name - Testing" --epic_id "$epic_id"
    tickets create --title "$feature_name - Documentation" --epic_id "$epic_id"
}
```

### 3. Backlog Grooming
```bash
# Agent prioritizes and converts backlog items
groom_backlog() {
    # Get high priority items
    high_priority=$(tickets backlog list --format json | jq -r '.[] | select(.priority_score > 80) | .id')
    
    # Convert to tickets
    for item_id in $high_priority; do
        tickets create --from-backlog "$item_id" --status todo
    done
}
```

### 4. Status Monitoring
```bash
# Agent monitors and updates ticket status
monitor_tickets() {
    # Check stale tickets
    tickets list --status "in-progress" --format json | jq -r '.[] | select(.updated_date < "2024-01-10") | .id' | while read -r ticket_id; do
        tickets update "$ticket_id" --add-comment "Agent: Checking on progress - ticket appears stale"
    done
}
```

## 📁 File System Structure for Agents

The system uses predictable file locations:

```
project-directory/
├── .tickets/                 # Main ticket storage
│   ├── tickets.json         # All tickets
│   ├── epics.json          # All epics
│   ├── backlog.json        # Backlog items
│   ├── requirements.json   # Requirements data
│   └── config.json         # System config
├── reports/                 # Generated reports
│   ├── status_report.html  # HTML status report
│   └── epic_progress.json  # Epic progress data
└── docs/                   # Documentation
    ├── README.md
    ├── AGENT_GUIDE.md      # This file
    └── examples/           # Example workflows
```

## 🔧 Agent Integration Points

### 1. Direct File Access
Agents can directly read/parse JSON files:
```python
import json

# Read tickets
with open('.tickets/tickets.json', 'r') as f:
    tickets = json.load(f)

# Filter and process
todo_tickets = [t for t in tickets if t['status'] == 'todo']
```

### 2. CLI Command Integration
Use subprocess or shell commands:
```python
import subprocess
import json

# Get tickets via CLI
result = subprocess.run(['tickets', 'list', '--format', 'json'], 
                       capture_output=True, text=True)
tickets = json.loads(result.stdout)
```

### 3. Environment Integration
```bash
# Set agent context
export TICKETS_AGENT="autonomous-agent-v1" 
export TICKETS_AUTO_ASSIGN="true"

# Use in commands
tickets create --assignee "$TICKETS_AGENT" --title "Agent Task"
```

## 🎯 Agent Success Patterns

### 1. Always Check System State
```bash
# Before any operation
tickets status --format json
tickets list --count-only
```

### 2. Use Consistent Formatting
```bash
# Always request JSON for parsing
tickets list --format json
tickets epic list --format json
```

### 3. Handle Errors Gracefully
```bash
# Check command success
if tickets create --title "Test" 2>/dev/null; then
    echo "Ticket created successfully"
else
    echo "Error creating ticket"
fi
```

### 4. Maintain Relationships
```bash
# When creating related tickets, maintain epic relationships
tickets create --title "Subtask" --parent_ticket_id "$parent_id"
```

## 🚨 Agent Safety Guidelines

### 1. Never Delete Without Confirmation
- Use `--dry-run` flags when available
- Always backup before bulk operations
- Prefer status changes over deletion

### 2. Validate Before Bulk Operations
```bash
# Count before bulk update
count=$(tickets list --status todo --format json | jq length)
echo "About to update $count tickets. Confirm? (y/n)"
```

### 3. Use Atomic Operations
- Create tickets one at a time for error handling
- Update individual fields rather than entire records
- Use transactions when possible

### 4. Maintain Audit Trail
```bash
# Always add comments for agent actions
tickets update "$id" --add-comment "Agent: Automated status update - task completed"
```

## 📈 Agent Reporting and Analytics

### Generate Status Reports
```bash
# Create comprehensive status report
tickets report --format json > daily_status.json

# Epic progress report
tickets epic list --format json | jq '.[] | {id, name, progress: (.assigned_tickets | length)}'
```

### Performance Metrics
```bash
# Ticket completion rate
tickets list --status done --format json | jq 'length'

# Average time in progress
tickets list --format json | jq '.[] | select(.status == "done") | .completion_time'
```

## 🔗 Integration Examples

See the `examples/` directory for:
- `agent_workflow.sh` - Complete agent workflow example
- `bulk_operations.py` - Python automation script
- `monitoring.sh` - Continuous monitoring script
- `epic_automation.py` - Epic management automation

## 📚 Additional Resources

- **AGENT_API.md**: Detailed API reference for programmatic access
- **examples/**: Practical automation scripts and workflows
- **README.md**: General system overview and human usage
- **FAST_TRACK.md**: Quick start guide for immediate productivity

## 🤝 Agent Collaboration

When multiple agents work with the system:

1. **Use unique agent identifiers**
   ```bash
   export TICKETS_AGENT_ID="agent-$(hostname)-$(date +%s)"
   ```

2. **Check for locks/conflicts**
   ```bash
   tickets status --check-locks
   ```

3. **Coordinate through ticket assignments**
   ```bash
   tickets list --assignee "other-agent" --status "in-progress"
   ```

4. **Use ticket comments for communication**
   ```bash
   tickets update "$id" --add-comment "Agent-A: Delegating to Agent-B for testing phase"
   ```

---

This guide enables agents to work autonomously with repo-tickets while maintaining system integrity and collaboration capabilities. For specific automation needs, refer to the examples directory and API documentation.