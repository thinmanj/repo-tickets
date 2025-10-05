# Agent API Reference for repo-tickets

This document provides detailed technical specifications for AI agents to programmatically interact with the repo-tickets system. It covers data structures, file formats, CLI interfaces, and automation patterns.

## 📋 Table of Contents

- [Data Models](#data-models)
- [File System API](#file-system-api)
- [CLI Interface](#cli-interface)
- [JSON Schemas](#json-schemas)
- [Automation Patterns](#automation-patterns)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)

## 🗄️ Data Models

### Ticket Data Model
```python
class Ticket:
    id: str                    # Format: TICK-001, TICK-002, etc.
    title: str                 # Brief title (max 200 chars)
    description: str           # Detailed description (unlimited)
    status: str                # created|todo|in-progress|done|closed
    priority: str              # critical|high|medium|low
    created_date: str          # ISO 8601 format (YYYY-MM-DD)
    updated_date: str          # ISO 8601 format (YYYY-MM-DD)
    assignee: str|null         # Assignee name or null
    epic_id: str|null          # Parent epic ID or null
    parent_ticket_id: str|null # Parent ticket ID for subtasks
    child_ticket_ids: list[str] # List of child ticket IDs
    requirements: list[str]     # List of requirement IDs
    tags: list[str]            # Arbitrary tags
    estimated_hours: int|null   # Estimated work hours
    actual_hours: int|null     # Actual work hours
    metadata: dict             # Additional custom fields
```

### Epic Data Model
```python
class Epic:
    id: str                    # Format: EPIC-001, EPIC-002, etc.
    name: str                  # Epic name (max 200 chars)
    description: str           # Detailed description
    goals: list[str]           # List of epic goals
    success_criteria: list[str] # List of success criteria
    status: str                # active|completed|cancelled
    priority: str              # critical|high|medium|low
    start_date: str|null       # ISO 8601 format (YYYY-MM-DD)
    due_date: str|null         # ISO 8601 format (YYYY-MM-DD)
    assigned_tickets: list[str] # List of ticket IDs in this epic
    stakeholders: list[str]     # List of stakeholder names
    metadata: dict             # Additional custom fields
```

### Backlog Item Data Model
```python
class BacklogItem:
    id: str                    # Format: BACK-001, BACK-002, etc.
    title: str                 # Item title (max 200 chars)
    description: str           # Detailed description
    priority_score: int        # 0-100 priority score
    business_value: str        # high|medium|low
    effort_estimate: str       # high|medium|low
    created_date: str          # ISO 8601 format (YYYY-MM-DD)
    tags: list[str]            # Arbitrary tags
    metadata: dict             # Additional custom fields
```

## 📁 File System API

### File Structure
```
.tickets/
├── tickets.json      # Array of all tickets
├── epics.json        # Array of all epics
├── backlog.json      # Array of all backlog items
├── requirements.json # Array of all requirements
├── config.json       # System configuration
└── metadata.json     # System metadata (counters, etc.)
```

### Reading Data Files

#### Direct File Access (Python)
```python
import json
from pathlib import Path

def read_tickets():
    """Read all tickets from the JSON file."""
    tickets_file = Path('.tickets/tickets.json')
    if tickets_file.exists():
        with open(tickets_file, 'r') as f:
            return json.load(f)
    return []

def read_epics():
    """Read all epics from the JSON file."""
    epics_file = Path('.tickets/epics.json')
    if epics_file.exists():
        with open(epics_file, 'r') as f:
            return json.load(f)
    return []

def read_backlog():
    """Read all backlog items from the JSON file."""
    backlog_file = Path('.tickets/backlog.json')
    if backlog_file.exists():
        with open(backlog_file, 'r') as f:
            return json.load(f)
    return []
```

#### Safe File Writing (Python)
```python
import json
import os
from pathlib import Path

def write_tickets(tickets):
    """Safely write tickets to the JSON file."""
    tickets_dir = Path('.tickets')
    tickets_dir.mkdir(exist_ok=True)
    
    tickets_file = tickets_dir / 'tickets.json'
    temp_file = tickets_dir / 'tickets.json.tmp'
    
    # Write to temp file first
    with open(temp_file, 'w') as f:
        json.dump(tickets, f, indent=2, ensure_ascii=False)
    
    # Atomic rename
    os.rename(temp_file, tickets_file)
```

### Configuration File Format
```json
{
  "version": "1.0.0",
  "ticket_counter": 42,
  "epic_counter": 5,
  "backlog_counter": 15,
  "default_assignee": null,
  "auto_assign_enabled": false,
  "priority_levels": ["critical", "high", "medium", "low"],
  "status_transitions": {
    "created": ["todo", "closed"],
    "todo": ["in-progress", "closed"],
    "in-progress": ["done", "todo"],
    "done": ["closed", "todo"],
    "closed": []
  }
}
```

## 🔧 CLI Interface

### Command Structure
All CLI commands follow the pattern:
```bash
tickets <entity> <action> [options]
```

### Global Options
```bash
--format json|table|csv    # Output format
--verbose                  # Verbose output
--quiet                    # Suppress output
--dry-run                  # Preview changes only
--config-file PATH         # Custom config file
```

### Ticket Commands

#### Create Ticket
```bash
tickets create [options]

Options:
  --title TEXT           # Required: Ticket title
  --description TEXT     # Ticket description
  --priority LEVEL       # critical|high|medium|low
  --status STATUS        # created|todo|in-progress|done|closed
  --assignee NAME        # Assignee name
  --epic-id ID           # Parent epic ID
  --parent-ticket-id ID  # Parent ticket ID
  --tags TAG1,TAG2       # Comma-separated tags
  --estimated-hours INT  # Estimated hours
  --from-backlog ID      # Create from backlog item
  --format FORMAT        # Output format

Returns:
  JSON: {"id": "TICK-001", "status": "created", ...}
  Table: Formatted table with ticket details
```

#### List Tickets
```bash
tickets list [options]

Options:
  --status STATUS        # Filter by status
  --priority LEVEL       # Filter by priority  
  --assignee NAME        # Filter by assignee
  --epic-id ID           # Filter by epic
  --tags TAG1,TAG2       # Filter by tags
  --limit INT            # Limit results
  --offset INT           # Offset for pagination
  --sort-by FIELD        # Sort field
  --sort-order asc|desc  # Sort order
  --format FORMAT        # Output format
  --count-only           # Return count only

Returns:
  JSON: [{"id": "TICK-001", ...}, {"id": "TICK-002", ...}]
  Table: Formatted table
  Count: Integer count
```

#### Update Ticket
```bash
tickets update <ticket-id> [options]

Options:
  --title TEXT           # Update title
  --description TEXT     # Update description
  --status STATUS        # Update status
  --priority LEVEL       # Update priority
  --assignee NAME        # Update assignee
  --add-tag TAG          # Add tag
  --remove-tag TAG       # Remove tag
  --estimated-hours INT  # Update estimated hours
  --actual-hours INT     # Update actual hours
  --add-comment TEXT     # Add comment to history
  --format FORMAT        # Output format

Returns:
  JSON: {"id": "TICK-001", "updated": true, ...}
```

### Epic Commands

#### Create Epic
```bash
tickets epic create [options]

Options:
  --name TEXT            # Required: Epic name
  --description TEXT     # Epic description
  --goals GOAL1,GOAL2    # Comma-separated goals
  --success-criteria C1,C2 # Success criteria
  --priority LEVEL       # Priority level
  --start-date DATE      # Start date (YYYY-MM-DD)
  --due-date DATE        # Due date (YYYY-MM-DD)
  --stakeholders NAME1,NAME2 # Stakeholders
  --format FORMAT        # Output format

Returns:
  JSON: {"id": "EPIC-001", "status": "active", ...}
```

#### List Epics
```bash
tickets epic list [options]

Options:
  --status STATUS        # Filter by status
  --priority LEVEL       # Filter by priority
  --format FORMAT        # Output format

Returns:
  JSON: [{"id": "EPIC-001", ...}, ...]
```

#### Add Ticket to Epic
```bash
tickets epic add-ticket <epic-id> <ticket-id>

Returns:
  JSON: {"epic_id": "EPIC-001", "ticket_id": "TICK-001", "added": true}
```

### Backlog Commands

#### Add to Backlog
```bash
tickets backlog add [options]

Options:
  --title TEXT           # Required: Item title
  --description TEXT     # Item description
  --priority-score INT   # Priority score (0-100)
  --business-value LEVEL # high|medium|low
  --effort-estimate LEVEL # high|medium|low
  --tags TAG1,TAG2       # Tags
  --format FORMAT        # Output format

Returns:
  JSON: {"id": "BACK-001", "priority_score": 85, ...}
```

#### List Backlog
```bash
tickets backlog list [options]

Options:
  --min-priority INT     # Minimum priority score
  --business-value LEVEL # Filter by business value
  --effort-estimate LEVEL # Filter by effort estimate
  --sort-by FIELD        # Sort field (priority_score, created_date)
  --format FORMAT        # Output format

Returns:
  JSON: [{"id": "BACK-001", "priority_score": 85, ...}, ...]
```

## 📊 JSON Schemas

### Ticket Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "title", "status", "created_date"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^TICK-\\d{3}$"
    },
    "title": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "description": {
      "type": "string"
    },
    "status": {
      "type": "string",
      "enum": ["created", "todo", "in-progress", "done", "closed"]
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"]
    },
    "created_date": {
      "type": "string",
      "format": "date"
    },
    "updated_date": {
      "type": "string",
      "format": "date"
    },
    "assignee": {
      "type": ["string", "null"]
    },
    "epic_id": {
      "type": ["string", "null"],
      "pattern": "^EPIC-\\d{3}$"
    },
    "parent_ticket_id": {
      "type": ["string", "null"],
      "pattern": "^TICK-\\d{3}$"
    },
    "child_ticket_ids": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^TICK-\\d{3}$"
      }
    },
    "requirements": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "estimated_hours": {
      "type": ["integer", "null"],
      "minimum": 0
    },
    "actual_hours": {
      "type": ["integer", "null"],
      "minimum": 0
    },
    "metadata": {
      "type": "object"
    }
  }
}
```

### Epic Schema
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "name", "status"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^EPIC-\\d{3}$"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "description": {
      "type": "string"
    },
    "goals": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "success_criteria": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "status": {
      "type": "string",
      "enum": ["active", "completed", "cancelled"]
    },
    "priority": {
      "type": "string",
      "enum": ["critical", "high", "medium", "low"]
    },
    "start_date": {
      "type": ["string", "null"],
      "format": "date"
    },
    "due_date": {
      "type": ["string", "null"],
      "format": "date"
    },
    "assigned_tickets": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^TICK-\\d{3}$"
      }
    },
    "stakeholders": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "metadata": {
      "type": "object"
    }
  }
}
```

