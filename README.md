# Repo Tickets
## 📊 Project Status

<!-- AUTO-GENERATED STATUS - DO NOT EDIT MANUALLY -->
**Last Updated:** 2025-10-02 13:04:34

**Ticket Overview:**
- 🎫 Total: 4
- 📂 Open: 2
- ⚡ In Progress: 1
- ✅ Closed: 1

**Priority Items:**
- 🟡 High Priority: 1

**Recent Progress:**
- ✅ IMPLEMEN-1: Implement user authentication (2025-10-02)

**🤖 AI Agents:** 2/2 active, 2 active tasks

<!-- END AUTO-GENERATED STATUS -->


A CLI ticket system that works with git, mercurial, and Jujutsu repositories without external services.

## Features

- **VCS Agnostic**: Works with git, mercurial (hg), and Jujutsu (jj) repositories
- **Self-contained**: No external services required - tickets stored in your repository
- **Distributed**: Tickets travel with your code through branches and merges
- **CLI-first**: Designed for developers who live in the terminal
- **🤖 AI Agent System**: Automated task assignment and coordination with multiple AI agents
- **Professional HTML Reports**: Interactive dashboards with charts and analytics
- **Advanced Analytics**: Risk assessment, velocity metrics, and team insights
- **Project Management**: Journal entries, time tracking, and performance metrics
- **Time Tracking**: Start/stop timers, manual time entry, and detailed logging
- **Performance Metrics**: Effort estimation, story points, and completion tracking
- **📋 Requirements Management**: Comprehensive requirement tracking, user stories, and acceptance criteria
- **🧪 BDD Testing**: Gherkin scenario support with Given-When-Then format
- **🎯 Epic Management**: Large-scale feature planning with epic-level tracking and relationships
- **📋 Product Backlog**: Advanced backlog management with prioritization scoring and sprint planning
- **🚀 Sprint Planning**: Backlog grooming, readiness detection, and backlog-to-ticket conversion
- **Flexible**: Support for custom labels, statuses, and workflows

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Initialize tickets in your repository
tickets init

# Create a new ticket
tickets create "Fix login bug" --description "Users can't login with special characters"

# List all tickets
tickets list

# Show a specific ticket
tickets show TICKET-1

# Update ticket status
tickets update TICKET-1 --status in-progress

# Add labels
tickets update TICKET-1 --labels bug,urgent

# Search tickets
tickets search "login"

# Close a ticket
tickets close TICKET-1

# Check project status
tickets status
tickets status --format detailed
tickets status --update-readme --generate-report

# Generate professional HTML report
tickets report

# Add PM journal entry with metrics
tickets journal TICKET-1 "Completed feature implementation" --type progress --completion 80 --spent 4.5

# Track time on a ticket
tickets time TICKET-1 --start --description "Working on bug fix"
tickets time TICKET-1 --stop

# Create AI agents for automated task handling
tickets agent create "CodeBot" --type developer --max-tasks 3 --model "gpt-4"
tickets agent create "TestBot" --type tester --max-tasks 5 --model "claude-3-opus"

# List available agents
tickets agent list

# Assign task to specific agent
tickets agent assign TICKET-1 AGENT-CODEBOT code "Implement login fix" --priority high

# Auto-assign task to best available agent
tickets agent auto-assign TICKET-2 test "Write unit tests" --priority medium

# View agent tasks and performance
tickets agent tasks
tickets agent show AGENT-CODEBOT

# Epic and backlog management
tickets epic create "User Management System" --description "Complete user auth and profiles" --priority high --target-version "v1.0"
tickets backlog add "User Registration" --type feature --priority high --story-points 8 --business-value 90 --epic-id USER-1
tickets epic add-ticket USER-1 AUTH-1
tickets epic show USER-1

