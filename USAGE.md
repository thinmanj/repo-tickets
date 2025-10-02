# Repo-Tickets Usage Guide

## Overview

Repo-Tickets is a CLI ticket system that works directly within your version control repositories (git, mercurial, Jujutsu). Tickets are stored as YAML files in a `.tickets/` directory, making them version-controlled and distributed alongside your code.

## Getting Started

### 1. Installation

```bash
pip install -e .
```

### 2. Initialize in Your Repository

Navigate to any git, mercurial, or Jujutsu repository and run:

```bash
tickets init
```

This creates a `.tickets/` directory with the following structure:
```
.tickets/
├── config.yaml      # Configuration settings
├── index.yaml       # Quick index of all tickets
├── open/            # Open ticket files
└── closed/          # Closed ticket files
```

## Core Commands

### Creating Tickets

```bash
# Basic ticket
tickets create "Fix login bug"

# With description and priority
tickets create "Add dark mode" -d "Implement dark theme" -p high

# With labels and assignee
tickets create "Update docs" -l documentation,urgent -a "john@example.com"
```

**Options:**
- `-d, --description`: Detailed description
- `-p, --priority`: critical, high, medium, low (default: medium)
- `-a, --assignee`: Assign to someone
- `-l, --labels`: Comma-separated labels

### Listing Tickets

```bash
# List open tickets (default)
tickets list

# List all tickets (including closed)
tickets list --all

# Filter by status
tickets list -s in-progress

# Filter by labels
tickets list -l bug,urgent

# Filter by assignee  
tickets list -a "john@example.com"
```

### Viewing Ticket Details

```bash
tickets show TICKET-1
```

This shows:
- Full ticket information
- All comments
- Creation/update timestamps
- VCS branch information

### Updating Tickets

```bash
# Change status
tickets update TICKET-1 -s in-progress

# Assign to someone
tickets update TICKET-1 -a "jane@example.com"

# Update multiple fields
tickets update TICKET-1 -s blocked -p critical -l bug,urgent

# Update title and description
tickets update TICKET-1 -t "New title" -d "Updated description"
```

### Adding Comments

```bash
tickets comment TICKET-1 "Started working on this issue"
```

### Searching Tickets

```bash
# Search in titles, descriptions, and comments
tickets search "authentication"
tickets search "login bug"
```

### Closing Tickets

```bash
tickets close TICKET-1
```

### Project Status

```bash
# Show project status summary
tickets status

# Show detailed status with ticket listings
tickets status --format detailed

# Get JSON output for integration
tickets status --format json

# Update README.md with current status
tickets status --update-readme

# Generate detailed STATUS.md report
tickets status --generate-report

# Both update README and generate report
tickets status --update-readme --generate-report

# Check status for different time periods
tickets status --days 30  # Last 30 days of activity
tickets status --days 1   # Just today's changes
```

The status command provides:
- **Overview**: Total tickets, open, in-progress, closed counts
- **Priority Breakdown**: Critical and high priority items
- **Recent Progress**: Recently closed tickets in specified time period
- **AI Agent Status**: Agent availability and active tasks
- **README Integration**: Auto-updates README.md with status section
- **Detailed Reports**: Generates STATUS.md with comprehensive breakdown

### Statistics

```bash
tickets stats
```

Shows breakdown by status (open, in-progress, blocked, closed, etc.).

## Configuration

### View Configuration

```bash
tickets config
```

### Edit Configuration

```bash
tickets config --edit
```

Opens the config file in your `$EDITOR` (defaults to vi).

### Reset Configuration

```bash
tickets config --reset
```

### Configuration Options

The `.tickets/config.yaml` file supports:

```yaml
default_status: open
statuses:
  - open
  - in-progress
  - blocked
  - closed
  - cancelled
priorities:
  - critical
  - high
  - medium
  - low
labels:
  - bug
  - feature
  - enhancement
  - documentation
  - urgent
id_prefix: TICKET
```

## VCS Integration

### Automatic Detection

Repo-tickets automatically detects your VCS:
- **Git**: Detects `.git` directory
- **Mercurial**: Detects `.hg` directory  
- **Jujutsu**: Detects `.jj` directory

### User Information

User information is automatically pulled from VCS config:
- **Git**: `git config user.name` and `git config user.email`
- **Mercurial**: `hg config ui.username`
- **Jujutsu**: `jj config get user.name` and `jj config get user.email`

### Branch Information

