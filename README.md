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

## Commands

### Core Ticket Management
- `tickets init` - Initialize ticket system in current repository
- `tickets create TITLE` - Create a new ticket
- `tickets list` - List all tickets
- `tickets show ID` - Show ticket details
- `tickets update ID` - Update ticket properties
- `tickets close ID` - Close a ticket
- `tickets search QUERY` - Search tickets

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