# Requirements management
tickets requirements add TICKET-1 --title "User Authentication" --priority high
tickets requirements story TICKET-1 --persona "user" --goal "log in securely" --benefit "access my account" --points 5
tickets requirements result TICKET-1 --description "Login page loads < 2s" --method automated
tickets requirements gherkin TICKET-1 --title "Valid login" --given "I am on login page" --when "I enter valid credentials" --then "I should be logged in"
tickets requirements list TICKET-1
```

## How it works

Repo-tickets stores tickets as YAML files in a `.tickets/` directory in your repository root. This approach:

- Keeps tickets versioned alongside your code
- Allows tickets to be shared through normal VCS operations (push/pull/merge)
- Works offline and doesn't depend on external services
- Integrates naturally with your existing development workflow

## 🤖 Agent Integration

repo-tickets is designed from the ground up to work seamlessly with AI agents. The system provides comprehensive APIs, documentation, and automation capabilities specifically for autonomous agent interaction.

### Agent-Friendly Features:
- **JSON-First CLI**: All commands support `--format json` for easy parsing
- **Predictable Data Structure**: Consistent file layouts and naming conventions
- **Complete API Coverage**: Programmatic access to all features through CLI and direct file access
- **Automation Scripts**: Pre-built workflows for common agent tasks
- **Error Handling**: Robust error responses with detailed context
- **Bulk Operations**: Efficient batch processing capabilities
- **State Monitoring**: Built-in health checks and system monitoring

### Quick Agent Setup:
```bash
# Agents can check system availability
tickets --help && tickets list --format json

# Create tickets programmatically
tickets create --title "Agent Task" --priority high --assignee "ai-agent" --format json

# Monitor system health
tickets list --status todo --format json | jq length

# Bulk operations
tickets list --assignee "ai-agent" --format json | jq -r '.[].id' | xargs -I {} tickets update {} --status "in-progress"
```

### Agent Resources:
- **[AGENT_GUIDE.md](AGENT_GUIDE.md)** - Comprehensive guide for AI agent integration
- **[AGENT_API.md](AGENT_API.md)** - Technical API reference and data structures
- **[examples/](examples/)** - Ready-to-use automation scripts and workflows
  - `agent_workflow.sh` - Complete autonomous workflow example
  - `bulk_operations.py` - Python automation library
  - `monitoring.sh` - Continuous system monitoring

### Agent Workflow Example:
```bash
# Autonomous epic creation and management
epic_id=$(tickets epic create --name "AI Feature" --format json | jq -r '.id')
tickets create --title "Implement AI" --epic-id "$epic_id" --assignee "agent" --format json
tickets backlog add --title "AI Testing" --priority-score 90 --format json
```

Agents can fully manage the entire project lifecycle from epic planning through ticket completion, with complete audit trails and collaboration capabilities.

## Commands

### Core Ticket Management
- `tickets init` - Initialize ticket system in current repository
- `tickets create TITLE` - Create a new ticket
- `tickets list` - List all tickets
- `tickets show ID` - Show ticket details
- `tickets update ID` - Update ticket properties
- `tickets close ID` - Close a ticket
- `tickets search QUERY` - Search tickets

### Epic Management 🎯
- `tickets epic create TITLE` - Create a new epic with goals and success criteria
- `tickets epic list` - List all epics with status and progress
- `tickets epic show EPIC_ID` - Show detailed epic information and associated tickets
- `tickets epic update EPIC_ID` - Update epic properties, dates, and priorities
- `tickets epic add-ticket EPIC_ID TICKET_ID` - Add ticket to epic (bidirectional)
- `tickets epic remove-ticket EPIC_ID TICKET_ID` - Remove ticket from epic

### Product Backlog Management 📋
- `tickets backlog add TITLE` - Add item to backlog with business value and effort estimates
- `tickets backlog list` - List backlog items prioritized by scoring algorithm
- `tickets backlog show ITEM_ID` - Show detailed backlog item with acceptance criteria
- `tickets backlog update ITEM_ID` - Update backlog item properties and sprint assignment
- `tickets backlog convert ITEM_ID` - Convert backlog item to full ticket with requirements

### Requirements Management 📋
- `tickets requirements add TICKET_ID` - Add formal requirement with acceptance criteria
- `tickets requirements story TICKET_ID` - Add user story with persona, goal, and benefit
- `tickets requirements result TICKET_ID` - Add expected result with verification method
- `tickets requirements gherkin TICKET_ID` - Add Gherkin BDD scenario
- `tickets requirements list TICKET_ID` - View all requirements for a ticket
- `tickets requirements verify TICKET_ID RESULT_ID` - Mark expected result as verified

### AI Agent Management 🤖
- `tickets agent create NAME` - Create a new AI agent
- `tickets agent list` - List all agents with status and metrics
- `tickets agent show ID` - Show detailed agent information
- `tickets agent assign TICKET_ID AGENT_ID TYPE DESC` - Assign task to specific agent
- `tickets agent auto-assign TICKET_ID TYPE DESC` - Auto-assign to best available agent
- `tickets agent tasks` - List all agent tasks

### Analytics & Reporting
- `tickets report` - Generate HTML report with analytics
- `tickets status` - Show project status summary with recent progress
- `tickets journal ID CONTENT` - Add PM journal entry with metrics
- `tickets time ID` - Track time spent on tickets

### Configuration
- `tickets config` - Manage configuration

## Configuration

The system supports per-repository and global configuration through `.tickets/config.yaml`:

```yaml
default_status: open
statuses:
  - open
  - in-progress  
  - closed
