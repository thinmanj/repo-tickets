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