Tickets automatically capture the current branch when created:
- **Git**: Uses `git rev-parse --abbrev-ref HEAD`
- **Mercurial**: Uses `hg branch`
- **Jujutsu**: Uses `jj log -r @ --no-graph -T branches`

## Workflow Examples

### Bug Tracking Workflow

```bash
# Report a bug
tickets create "Login fails with special characters" \
  -d "Users can't login when password contains @, #, or %" \
  -p high -l bug,security

# Start working on it
tickets update BUG-1 -s in-progress -a "developer@company.com"

# Add progress updates
tickets comment BUG-1 "Identified the issue in password validation"
tickets comment BUG-1 "Fixed and tested locally"

# Close when done
tickets close BUG-1
```

### Feature Development Workflow

```bash
# Create feature request
tickets create "Add user profile page" \
  -d "Users should be able to view and edit their profile information" \
  -p medium -l feature

# Break down into sub-tasks (create separate tickets)
tickets create "Design user profile UI" -l feature,ui
tickets create "Implement profile backend API" -l feature,backend
tickets create "Add profile photo upload" -l feature,ui

# Track progress
tickets list -l feature
tickets update PROFILE-1 -s in-progress
```

### Release Planning

```bash
# See all open tickets
tickets list

# Filter by priority for release planning
tickets list -l urgent
tickets list -s blocked

# Get overview
tickets stats
```

## Integration with Git Workflows

### Commit Messages

You can reference tickets in commit messages:

```bash
git commit -m "Fix password validation issue (fixes FIX-1)"
```

### Branch Naming

Use ticket IDs in branch names:

```bash
git checkout -b feature/ADD-1-user-profile
```

### .gitignore

The `.tickets/` directory should be committed to your repository to share tickets with your team. However, you might want to ignore temporary files:

```gitignore
# Don't ignore the tickets directory itself
# .tickets/

# But you could ignore backup files if your editor creates them
.tickets/*.bak
.tickets/*~
```

## AI Agent System 🤖

Repo-tickets includes a comprehensive AI agent system for automated task management. Create AI agents to handle different types of work and automatically assign tasks based on agent capabilities and availability.

### Creating AI Agents

```bash
# Create a developer agent
tickets agent create "CodeBot" \
  --description "AI developer specialized in Python and JavaScript" \
  --type developer \
  --max-tasks 3 \
  --model "gpt-4" \
  --endpoint "https://api.openai.com/v1"

# Create a testing agent
tickets agent create "TestBot" \
  --description "AI testing specialist for QA and validation" \
  --type tester \
  --max-tasks 5 \
  --model "claude-3-opus"
```

**Agent Types:**
- `developer` - Coding and implementation tasks
- `reviewer` - Code review and quality assurance
- `tester` - Testing, QA, and validation
- `analyst` - Analysis and research tasks
- `documenter` - Documentation creation/maintenance
- `project_manager` - Task coordination and workflow management
- `general` - Can handle any task type

### Managing Agents

```bash
# List all agents
tickets agent list

# View detailed agent information
tickets agent show AGENT-CODEBOT

# List agents in different formats
tickets agent list --format json    # JSON output
tickets agent list --format simple  # Simple list
tickets agent list --all            # Include inactive agents
```

### Task Assignment

#### Manual Assignment
```bash
# Assign specific task to specific agent
tickets agent assign TICKET-1 AGENT-CODEBOT code \
  "Implement JWT authentication middleware" \
  --priority high \
  --instructions "Create Express middleware for JWT validation, add login/logout endpoints"
```

#### Automatic Assignment
```bash
# Let system choose best agent for the task
tickets agent auto-assign TICKET-2 test \
  "Write comprehensive unit tests for auth system" \
  --priority medium
```

The auto-assignment system considers:
- Agent type matching task type
- Current agent workload and availability
- Agent performance history and success rates
- Task priority and estimated complexity

### Task Management

```bash
# List all agent tasks
tickets agent tasks

# Filter tasks by agent
tickets agent tasks --agent AGENT-CODEBOT

# Filter by status
tickets agent tasks --status assigned
tickets agent tasks --status in-progress
tickets agent tasks --status completed

# Filter by ticket
tickets agent tasks --ticket TICKET-1
```

### Agent Performance Tracking

Each agent automatically tracks:
- **Success Rate**: Percentage of completed vs failed tasks
- **Execution Time**: Average time spent on different task types
- **Response Time**: How quickly agent starts assigned tasks
- **Task Breakdown**: Performance metrics by task category
- **Activity Status**: Last activity timestamp and availability