labels:
  - bug
  - feature
  - urgent
  - nice-to-have
```

## AI Agent System 🤖

Repo-tickets includes a sophisticated AI agent system for automated task management and coordination. Create specialized AI agents to handle different types of work, assign tasks automatically, and track performance.

### Agent Types

- **developer** - Specialized in coding, implementation, and technical tasks
- **reviewer** - Focused on code review and quality assurance  
- **tester** - Handles testing, QA, and validation tasks
- **analyst** - Performs analysis, research, and documentation
- **documenter** - Creates and maintains documentation
- **project_manager** - Coordinates tasks and manages project workflows
- **general** - Can handle any type of task

### Creating Agents

```bash
# Create a developer agent with GPT-4
tickets agent create "CodeBot" \
  --description "AI developer specialized in Python and JavaScript" \
  --type developer \
  --max-tasks 3 \
  --model "gpt-4"

# Create a testing agent with Claude
tickets agent create "TestBot" \
  --description "AI testing agent for QA and automated testing" \
  --type tester \
  --max-tasks 5 \
  --model "claude-3-opus"
```

### Task Assignment

#### Manual Assignment
```bash
# Assign specific task to specific agent
tickets agent assign TICKET-1 AGENT-CODEBOT code \
  "Implement JWT authentication" \
  --priority high \
  --instructions "Create middleware, login endpoints, and API protection"
```

#### Automatic Assignment
```bash
# Let the system choose the best agent for the task
tickets agent auto-assign TICKET-2 test \
  "Write unit tests for authentication" \
  --priority medium
```

The auto-assignment system uses intelligent scoring to match:
- Agent type with task type
- Agent availability (current task load)
- Agent performance history
- Task priority and complexity

### Agent Management

```bash
# List all agents with status and metrics
tickets agent list

# View detailed agent information
tickets agent show AGENT-CODEBOT

# List all agent tasks across agents
tickets agent tasks

# Filter tasks by agent, ticket, or status
tickets agent tasks --agent AGENT-CODEBOT --status in-progress
```

### Agent Performance Tracking

Each agent automatically tracks:
- **Tasks completed/failed** - Success rate metrics
- **Execution time** - Average time per task type
- **Response time** - How quickly agents start tasks
- **Last activity** - Agent health monitoring
- **Task type breakdown** - Performance by task category

### Output Formats

Agent information supports multiple output formats:

```bash
# Table format (default)
tickets agent list

# JSON format for integration
tickets agent list --format json