## 🔄 Automation Patterns

### Batch Operations Pattern
```python
def batch_update_tickets(ticket_ids, updates):
    """Update multiple tickets atomically."""
    tickets = read_tickets()
    ticket_dict = {t['id']: t for t in tickets}
    
    for ticket_id in ticket_ids:
        if ticket_id in ticket_dict:
            ticket_dict[ticket_id].update(updates)
            ticket_dict[ticket_id]['updated_date'] = datetime.now().isoformat()
    
    write_tickets(list(ticket_dict.values()))
    return len([t for t in ticket_ids if t in ticket_dict])
```

### Query Pattern
```python
def query_tickets(filters):
    """Query tickets with complex filters."""
    tickets = read_tickets()
    results = tickets
    
    if 'status' in filters:
        results = [t for t in results if t['status'] == filters['status']]
    
    if 'priority' in filters:
        results = [t for t in results if t['priority'] == filters['priority']]
    
    if 'assignee' in filters:
        results = [t for t in results if t['assignee'] == filters['assignee']]
    
    if 'epic_id' in filters:
        results = [t for t in results if t['epic_id'] == filters['epic_id']]
    
    return results
```

### Workflow Automation Pattern
```python
def automate_epic_workflow(epic_name, feature_spec):
    """Automate epic creation and ticket generation."""
    # Create epic
    epic_id = create_epic(
        name=epic_name,
        description=f"Complete {epic_name} feature development"
    )
    
    # Create standard tickets
    ticket_templates = [
        ("API Development", "Implement backend API"),
        ("Frontend Implementation", "Build user interface"),
        ("Testing", "Write and run tests"), 
        ("Documentation", "Update documentation")
    ]
    
    ticket_ids = []
    for title, desc in ticket_templates:
        ticket_id = create_ticket(
            title=f"{epic_name} - {title}",
            description=desc,
            epic_id=epic_id,
            priority="medium"
        )
        ticket_ids.append(ticket_id)
    
    return epic_id, ticket_ids
```