### Workflow Integration

#### With Regular Tickets
```bash
# Create ticket
tickets create "Implement user dashboard" -d "Create responsive user dashboard" -p high

# Assign to agent for implementation
tickets agent assign DASHBOARD-1 AGENT-CODEBOT code \
  "Build user dashboard with React" \
  --instructions "Use Material-UI components, implement responsive design"

# Assign testing to another agent
tickets agent auto-assign DASHBOARD-1 test \
  "Test dashboard functionality and responsiveness"

# Check progress
tickets agent tasks --ticket DASHBOARD-1
tickets show DASHBOARD-1
```

#### Task Status Lifecycle
1. **assigned** - Task created and assigned to agent
2. **in-progress** - Agent has started working on task
3. **completed** - Task finished successfully
4. **failed** - Task encountered errors or couldn't be completed

### Agent Workflow Examples

#### Development Team Setup
```bash
# Create specialized agents
tickets agent create "BackendBot" --type developer --model "gpt-4" --max-tasks 2
tickets agent create "FrontendBot" --type developer --model "claude-3-opus" --max-tasks 3
tickets agent create "QABot" --type tester --model "gpt-4" --max-tasks 5
tickets agent create "DocBot" --type documenter --model "claude-3-haiku" --max-tasks 4

# Create feature with multiple tasks
tickets create "User Authentication System" -p high
tickets agent assign AUTH-1 AGENT-BACKENDBOT code "JWT backend implementation"
tickets agent assign AUTH-1 AGENT-FRONTENDBOT code "Login UI components"
tickets agent auto-assign AUTH-1 test "Authentication flow testing"
tickets agent auto-assign AUTH-1 document "API documentation update"
```

#### Code Review Workflow
```bash
# Create reviewer agent
tickets agent create "ReviewBot" --type reviewer --model "gpt-4" --max-tasks 10

# Assign code review tasks
tickets agent assign FEATURE-1 AGENT-REVIEWBOT review \
  "Review pull request #123" \
  --instructions "Check code quality, security, and test coverage"
```

## Advanced Usage

### Custom Labels

Add custom labels to your configuration:

```yaml
labels:
  - bug
  - feature
  - enhancement
  - documentation
  - urgent
  - needs-review
  - blocked-external
  - technical-debt
```

### Custom Statuses

Define your own workflow statuses:

```yaml
statuses:
  - backlog
  - todo
  - in-progress
  - in-review
  - testing
  - done
  - cancelled
```

### Filtering Complex Queries

```bash
# High priority bugs
tickets list -s open -l bug -p high

# All tickets assigned to you
tickets list -a "$(git config user.email)"

# All urgent items
tickets list -l urgent
```

## Tips and Best Practices

### 1. Consistent Labeling
Establish a consistent labeling system with your team:
- `bug`: Something is broken
- `feature`: New functionality
- `enhancement`: Improve existing functionality
- `documentation`: Documentation updates
- `urgent`: Needs immediate attention

### 2. Descriptive Titles
Use clear, specific titles:
- ✅ "Login button doesn't respond on mobile Safari"
- ❌ "Login broken"

### 3. Regular Cleanup
Periodically review and close completed tickets:

```bash
tickets list --all | grep closed
```

### 4. Use Comments for Updates
Keep a paper trail of progress:

```bash
tickets comment TICKET-1 "Reproduced on staging environment"
tickets comment TICKET-1 "Root cause: database connection timeout"
tickets comment TICKET-1 "Applied fix and deploying to production"
```

### 5. Link to Code
Reference tickets in your code and commits:

```python
# TODO: Remove this workaround once PERF-5 is completed
# See ticket PERF-5 for details on the performance issue
```

## Troubleshooting

### "Not in a repository" Error
Make sure you're running commands from within a git, mercurial, or Jujutsu repository.

### "Tickets not initialized" Error
Run `tickets init` first to set up the ticket system.

### Configuration Issues
Reset to defaults with `tickets config --reset` if you encounter config errors.

### File Permissions
Ensure the `.tickets/` directory is readable and writable by your user.

## Migration and Backup

Since tickets are stored as YAML files in your repository, they:
- ✅ Are automatically backed up with your code
- ✅ Can be migrated by copying the `.tickets/` directory
- ✅ Are shared with your team through normal git/hg/jj operations
- ✅ Can be inspected and edited with any text editor
- ✅ Work offline without external dependencies