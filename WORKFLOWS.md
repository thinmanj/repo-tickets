# Repo-Tickets Workflow Patterns

Complete guide to workflow patterns and real-world examples for agentic development.

## Table of Contents

- [Workflow Overview](#workflow-overview)
- [Feature Development Workflow](#feature-development-workflow)
- [Bug Fix Workflow](#bug-fix-workflow)
- [Multi-Agent Coordination](#multi-agent-coordination)
- [Event-Driven Automation](#event-driven-automation)
- [Custom Workflow Patterns](#custom-workflow-patterns)
- [Real-World Examples](#real-world-examples)

---

## Workflow Overview

Repo-tickets provides powerful workflow orchestration for complex development tasks. Workflows are:

- **Event-driven**: Progress automatically on task completion
- **Dependency-aware**: Steps wait for prerequisites
- **State-managed**: Track progress through state machine
- **Agent-integrated**: Automatically assign tasks to agents
- **Observable**: Full logging and metrics

### Workflow Lifecycle

```
Create → Start → Execute Steps → Complete
                      ↓
                  [Blocked/Failed]
                      ↓
                  Resume/Retry → Execute Steps
```

---

## Feature Development Workflow

### Standard Feature Development

**Steps**: Requirements → Design → Implementation → Testing → Code Review

#### 1. Setup

```bash
# Create ticket for new feature
tickets create "User authentication system" \
  --priority high \
  --labels feature,security \
  --estimate 40 \
  --points 13

# Create agents for each role
tickets agent create RequirementsAnalyst --type analyst --skills requirements,documentation
tickets agent create SystemArchitect --type architect --skills design,architecture
tickets agent create PythonDeveloper --type developer --skills python,backend
tickets agent create QAEngineer --type tester --skills testing,qa
tickets agent create SeniorReviewer --type reviewer --skills code-review,security
```

#### 2. Create and Start Workflow

```python
from repo_tickets.workflows import get_workflow_engine, create_feature_development_workflow
from repo_tickets.storage import TicketStorage

# Get ticket
storage = TicketStorage()
ticket = storage.get_ticket_by_title("User authentication system")

# Create workflow
engine = get_workflow_engine()
workflow = create_feature_development_workflow(ticket.id, engine)

# Start workflow (begins execution)
engine.start_workflow(workflow.id)
```

#### 3. Monitor Progress

```python
# Check workflow status
status = engine.get_workflow_status(workflow.id)

print(f"State: {status['state']}")
print(f"Progress: {status['progress_percentage']}%")
print(f"Current step: {status['current_step']}")
print(f"Completed: {status['completed_steps']} / {status['total_steps']}")

# Get detailed step information
for step in status['steps']:
    print(f"  {step['name']}: {step['status']}")
    if step['agent_id']:
        print(f"    Agent: {step['agent_id']}")
    if step['started_at']:
        print(f"    Started: {step['started_at']}")
```

#### 4. Automatic Progression

Workflow progresses automatically as agents complete tasks:

```
Step 1: Requirements Gathering
  ↓ (analyst completes requirements)
  ↓ Event: AGENT_TASK_COMPLETED
  ↓ Workflow engine receives event
  ↓ Engine marks step 1 complete
  ↓
Step 2: Design Planning
  ↓ (architect completes design)
  ↓ Event: AGENT_TASK_COMPLETED
  ↓
Step 3: Implementation
  ↓ (developer completes code)
  ↓
Step 4: Testing
  ↓ (tester completes tests)
  ↓
Step 5: Code Review
  ↓ (reviewer approves)
  ↓
Workflow Complete!
  Event: WORKFLOW_COMPLETED
```

### Complete Python Example

```python
#!/usr/bin/env python3
"""
Feature development workflow example.
"""

from repo_tickets.storage import TicketStorage
from repo_tickets.agents import AgentStorage
from repo_tickets.workflows import get_workflow_engine, create_feature_development_workflow
from repo_tickets.events import EventType, subscribe_event, get_event_bus
import time

def workflow_progress_handler(event):
    """Monitor workflow progress."""
    workflow_id = event.data.get('workflow_id')
    step_name = event.data.get('step_name')
    print(f"✓ Workflow {workflow_id}: Step '{step_name}' completed")

def workflow_completed_handler(event):
    """Handle workflow completion."""
    workflow_id = event.data.get('workflow_id')
    print(f"🎉 Workflow {workflow_id} completed successfully!")

# Subscribe to workflow events
subscribe_event(EventType.WORKFLOW_STEP_COMPLETED, workflow_progress_handler)
subscribe_event(EventType.WORKFLOW_COMPLETED, workflow_completed_handler)

# Initialize
storage = TicketStorage()
agent_storage = AgentStorage()
engine = get_workflow_engine()

# Create feature ticket
ticket = storage.create_ticket(
    title="OAuth 2.0 Integration",
    description="Integrate OAuth 2.0 for social login",
    priority="high",
    labels=["feature", "authentication"],
    estimated_hours=32,
    story_points=13
)

print(f"Created ticket: {ticket.id}")

# Add requirements
ticket.add_requirement(
    "Must support Google and GitHub OAuth",
    priority="critical"
)
ticket.add_user_story(
    actor="user",
    action="login with Google account",
    benefit="quick access without registration"
)
storage.save_ticket(ticket)

# Create specialized agents
analyst = agent_storage.create_agent(
    name="RequirementsBot",
    agent_type="analyst",
    capabilities=["requirements", "user-stories", "documentation"]
)

architect = agent_storage.create_agent(
    name="ArchitectBot",
    agent_type="architect",
    capabilities=["system-design", "architecture", "security"]
)

developer = agent_storage.create_agent(
    name="BackendBot",
    agent_type="developer",
    capabilities=["python", "oauth", "security", "apis"]
)

tester = agent_storage.create_agent(
    name="QABot",
    agent_type="tester",
    capabilities=["testing", "integration-tests", "security-testing"]
)

reviewer = agent_storage.create_agent(
    name="ReviewBot",
    agent_type="reviewer",
    capabilities=["code-review", "security-review", "best-practices"]
)

print(f"Created {len([analyst, architect, developer, tester, reviewer])} agents")

# Create workflow
workflow = create_feature_development_workflow(ticket.id, engine)
print(f"Created workflow: {workflow.id}")

# Customize workflow with specific agents
workflow.steps[0].agent_id = analyst.id   # Requirements
workflow.steps[1].agent_id = architect.id  # Design
workflow.steps[2].agent_id = developer.id  # Implementation
workflow.steps[3].agent_id = tester.id     # Testing
workflow.steps[4].agent_id = reviewer.id   # Review

# Start workflow
print("\nStarting workflow...")
engine.start_workflow(workflow.id)

# Simulate agents completing tasks
print("\nSimulating task completion...")
for i, step in enumerate(workflow.steps):
    # Get agent for this step
    agent_id = step.agent_id
    agent = agent_storage.load_agent(agent_id)
    
    print(f"\nStep {i+1}: {step.name}")
    print(f"  Agent: {agent.name}")
    
    # Simulate agent working
    time.sleep(0.5)  # Simulate work
    
    # Complete task (this triggers workflow progression)
    task = agent_storage.create_task(
        agent_id=agent_id,
        ticket_id=ticket.id,
        task_type=step.name.lower().replace(' ', '_'),
        description=f"Complete {step.name}"
    )
    
    # Mark task as completed
    task.status = "completed"
    task.result = f"Successfully completed {step.name}"
    agent_storage.save_task(task)
    
    # Wait for workflow to process
    time.sleep(0.2)

# Check final status
final_status = engine.get_workflow_status(workflow.id)
print(f"\n{'='*50}")
print(f"Final workflow state: {final_status['state']}")
print(f"Progress: {final_status['progress_percentage']}%")
print(f"Completed in: {final_status.get('duration', 'N/A')}")
```

---

## Bug Fix Workflow

### Standard Bug Fix Process

**Steps**: Reproduce → Diagnose → Fix → Verify

#### 1. Create Bug Ticket

```bash
# Create bug ticket
tickets create "Login fails with invalid credentials message" \
  --priority critical \
  --labels bug,login,security \
  --description "Users see 'Invalid credentials' even with correct password"

# Add reproduction steps
tickets requirements gherkin TICKET-123 "Failed login scenario" \
  --given "User has valid credentials" \
  --when "User enters correct username and password" \
  --then "User should login successfully" \
  --and "Instead sees 'Invalid credentials' error"
```

#### 2. Create Bug Fix Workflow

```python
from repo_tickets.workflows import get_workflow_engine, create_bug_fix_workflow

engine = get_workflow_engine()
workflow = create_bug_fix_workflow("TICKET-123", engine)

# Assign agents to steps
workflow.steps[0].agent_id = "AGENT-TESTER-1"    # Reproduce
workflow.steps[1].agent_id = "AGENT-DEBUGGER-1"  # Diagnose
workflow.steps[2].agent_id = "AGENT-DEVELOPER-1" # Fix
workflow.steps[3].agent_id = "AGENT-QA-1"        # Verify

# Start workflow
engine.start_workflow(workflow.id)
```

#### 3. Track Bug Resolution

```python
# Monitor each stage
status = engine.get_workflow_status(workflow.id)

for step in status['steps']:
    if step['status'] == 'completed':
        print(f"✓ {step['name']}")
        if step.get('notes'):
            print(f"  Notes: {step['notes']}")
    elif step['status'] == 'in_progress':
        print(f"⏳ {step['name']} (in progress)")
    else:
        print(f"○ {step['name']} (pending)")
```

### Complete Bug Fix Example

```python
#!/usr/bin/env python3
"""
Bug fix workflow with root cause analysis.
"""

from repo_tickets.storage import TicketStorage
from repo_tickets.agents import AgentStorage
from repo_tickets.workflows import get_workflow_engine, create_bug_fix_workflow
from repo_tickets.events import EventType, subscribe_event

def on_bug_diagnosed(event):
    """Capture root cause when diagnosis completes."""
    if event.data.get('step_name') == 'Diagnose Root Cause':
        root_cause = event.data.get('notes', '')
        print(f"🔍 Root cause identified: {root_cause}")

subscribe_event(EventType.WORKFLOW_STEP_COMPLETED, on_bug_diagnosed)

# Create bug ticket
storage = TicketStorage()
ticket = storage.create_ticket(
    title="Authentication token expires prematurely",
    description="User sessions end after 5 minutes instead of 30 minutes",
    priority="critical",
    labels=["bug", "security", "authentication"]
)

# Add context
ticket.add_requirement(
    "Sessions must remain valid for 30 minutes",
    priority="critical"
)

ticket.add_gherkin_scenario(
    name="Session timeout",
    given_step="User is logged in",
    when_step="User is idle for 25 minutes",
    then_step="User session should still be active"
)

storage.save_ticket(ticket)

# Create workflow
engine = get_workflow_engine()
workflow = create_bug_fix_workflow(ticket.id, engine)

# Start execution
engine.start_workflow(workflow.id)

# Workflow progresses through:
# 1. Reproduce issue → Confirms bug exists
# 2. Diagnose → Identifies token TTL misconfiguration
# 3. Fix → Updates configuration from 300s to 1800s
# 4. Verify → Confirms 30-minute session timeout works

# Check result
final_status = engine.get_workflow_status(workflow.id)
if final_status['state'] == 'completed':
    print(f"✅ Bug {ticket.id} fixed and verified!")
    
    # Close ticket
    ticket = storage.load_ticket(ticket.id)
    ticket.status = "closed"
    ticket.resolution = "fixed"
    storage.save_ticket(ticket)
```

---

## Multi-Agent Coordination

### Parallel Task Execution

Execute independent tasks simultaneously for faster completion.

#### Pattern 1: Frontend + Backend Development

```python
from repo_tickets.async_agents import get_async_agent_operations

async_ops = get_async_agent_operations()

# Define parallel tasks
tasks = [
    {
        'ticket_id': 'TICKET-100',
        'agent_id': 'AGENT-FRONTEND-1',
        'task_type': 'frontend',
        'description': 'Build login UI components'
    },
    {
        'ticket_id': 'TICKET-100',
        'agent_id': 'AGENT-BACKEND-1',
        'task_type': 'backend',
        'description': 'Implement authentication API'
    },
    {
        'ticket_id': 'TICKET-100',
        'agent_id': 'AGENT-DB-1',
        'task_type': 'database',
        'description': 'Design user schema'
    }
]

# Execute in parallel (10-15x faster)
result = async_ops.assign_tasks_parallel(tasks)

print(f"Completed {result.completed}/{result.total} tasks")
print(f"Duration: {result.duration_ms:.1f}ms")
print(f"Average per task: {result.avg_task_duration_ms:.1f}ms")
```

#### Pattern 2: Auto-Distribution

Let the system assign tasks to best available agents:

```python
from repo_tickets.async_agents import get_async_agent_operations
from repo_tickets.agent_learning import get_smart_selector

async_ops = get_async_agent_operations()

# Tasks without agent assignment
tasks = [
    {'ticket_id': 'TICKET-200', 'task_type': 'python', 'description': 'Refactor auth module'},
    {'ticket_id': 'TICKET-201', 'task_type': 'test', 'description': 'Write unit tests'},
    {'ticket_id': 'TICKET-202', 'task_type': 'review', 'description': 'Code review'},
    {'ticket_id': 'TICKET-203', 'task_type': 'documentation', 'description': 'Update API docs'},
]

# System selects best agents based on:
# - Historical performance
# - Current workload
# - Expertise in task type
result = async_ops.auto_distribute_tasks(
    tasks,
    consider_load=True,
    consider_capabilities=True
)

print(f"Auto-distributed {result.completed} tasks")
for i, task_id in enumerate(result.task_ids):
    print(f"  Task {i+1} → {result.assigned_agents[i]}")
```

### Sequential Dependencies

Chain tasks with dependencies:

```python
from repo_tickets.workflows import get_workflow_engine, Workflow, WorkflowStep

engine = get_workflow_engine()

# Create custom workflow with dependencies
workflow = Workflow(
    id="WF-DATABASE-MIGRATION",
    name="Database Migration",
    ticket_id="TICKET-300",
    description="Migrate database to new schema"
)

# Step 1: Backup database (no dependencies)
backup_step = WorkflowStep(
    name="Backup Database",
    agent_id="AGENT-DBA-1",
    task_type="backup",
    description="Create full database backup",
    dependencies=[]  # Can start immediately
)

# Step 2: Run migration (depends on backup)
migrate_step = WorkflowStep(
    name="Run Migration",
    agent_id="AGENT-DBA-1",
    task_type="migration",
    description="Execute schema migration scripts",
    dependencies=[backup_step.id]  # Waits for backup
)

# Step 3: Verify data (depends on migration)
verify_step = WorkflowStep(
    name="Verify Data Integrity",
    agent_id="AGENT-QA-1",
    task_type="verification",
    description="Verify all data migrated correctly",
    dependencies=[migrate_step.id]  # Waits for migration
)

# Step 4: Update application (depends on migration)
deploy_step = WorkflowStep(
    name="Deploy New Version",
    agent_id="AGENT-DEVOPS-1",
    task_type="deployment",
    description="Deploy application with new schema",
    dependencies=[migrate_step.id]  # Waits for migration
)

workflow.steps = [backup_step, migrate_step, verify_step, deploy_step]

# Register and start
engine.register_workflow(workflow)
engine.start_workflow(workflow.id)

# Execution order:
# 1. Backup Database (starts immediately)
# 2. Run Migration (after backup completes)
# 3. Verify Data & Deploy (both after migration, can run in parallel)
```

---

## Event-Driven Automation

### Reactive Automation Patterns

#### Pattern 1: Auto-Assignment on Priority

```python
from repo_tickets.events import EventType, subscribe_event
from repo_tickets.storage import TicketStorage
from repo_tickets.agents import AgentStorage

storage = TicketStorage()
agent_storage = AgentStorage()

def auto_assign_critical_tickets(event):
    """Automatically assign critical tickets to senior engineer."""
    ticket_id = event.data['ticket_id']
    priority = event.data.get('priority')
    
    if priority == 'critical':
        # Find senior engineer agent
        agents = agent_storage.list_agents()
        senior = next(
            (a for a in agents if 'senior' in a.name.lower()),
            None
        )
        
        if senior:
            # Assign immediately
            ticket = storage.load_ticket(ticket_id)
            ticket.assignee = senior.name
            storage.save_ticket(ticket)
            
            # Create urgent task
            agent_storage.create_task(
                agent_id=senior.id,
                ticket_id=ticket_id,
                task_type="critical_response",
                description=f"Urgent: {ticket.title}"
            )
            
            print(f"🚨 Critical ticket {ticket_id} auto-assigned to {senior.name}")

subscribe_event(EventType.TICKET_CREATED, auto_assign_critical_tickets)
```

#### Pattern 2: Automatic Testing on Code Completion

```python
from repo_tickets.events import EventType, subscribe_event
from repo_tickets.agents import AgentStorage

agent_storage = AgentStorage()

def trigger_testing_on_code_complete(event):
    """Automatically start testing when code is completed."""
    task_id = event.data.get('task_id')
    task_type = event.data.get('task_type')
    
    if task_type == 'code' or task_type == 'implementation':
        task = agent_storage.load_task(task_id)
        ticket_id = task.ticket_id
        
        # Find test agent
        agents = agent_storage.list_agents()
        tester = next(
            (a for a in agents if a.agent_type == 'tester'),
            None
        )
        
        if tester:
            # Create test task automatically
            test_task = agent_storage.create_task(
                agent_id=tester.id,
                ticket_id=ticket_id,
                task_type="test",
                description=f"Test changes from task {task_id}"
            )
            
            print(f"🧪 Auto-created test task {test_task.id}")

subscribe_event(EventType.AGENT_TASK_COMPLETED, trigger_testing_on_code_complete)
```

#### Pattern 3: Notification on Workflow Completion

```python
from repo_tickets.events import EventType, subscribe_event
from repo_tickets.storage import TicketStorage
import subprocess

storage = TicketStorage()

def notify_on_workflow_complete(event):
    """Send notification when workflow completes."""
    workflow_id = event.data['workflow_id']
    ticket_id = event.data.get('ticket_id')
    
    ticket = storage.load_ticket(ticket_id)
    
    # Send notification (example: Slack)
    message = f"✅ Workflow {workflow_id} completed for ticket {ticket_id}: {ticket.title}"
    
    # Example: Post to Slack
    subprocess.run([
        "curl", "-X", "POST",
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        "-H", "Content-Type: application/json",
        "-d", f'{{"text": "{message}"}}'
    ])
    
    print(f"📢 Notification sent: {message}")

subscribe_event(EventType.WORKFLOW_COMPLETED, notify_on_workflow_complete)
```

---

## Custom Workflow Patterns

### Pattern 1: Hotfix Workflow

Emergency fixes with abbreviated process:

```python
from repo_tickets.workflows import Workflow, WorkflowStep, get_workflow_engine

def create_hotfix_workflow(ticket_id):
    """Create abbreviated workflow for emergency fixes."""
    workflow = Workflow(
        id=f"WF-HOTFIX-{ticket_id}",
        name="Emergency Hotfix",
        ticket_id=ticket_id,
        description="Fast-track fix for production issue"
    )
    
    # Only essential steps
    steps = [
        WorkflowStep(
            name="Emergency Fix",
            task_type="hotfix",
            description="Implement immediate fix",
            dependencies=[]
        ),
        WorkflowStep(
            name="Quick Verify",
            task_type="verify",
            description="Verify fix resolves issue",
            dependencies=["Emergency Fix"]
        ),
        WorkflowStep(
            name="Deploy",
            task_type="deploy",
            description="Deploy to production",
            dependencies=["Quick Verify"]
        )
    ]
    
    workflow.steps = steps
    return workflow

# Usage
engine = get_workflow_engine()
workflow = create_hotfix_workflow("TICKET-CRITICAL-1")
engine.register_workflow(workflow)
engine.start_workflow(workflow.id)
```

### Pattern 2: Research Spike Workflow

Exploratory work with flexible outcomes:

```python
def create_research_spike_workflow(ticket_id, time_box_hours=8):
    """Create time-boxed research workflow."""
    workflow = Workflow(
        id=f"WF-SPIKE-{ticket_id}",
        name="Research Spike",
        ticket_id=ticket_id,
        description=f"Time-boxed research ({time_box_hours}h)"
    )
    
    steps = [
        WorkflowStep(
            name="Research Options",
            task_type="research",
            description=f"Explore solutions (max {time_box_hours}h)",
            dependencies=[]
        ),
        WorkflowStep(
            name="Document Findings",
            task_type="documentation",
            description="Summarize research results",
            dependencies=["Research Options"]
        ),
        WorkflowStep(
            name="Recommend Approach",
            task_type="recommendation",
            description="Propose solution based on findings",
            dependencies=["Document Findings"]
        )
    ]
    
    workflow.steps = steps
    return workflow
```

### Pattern 3: Incremental Delivery Workflow

Break large features into phases:

```python
def create_incremental_delivery_workflow(ticket_id, phases):
    """Create workflow for phased delivery."""
    workflow = Workflow(
        id=f"WF-INCREMENTAL-{ticket_id}",
        name="Incremental Delivery",
        ticket_id=ticket_id,
        description="Phased feature delivery"
    )
    
    steps = []
    for i, phase in enumerate(phases):
        # Each phase has: code → test → deploy
        phase_prefix = f"Phase {i+1}: {phase['name']}"
        
        code_step = WorkflowStep(
            name=f"{phase_prefix} - Code",
            task_type="code",
            description=phase['description'],
            dependencies=[]
        )
        
        test_step = WorkflowStep(
            name=f"{phase_prefix} - Test",
            task_type="test",
            description=f"Test {phase['name']}",
            dependencies=[code_step.id]
        )
        
        deploy_step = WorkflowStep(
            name=f"{phase_prefix} - Deploy",
            task_type="deploy",
            description=f"Deploy {phase['name']} to production",
            dependencies=[test_step.id]
        )
        
        steps.extend([code_step, test_step, deploy_step])
    
    workflow.steps = steps
    return workflow

# Usage
phases = [
    {"name": "Basic Auth", "description": "Username/password login"},
    {"name": "Social Login", "description": "OAuth integration"},
    {"name": "2FA", "description": "Two-factor authentication"}
]

workflow = create_incremental_delivery_workflow("TICKET-BIG-FEATURE", phases)
```

---

## Real-World Examples

### Example 1: Complete E-commerce Feature

Build a shopping cart feature from start to finish:

```python
#!/usr/bin/env python3
"""
Complete example: Shopping cart feature development.
"""

from repo_tickets.storage import TicketStorage
from repo_tickets.agents import AgentStorage
from repo_tickets.workflows import get_workflow_engine, create_feature_development_workflow
from repo_tickets.async_agents import get_async_agent_operations

# Initialize
storage = TicketStorage()
agent_storage = AgentStorage()
engine = get_workflow_engine()
async_ops = get_async_agent_operations()

# 1. Create main feature ticket
cart_ticket = storage.create_ticket(
    title="Shopping Cart System",
    description="Implement complete shopping cart functionality",
    priority="high",
    labels=["feature", "ecommerce", "cart"],
    estimated_hours=80,
    story_points=21
)

# 2. Add requirements
requirements = [
    "Users can add items to cart",
    "Users can update quantities",
    "Users can remove items",
    "Cart persists across sessions",
    "Cart shows total price with tax"
]

for req in requirements:
    cart_ticket.add_requirement(req, priority="high")

# 3. Add user stories
cart_ticket.add_user_story(
    "shopper",
    "add items to my cart",
    "I can purchase multiple items at once"
)

cart_ticket.add_user_story(
    "shopper",
    "see cart total before checkout",
    "I know exactly what I'll pay"
)

storage.save_ticket(cart_ticket)

# 4. Create subtasks for parallel work
subtasks = [
    {
        'title': 'Cart Backend API',
        'description': 'REST API for cart operations',
        'labels': ['backend', 'api'],
        'estimate': 24
    },
    {
        'title': 'Cart Frontend UI',
        'description': 'Shopping cart user interface',
        'labels': ['frontend', 'ui'],
        'estimate': 20
    },
    {
        'title': 'Cart Database Schema',
        'description': 'Database design for cart storage',
        'labels': ['database', 'schema'],
        'estimate': 8
    },
    {
        'title': 'Cart Integration Tests',
        'description': 'End-to-end cart tests',
        'labels': ['testing', 'integration'],
        'estimate': 16
    }
]

subtask_tickets = []
for subtask in subtasks:
    ticket = storage.create_ticket(**subtask)
    subtask_tickets.append(ticket)
    print(f"Created subtask: {ticket.id}")

# 5. Assign subtasks to specialized agents in parallel
backend_agent = agent_storage.get_agent_by_name("BackendBot")
frontend_agent = agent_storage.get_agent_by_name("FrontendBot")
db_agent = agent_storage.get_agent_by_name("DatabaseBot")
test_agent = agent_storage.get_agent_by_name("TestBot")

parallel_tasks = [
    {
        'ticket_id': subtask_tickets[0].id,
        'agent_id': backend_agent.id,
        'task_type': 'backend',
        'description': 'Implement cart API endpoints'
    },
    {
        'ticket_id': subtask_tickets[1].id,
        'agent_id': frontend_agent.id,
        'task_type': 'frontend',
        'description': 'Build cart UI components'
    },
    {
        'ticket_id': subtask_tickets[2].id,
        'agent_id': db_agent.id,
        'task_type': 'database',
        'description': 'Create cart tables and indexes'
    }
]

# Execute first 3 in parallel
print("\nStarting parallel development...")
result = async_ops.assign_tasks_parallel(parallel_tasks)
print(f"Completed {result.completed}/{result.total} parallel tasks")

# 6. After parallel tasks, start integration testing
integration_task = agent_storage.create_task(
    agent_id=test_agent.id,
    ticket_id=subtask_tickets[3].id,
    task_type='integration_test',
    description='Test complete cart workflow'
)

print(f"\nStarted integration testing: {integration_task.id}")

# 7. Create main workflow for coordination
main_workflow = create_feature_development_workflow(cart_ticket.id, engine)
engine.start_workflow(main_workflow.id)

print(f"\nMain workflow started: {main_workflow.id}")
print(f"Track progress: tickets workflow show {main_workflow.id}")
```

### Example 2: Security Vulnerability Response

Coordinated response to security issue:

```python
#!/usr/bin/env python3
"""
Security vulnerability response workflow.
"""

from repo_tickets.storage import TicketStorage
from repo_tickets.agents import AgentStorage
from repo_tickets.workflows import Workflow, WorkflowStep, get_workflow_engine
from repo_tickets.events import EventType, subscribe_event

# Setup
storage = TicketStorage()
agent_storage = AgentStorage()
engine = get_workflow_engine()

# Create security ticket
vuln_ticket = storage.create_ticket(
    title="SQL Injection vulnerability in login endpoint",
    description="Reported by security researcher: user input not sanitized",
    priority="critical",
    labels=["security", "vulnerability", "sql-injection"],
    estimated_hours=4
)

# Add detailed requirement
vuln_ticket.add_requirement(
    "All user inputs must be parameterized to prevent SQL injection",
    priority="critical"
)

storage.save_ticket(vuln_ticket)

# Create emergency response workflow
workflow = Workflow(
    id=f"WF-SECURITY-{vuln_ticket.id}",
    name="Security Response",
    ticket_id=vuln_ticket.id,
    description="Emergency security fix workflow"
)

# Define steps
security_analyst = agent_storage.get_agent_by_capability("security-analysis")
senior_dev = agent_storage.get_agent_by_capability("security-fixes")
security_tester = agent_storage.get_agent_by_capability("security-testing")
devops = agent_storage.get_agent_by_capability("deployment")

steps = [
    WorkflowStep(
        name="Assess Impact",
        agent_id=security_analyst.id,
        task_type="security_assessment",
        description="Determine scope and severity",
        dependencies=[]
    ),
    WorkflowStep(
        name="Implement Fix",
        agent_id=senior_dev.id,
        task_type="security_fix",
        description="Apply parameterized queries",
        dependencies=["Assess Impact"]
    ),
    WorkflowStep(
        name="Security Test",
        agent_id=security_tester.id,
        task_type="security_test",
        description="Verify vulnerability is fixed",
        dependencies=["Implement Fix"]
    ),
    WorkflowStep(
        name="Emergency Deploy",
        agent_id=devops.id,
        task_type="deploy",
        description="Deploy security fix to production",
        dependencies=["Security Test"]
    ),
    WorkflowStep(
        name="Post-Mortem",
        agent_id=security_analyst.id,
        task_type="analysis",
        description="Document incident and prevention",
        dependencies=["Emergency Deploy"]
    )
]

workflow.steps = steps

# Register workflow
engine.register_workflow(workflow)

# Set up notification on completion
def notify_security_fix_complete(event):
    workflow_id = event.data['workflow_id']
    if workflow_id == workflow.id:
        print(f"🔒 Security fix deployed for {vuln_ticket.id}")
        # Send alerts, update status pages, etc.

subscribe_event(EventType.WORKFLOW_COMPLETED, notify_security_fix_complete)

# Start emergency response
engine.start_workflow(workflow.id)
print(f"🚨 Emergency security workflow started: {workflow.id}")
```

### Example 3: Microservice Deployment Pipeline

Deploy new microservice with full testing:

```python
#!/usr/bin/env python3
"""
Microservice deployment pipeline.
"""

from repo_tickets.workflows import Workflow, WorkflowStep, get_workflow_engine
from repo_tickets.storage import TicketStorage

def create_microservice_deployment_workflow(ticket_id, service_name):
    """Create comprehensive deployment workflow."""
    workflow = Workflow(
        id=f"WF-DEPLOY-{service_name}",
        name=f"Deploy {service_name}",
        ticket_id=ticket_id,
        description=f"Full deployment pipeline for {service_name} microservice"
    )
    
    steps = [
        # Stage 1: Pre-deployment
        WorkflowStep(
            name="Unit Tests",
            task_type="test",
            description="Run unit test suite",
            dependencies=[]
        ),
        WorkflowStep(
            name="Integration Tests",
            task_type="test",
            description="Run integration tests",
            dependencies=[]
        ),
        WorkflowStep(
            name="Build Container",
            task_type="build",
            description="Build Docker image",
            dependencies=["Unit Tests", "Integration Tests"]
        ),
        
        # Stage 2: Staging deployment
        WorkflowStep(
            name="Deploy to Staging",
            task_type="deploy",
            description=f"Deploy {service_name} to staging",
            dependencies=["Build Container"]
        ),
        WorkflowStep(
            name="Smoke Tests (Staging)",
            task_type="test",
            description="Run smoke tests on staging",
            dependencies=["Deploy to Staging"]
        ),
        WorkflowStep(
            name="Load Tests",
            task_type="test",
            description="Run load tests",
            dependencies=["Smoke Tests (Staging)"]
        ),
        
        # Stage 3: Production deployment
        WorkflowStep(
            name="Deploy to Production",
            task_type="deploy",
            description=f"Blue-green deploy {service_name} to prod",
            dependencies=["Load Tests"]
        ),
        WorkflowStep(
            name="Smoke Tests (Production)",
            task_type="test",
            description="Verify production deployment",
            dependencies=["Deploy to Production"]
        ),
        WorkflowStep(
            name="Monitor Metrics",
            task_type="monitoring",
            description="Monitor service health for 15 minutes",
            dependencies=["Smoke Tests (Production)"]
        )
    ]
    
    workflow.steps = steps
    return workflow

# Usage
storage = TicketStorage()
engine = get_workflow_engine()

# Create deployment ticket
ticket = storage.create_ticket(
    title="Deploy Payment Service v2.0",
    description="Deploy new payment processing microservice",
    priority="high",
    labels=["deployment", "microservice", "payment"]
)

# Create and start workflow
workflow = create_microservice_deployment_workflow(ticket.id, "payment-service")
engine.register_workflow(workflow)
engine.start_workflow(workflow.id)

print(f"Deployment pipeline started: {workflow.id}")
print(f"Monitor: tickets workflow show {workflow.id}")
```

---

## Best Practices

### 1. Design Workflows for Failure

Always handle potential failures:

```python
from repo_tickets.events import EventType, subscribe_event

def handle_workflow_failure(event):
    """Handle workflow failures gracefully."""
    workflow_id = event.data['workflow_id']
    error = event.data.get('error')
    
    # Log failure
    print(f"❌ Workflow {workflow_id} failed: {error}")
    
    # Create follow-up ticket
    storage.create_ticket(
        title=f"Investigate workflow failure: {workflow_id}",
        priority="high",
        labels=["workflow", "failure", "investigation"]
    )

subscribe_event(EventType.WORKFLOW_FAILED, handle_workflow_failure)
```

### 2. Use Time Estimates for Planning

Track and learn from duration estimates:

```python
from repo_tickets.metrics import get_system_metrics

metrics = get_system_metrics()

# Compare estimates vs actual
report = metrics.get_performance_report()
for op in report['operations']:
    if 'workflow' in op:
        estimated = op['estimated_duration']
        actual = op['avg_duration']
        accuracy = (1 - abs(estimated - actual) / estimated) * 100
        print(f"{op['name']}: {accuracy:.0f}% accurate")
```

### 3. Monitor Workflow Health

Track workflow metrics:

```python
from repo_tickets.workflows import get_workflow_engine

engine = get_workflow_engine()

# Get all workflows
all_workflows = engine.list_workflows()

# Calculate health metrics
total = len(all_workflows)
completed = len([w for w in all_workflows if w.state == 'completed'])
failed = len([w for w in all_workflows if w.state == 'failed'])
blocked = len([w for w in all_workflows if w.state == 'blocked'])

print(f"Workflow Health:")
print(f"  Completion rate: {completed/total*100:.1f}%")
print(f"  Failure rate: {failed/total*100:.1f}%")
print(f"  Blocked: {blocked}")
```

---

## Related Documentation

- **Usage Guide**: `USAGE_GUIDE.md` - Complete usage documentation
- **Architecture**: `ARCHITECTURE.md` - System architecture details
- **Agent Guide**: `AGENT_GUIDE.md` - AI agent integration
- **Examples**: `/examples` directory - Working code examples
