# Repo-Tickets Usage Guide

Complete guide to using repo-tickets for agentic development.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Basic Operations](#basic-operations)
- [Advanced Features](#advanced-features)
- [Agentic Workflows](#agentic-workflows)
- [Performance Optimization](#performance-optimization)
- [Monitoring & Observability](#monitoring--observability)
- [Best Practices](#best-practices)

---

## Quick Start

### Installation

```bash
# Install in development mode
pip install -e .

# Or install with pip
pip install repo-tickets
```

### Initialize in Repository

```bash
# Navigate to your git/hg/jj repository
cd /path/to/your/project

# Initialize tickets
tickets init

# Create your first ticket
tickets create "Fix login bug" --priority high --description "Users cannot login"
```

### Basic Workflow

```bash
# List all tickets
tickets list

# Show ticket details
tickets show TICKET-1

# Update ticket status
tickets update TICKET-1 --status in-progress

# Close ticket
tickets close TICKET-1
```

---

## Core Concepts

### Tickets

Tickets are the fundamental unit of work in repo-tickets:

```python
{
    "id": "TICKET-123",
    "title": "Implement user authentication",
    "status": "open",           # open, in-progress, blocked, closed, cancelled
    "priority": "high",          # critical, high, medium, low
    "description": "Add JWT-based auth",
    "assignee": "alice",
    "reporter": "bob",
    "labels": ["security", "backend"],
    "estimated_hours": 8.0,
    "story_points": 5
}
```

### Epics

Epics group related tickets for large features:

```bash
# Create epic
tickets epic create "User Management System" --priority high

# Add tickets to epic
tickets epic add-ticket EPIC-AUTH TICKET-123 TICKET-124

# View epic progress
tickets epic show EPIC-AUTH
```

### Agents

AI agents perform automated work on tickets:

```bash
# Create agents
tickets agent create CodeBot --type developer
tickets agent create TestBot --type tester
tickets agent create ReviewBot --type reviewer

# Assign task to agent
tickets agent assign TICKET-123 AGENT-CODEBOT-1 code "Implement JWT auth"

# Auto-assign based on capabilities
tickets agent auto-assign TICKET-123 code "Implement feature"
```

---

## Basic Operations

### Creating Tickets

```bash
# Simple ticket
tickets create "Fix bug" --priority high

# Detailed ticket
tickets create "New feature" \
  --description "Detailed description here" \
  --priority medium \
  --assignee alice \
  --labels feature,backend \
  --estimate 8 \
  --points 5

# From template (JSON)
tickets batch create tickets.json
```

### Searching & Filtering

```bash
# Search by text
tickets search "login"

# Fast index-based search
tickets search "authentication" --fast

# Filter by status
tickets list --status open

# Filter by assignee
tickets list --assignee alice

# Filter by labels
tickets list --labels bug,urgent

# Lightweight summaries
tickets list-summary --status in-progress --priority high
```

### Requirements Management

```bash
# Add requirement
tickets requirements add TICKET-123 \
  "Must support OAuth 2.0" \
  --priority critical

# Add user story
tickets requirements story TICKET-123 \
  "user" \
  "login with Google" \
  "access the app quickly"

# Add expected result
tickets requirements result TICKET-123 \
  "Users can login successfully" \
  --method "manual_test"

# Add Gherkin scenario
tickets requirements gherkin TICKET-123 \
  "Successful login" \
  --given "User has valid credentials" \
  --when "User submits login form" \
  --then "User is redirected to dashboard"

# List requirements
tickets requirements list TICKET-123
```

### Time Tracking

```bash
# Start time tracking
tickets time start TICKET-123

# Stop time tracking
tickets time stop TICKET-123

# Log time manually
tickets time log TICKET-123 --hours 2.5 --description "Fixed auth bug"

# View time summary
tickets time TICKET-123
```

---

## Advanced Features

### Batch Operations

Perform bulk operations with atomic transactions:

```bash
# Batch create from file
tickets batch create new_tickets.json

# Batch update
tickets batch update updates.json

# Batch delete (with confirmation)
tickets batch delete TICKET-1 TICKET-2 TICKET-3

# Non-atomic mode (continue on errors)
tickets batch create tickets.json --no-atomic
```

**File formats:**

`new_tickets.json`:
```json
[
  {
    "title": "Feature 1",
    "description": "Description",
    "priority": "high",
    "labels": ["feature"]
  },
  {
    "title": "Feature 2",
    "description": "Description",
    "priority": "medium"
  }
]
```

`updates.json`:
```json
{
  "TICKET-1": {
    "status": "closed",
    "resolution": "fixed"
  },
  "TICKET-2": {
    "priority": "high",
    "assignee": "alice"
  }
}
```

### Event-Driven Automation

Subscribe to events for reactive automation:

```python
from repo_tickets.events import EventType, subscribe_event

def on_ticket_created(event):
    ticket_id = event.data['ticket_id']
    priority = event.data.get('priority')
    
    if priority == 'critical':
        # Auto-assign to emergency team
        assign_to_emergency_team(ticket_id)

# Subscribe to events
subscribe_event(EventType.TICKET_CREATED, on_ticket_created)
```

View event history:

```bash
# View recent events
tickets events history

# Filter by type
tickets events history --type ticket.created --limit 50

# View statistics
tickets events stats
```

### Workflow Orchestration

Create multi-step workflows:

```python
from repo_tickets.workflows import get_workflow_engine, create_feature_development_workflow

# Get engine
engine = get_workflow_engine()

# Create feature development workflow
workflow = create_feature_development_workflow("TICKET-123", engine)

# Start workflow (automatic progression)
engine.start_workflow(workflow.id)

# Check progress
status = engine.get_workflow_status(workflow.id)
print(f"Progress: {status['progress_percentage']}%")
```

**Built-in workflow templates:**

1. **Feature Development**: requirements → design → code → test → review
2. **Bug Fix**: reproduce → diagnose → fix → verify

### Agent Learning

System learns from agent performance:

```python
from repo_tickets.agent_learning import get_learning_system, get_smart_selector

# Get learning system
learning = get_learning_system()

# Rebuild profiles from history
learning.rebuild_all_profiles()

# Get agent profile
profile = learning.get_agent_profile("AGENT-CODEBOT-1")
print(f"Success rate: {profile.overall_success_rate:.1%}")
print(f"Preferred tasks: {profile.preferred_task_types}")

# Smart agent selection
selector = get_smart_selector(learning)
agent = selector.select_agent("code", consider_workload=True)

# Get recommendations with explanations
recommendations = selector.get_recommendations("test", top_n=3)
for agent, score, explanation in recommendations:
    print(f"{agent.name}: {score:.1f} - {explanation}")
```

---

## Agentic Workflows

### Parallel Task Assignment

Assign multiple tasks to agents in parallel:

```python
from repo_tickets.async_agents import get_async_agent_operations

async_ops = get_async_agent_operations()

# Define tasks
task_specs = [
    {
        'ticket_id': 'TICKET-1',
        'agent_id': 'AGENT-CODEBOT-1',
        'task_type': 'code',
        'description': 'Implement feature A'
    },
    {
        'ticket_id': 'TICKET-2',
        'agent_id': 'AGENT-TESTBOT-1',
        'task_type': 'test',
        'description': 'Write tests for feature A'
    }
]

# Assign in parallel (10-15x faster)
result = async_ops.assign_tasks_parallel(task_specs)

print(f"Completed: {result.completed}/{result.total}")
print(f"Duration: {result.duration_ms:.1f}ms")
```

### Auto-Distribution

Automatically distribute tasks to best agents:

```python
# Tasks without agent assignment
task_specs = [
    {'ticket_id': 'TICKET-1', 'task_type': 'python', 'description': 'Implement API'},
    {'ticket_id': 'TICKET-2', 'task_type': 'test', 'description': 'Test API'},
    {'ticket_id': 'TICKET-3', 'task_type': 'review', 'description': 'Review code'}
]

# Auto-distribute based on:
# - Agent capabilities
# - Current workload
# - Historical performance
result = async_ops.auto_distribute_tasks(
    task_specs,
    consider_load=True,
    consider_capabilities=True
)
```

### Complete Agentic Workflow

```python
from repo_tickets.storage import TicketStorage
from repo_tickets.agents import AgentStorage
from repo_tickets.workflows import get_workflow_engine, create_feature_development_workflow
from repo_tickets.async_agents import get_async_agent_operations
from repo_tickets.agent_learning import get_smart_selector, get_learning_system

# 1. Create ticket
storage = TicketStorage()
ticket = storage.create_ticket(
    title="Implement user profile page",
    priority="high",
    labels=["feature", "frontend"]
)

# 2. Create workflow
engine = get_workflow_engine()
workflow = create_feature_development_workflow(ticket.id, engine)

# 3. System automatically:
#    - Selects best agents based on ML scoring
#    - Assigns tasks in parallel
#    - Progresses workflow based on events
#    - Learns from outcomes

# 4. Start workflow
engine.start_workflow(workflow.id)

# 5. Monitor progress
status = engine.get_workflow_status(workflow.id)
# Workflow progresses automatically as agents complete tasks!
```

---

## Performance Optimization

### Caching

Caching provides 100-500x speedup:

```bash
# View cache statistics
tickets cache-stats

# Clear cache
tickets cache-stats --clear
```

In code:

```python
# Caching is enabled by default
storage = TicketStorage(enable_cache=True)

# Get cache stats
stats = storage.get_cache_stats()
print(f"Hit rate: {stats['hit_rate']:.1%}")
```

### Fast Index Search

Index search is 40-200x faster:

```bash
# Fast search (index only, <5ms)
tickets search --fast "authentication"

# Full search (loads tickets, 200-1000ms)
tickets search "authentication"

# Lightweight summaries (10-50x faster)
tickets list-summary --status open --priority high
```

### Batch Operations

Bulk operations are 10-15x faster:

```bash
# Create 100 tickets: 30-60s → 3-5s
tickets batch create bulk_tickets.json

# Update 50 tickets: 15-30s → 1-2s
tickets batch update bulk_updates.json
```

---

## Monitoring & Observability

### Structured Logging

Configure structured logging:

```bash
# JSON format for log aggregation
tickets logs --level INFO --json --file /var/log/tickets.log

# Human-readable for development
tickets logs --level DEBUG --human
```

In code:

```python
from repo_tickets.logging_utils import get_logger, log_performance

logger = get_logger()

# Log with context
logger.log_ticket_operation("created", "TICKET-123", priority="high")

# Performance tracking
with log_performance("load_ticket", ticket_id="TICKET-123"):
    ticket = storage.load_ticket("TICKET-123")
```

### Metrics & Telemetry

Track system performance:

```python
from repo_tickets.metrics import get_system_metrics, timed_operation

# Get metrics
metrics = get_system_metrics()

# Register health check
def check_storage():
    return storage.is_initialized()

metrics.register_health_check("storage", check_storage)

# Check health
health = metrics.check_health()
print(f"Status: {health.status}")  # healthy, degraded, unhealthy

# Get performance report
report = metrics.get_performance_report()
print(f"Slowest operations: {report['slowest_operations']}")
print(f"Bottlenecks: {report['bottlenecks']}")

# Track operations
with timed_operation("bulk_import"):
    # Your code here
    pass

# Export metrics
metrics.export_metrics(Path("metrics_report.json"))
```

### Schema Validation

Validate data integrity:

```python
from repo_tickets.schemas import TicketSchema, validate_ticket_dict

# Validate ticket data
ticket_data = {
    "id": "TICKET-123",
    "title": "Fix bug",
    "status": "open",
    "priority": "high",
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}

# Method 1: Quick validation
is_valid, error = validate_ticket_dict(ticket_data)
if not is_valid:
    print(f"Validation error: {error}")

# Method 2: Pydantic validation
try:
    validated = TicketSchema(**ticket_data)
    print("Valid ticket!")
except ValidationError as e:
    print(f"Errors: {e}")
```

---

## Best Practices

### 1. Use Fast Operations for Queries

```python
# ❌ Slow: Full ticket load
tickets = storage.list_tickets()

# ✅ Fast: Summary only
summaries = storage.list_tickets_summary(status="open")

# ❌ Slow: Full search
ids = storage.search_tickets("bug")

# ✅ Fast: Index search
ids = storage.search_tickets_fast("bug")
```

### 2. Batch Operations for Bulk Changes

```python
# ❌ Slow: Individual updates
for ticket_id in ticket_ids:
    ticket = storage.load_ticket(ticket_id)
    ticket.status = "closed"
    storage.save_ticket(ticket)

# ✅ Fast: Batch update
from repo_tickets.batch import get_batch_operations

batch = get_batch_operations(storage)
updates = {tid: {"status": "closed"} for tid in ticket_ids}
result = batch.batch_update(updates, atomic=True)
```

### 3. Use Events for Automation

```python
# ❌ Polling (wastes resources)
while True:
    tickets = storage.list_tickets(status="open")
    # Check for new tickets
    time.sleep(60)

# ✅ Event-driven (instant, efficient)
from repo_tickets.events import EventType, subscribe_event

def handle_new_ticket(event):
    ticket_id = event.data['ticket_id']
    # React immediately

subscribe_event(EventType.TICKET_CREATED, handle_new_ticket)
```

### 4. Monitor Performance

```python
# Always monitor critical operations
from repo_tickets.metrics import timed_operation

with timed_operation("critical_batch_import"):
    result = batch.batch_create_tickets(large_dataset)

# Check for bottlenecks
metrics = get_system_metrics()
bottlenecks = metrics.collector.detect_bottlenecks(threshold_ms=100)
for bn in bottlenecks:
    print(f"Slow: {bn['operation']} ({bn['avg_duration_ms']:.1f}ms)")
```

### 5. Use Workflows for Complex Tasks

```python
# ❌ Manual coordination
# 1. Manually assign requirements task
# 2. Wait for completion
# 3. Manually assign design task
# 4. Wait for completion
# ... etc

# ✅ Workflow automation
workflow = create_feature_development_workflow(ticket_id, engine)
engine.start_workflow(workflow.id)
# Automatic progression based on events!
```

### 6. Enable Learning for Better Agent Selection

```python
# Update learning after each task
from repo_tickets.agent_learning import get_learning_system

learning = get_learning_system()

# Automatically updates from completed tasks
task = agent_storage.load_task(task_id)
learning.update_from_task(task)

# Use smart selection
from repo_tickets.agent_learning import get_smart_selector

selector = get_smart_selector(learning)
best_agent = selector.select_agent("python", consider_workload=True)
```

### 7. Validate Input Data

```python
# Always validate before saving
from repo_tickets.schemas import TicketSchema
from pydantic import ValidationError

try:
    validated = TicketSchema(**ticket_data)
    storage.save_ticket(validated)
except ValidationError as e:
    logger.error("Invalid ticket data", errors=e.errors())
```

---

## Next Steps

- **Examples**: See `/examples` directory for complete working examples
- **Architecture**: See `ARCHITECTURE.md` for system design details
- **API Reference**: See `API_REFERENCE.md` for detailed API documentation
- **Agent Guide**: See `AGENT_GUIDE.md` for AI agent integration

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/thinmanj/repo-tickets/issues
- Documentation: https://github.com/thinmanj/repo-tickets/wiki