# Simple format for scripts
tickets agent list --format simple
```

### Agent Integration

- **Ticket Assignment** - Agents can be assigned to tickets
- **Task Tracking** - Each ticket can have multiple agent tasks
- **Workflow Integration** - Agent tasks appear in reports and analytics
- **VCS Integration** - Agent data stored alongside tickets in `.tickets/agents/`

## Requirements Management 📋

Repo-tickets provides comprehensive requirements management capabilities that integrate seamlessly with ticket tracking. Define formal requirements, write user stories, specify expected results, and create Gherkin acceptance tests.

### Requirements Types

#### Formal Requirements
Structured requirements with priorities, statuses, and acceptance criteria:

```bash
# Add a requirement
tickets requirements add TICKET-1 \
  --title "Password Security" \
  --description "Implement secure password validation" \
  --priority critical \
  --criteria "Minimum 8 characters" \
  --criteria "Must contain uppercase, lowercase, and numbers"
```

#### User Stories  
Agile user stories following the "As a..., I want..., so that..." format:

```bash
# Add a user story
tickets requirements story TICKET-1 \
  --persona "developer" \
  --goal "track time on tickets" \
  --benefit "I can provide accurate estimates" \
  --priority high \
  --points 8 \
  --criteria "Timer can be started and stopped" \
  --criteria "Time is recorded accurately"
```

#### Expected Results
Verifiable outcomes with success criteria:

```bash
# Add expected result
tickets requirements result TICKET-1 \
  --description "Login API responds within 500ms" \
  --method automated \
  --criteria "95% of requests complete under 500ms" \
  --criteria "Error rate below 0.1%"
```

#### Gherkin Scenarios
BDD-style acceptance tests using Given-When-Then format:

```bash
# Add Gherkin scenario
tickets requirements gherkin TICKET-1 \
  --title "Successful user login" \
  --given "I am on the login page" \
  --given "I have valid credentials" \
  --when "I enter username and password" \
  --when "I click the login button" \
  --then "I should be redirected to dashboard" \
  --tags authentication --tags smoke

# Or load from file
tickets requirements gherkin TICKET-1 --file login_scenarios.feature
```

### Requirements Analytics

The system automatically calculates comprehensive metrics:

- **Requirements Coverage**: % of requirements implemented/verified
- **Test Pass Rate**: % of Gherkin scenarios passing  
- **Acceptance Rate**: % of tickets meeting acceptance criteria
- **Story Point Velocity**: Completed points over time
- **Verification Methods**: Distribution of testing approaches

These metrics appear in:
- HTML reports with visual dashboards
- Status command output
- README status sections
- JSON exports for automation

### Workflow Integration

Requirements integrate with the entire ticket lifecycle:

```bash
# View requirements summary
tickets requirements list TICKET-1

# View detailed breakdown
tickets requirements list TICKET-1 --format detailed

# View only Gherkin scenarios
tickets requirements list TICKET-1 --format gherkin

# Mark results as verified
tickets requirements verify TICKET-1 RESULT-123 --notes "Performance testing complete"
```

### Status Tracking

**Requirements**: draft → approved → implemented → verified
**Scenarios**: draft → ready → passing/failing → blocked
**Expected Results**: pending → verified/failed → blocked

### Best Practices

1. **Start with User Stories** - Define value before implementation
2. **Write Testable Requirements** - Use measurable acceptance criteria
3. **Use Consistent Tagging** - Organize scenarios by feature, risk, type
4. **Keep Scenarios Focused** - One behavior per scenario
5. **Verify Early and Often** - Update status as work progresses

See [REQUIREMENTS.md](REQUIREMENTS.md) for comprehensive documentation and examples.

## Epic and Backlog Management 🎯📋

Repo-tickets provides enterprise-grade epic planning and product backlog management, enabling professional Agile/Scrum workflows with complete traceability from business goals to development tasks.

### Epic Management

Epics represent large bodies of work that span multiple sprints and tickets. They provide high-level tracking for major features, initiatives, or business goals.

**Epic Lifecycle:** Draft → Active → Completed / Cancelled

```bash
# Create a comprehensive epic
tickets epic create "E-commerce Platform" \
  --description "Complete online shopping experience" \
  --priority critical \
  --owner "Product Team" \
  --target-version "v2.0" \
  --target-date "2024-12-31" \
  --estimated-points 200