## ⚠️ Error Handling

### CLI Error Codes
```
0   - Success
1   - General error
2   - Invalid command/arguments
3   - File system error
4   - Data validation error
5   - Resource not found
6   - Permission denied
7   - Network error (if applicable)
```

### Error Response Format (JSON)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid priority level 'urgent'",
    "details": {
      "field": "priority",
      "value": "urgent",
      "allowed_values": ["critical", "high", "medium", "low"]
    }
  }
}
```

### Python Error Handling Pattern
```python
import subprocess
import json

def safe_cli_call(command):
    """Safely execute CLI command and handle errors."""
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        if result.stdout.strip():
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout.strip()}
        
        return {"success": True}
        
    except subprocess.CalledProcessError as e:
        error_data = {"success": False, "exit_code": e.returncode}
        
        if e.stderr:
            try:
                error_data.update(json.loads(e.stderr))
            except json.JSONDecodeError:
                error_data["error"] = e.stderr.strip()
        
        return error_data
```

## 🚀 Performance Considerations

### File I/O Optimization
- Use atomic file operations for writes
- Implement file locking for concurrent access
- Cache frequently accessed data in memory
- Use streaming for large datasets

### CLI Command Optimization  
- Use `--format json` for programmatic access
- Filter at the CLI level rather than post-processing
- Use pagination for large result sets
- Batch operations when possible

### Memory Management
- Process large datasets in chunks
- Use generators for streaming data
- Clean up temporary files
- Monitor memory usage in long-running processes

### Concurrency Patterns
```python
import fcntl
import json

def locked_file_update(file_path, update_func):
    """Update file with exclusive lock."""
    with open(file_path, 'r+') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        
        try:
            data = json.load(f)
            updated_data = update_func(data)
            
            f.seek(0)
            f.truncate()
            json.dump(updated_data, f, indent=2)
            
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

---

This API reference provides the technical foundation for agents to build robust integrations with the repo-tickets system. For practical examples and workflows, see the `examples/` directory and the main Agent Guide.