# Manage epic relationships
tickets epic add-ticket ECOM-1 CART-1
tickets epic add-ticket ECOM-1 PAYMENT-1
tickets epic add-ticket ECOM-1 CHECKOUT-1

# Track epic progress
tickets epic show ECOM-1
tickets epic list --status active
```

**Epic Features:**
- Target versions and completion dates with overdue detection
- Goals and measurable success criteria
- Story point estimation and progress tracking
- Bidirectional ticket relationships
- Owner assignment and team coordination

### Product Backlog Management

The backlog system enables professional product management with prioritization scoring, sprint planning, and requirement tracking.

**Backlog Lifecycle:** New → Groomed → Ready → In Progress → Done / Cancelled

```bash
# Add items with comprehensive metadata
tickets backlog add "User Registration" \
  --type feature \
  --priority high \
  --story-points 8 \
  --business-value 90 \
  --effort-estimate 16 \
  --risk-level medium \
  --epic-id USER-1 \
  --component "Authentication" \
  --theme "User Onboarding"

# Prioritized listing (automatic scoring)
tickets backlog list

# Sprint planning filters
tickets backlog list --status ready
tickets backlog list --epic USER-1
tickets backlog list --sprint SPRINT-1
```

### Advanced Prioritization

Backlog items are automatically prioritized using a sophisticated scoring algorithm:

**Priority Score = (Base Priority × 100) + Business Value - (Story Points × 2)**

This balances:
- **Strategic Priority** (critical=4, high=3, medium=2, low=1)
- **Business Value** (1-100 scale of user/business impact)
- **Development Effort** (story points using Fibonacci scale)

Items are automatically sorted by priority score for optimal sprint planning.

### Sprint Planning Features

```bash
# Check sprint readiness
# Items are ready when they have:
# - Status: groomed or ready
# - Story points assigned
# - Acceptance criteria defined
tickets backlog list --status ready

# Convert ready items to development tickets
tickets backlog convert LOGIN-1 \
  --reporter "Product Manager" \
  --reporter-email "pm@company.com"

# This automatically:
# - Creates a full ticket with all metadata
# - Converts acceptance criteria to requirements
# - Links to the original backlog item
# - Updates backlog item status to "in-progress"
```

### Professional Workflows

**Epic Planning Workflow:**
1. Create epic with business goals and success criteria
2. Add backlog items and associate with epic
3. Prioritize and groom backlog items
4. Convert ready items to tickets for development
5. Track progress through epic dashboard

**Team Coordination:**
- **Product Owner**: Manages backlog priorities and business value
- **Scrum Master**: Reviews sprint readiness and team metrics
- **Developers**: Convert backlog items and implement features
- **Team**: Tracks epic progress and release planning

### Integration with Requirements

Epics and backlog items seamlessly integrate with the requirements system:

- **Backlog Items** can have acceptance criteria and definition of done
- **Epic Goals** become high-level success criteria  
- **Converted Tickets** automatically inherit requirements from backlog items
- **Traceability** from epic → backlog item → ticket → requirements

### Analytics and Reporting

Comprehensive metrics for professional project management:

- **Epic Progress**: Story points completed, tickets closed, timeline tracking
- **Backlog Health**: Items ready for sprint, prioritization distribution
- **Sprint Metrics**: Velocity, burndown, completion rates
- **Team Performance**: Individual and team story point delivery

All metrics appear in HTML reports, status commands, and project dashboards.

See [EPICS.md](EPICS.md) for comprehensive documentation, CLI reference, and best practices.
