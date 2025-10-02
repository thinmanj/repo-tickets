# Repo Tickets

A CLI ticket system that works with git, mercurial, and Jujutsu repositories without external services.

## Features

- **VCS Agnostic**: Works with git, mercurial (hg), and Jujutsu (jj) repositories
- **Self-contained**: No external services required - tickets stored in your repository
- **Distributed**: Tickets travel with your code through branches and merges
- **CLI-first**: Designed for developers who live in the terminal
- **Professional HTML Reports**: Interactive dashboards with charts and analytics
- **Advanced Analytics**: Risk assessment, velocity metrics, and team insights
- **Project Management**: Journal entries, time tracking, and performance metrics
- **Time Tracking**: Start/stop timers, manual time entry, and detailed logging
- **Performance Metrics**: Effort estimation, story points, and completion tracking
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

# Generate professional HTML report
tickets report

# Add PM journal entry with metrics
tickets journal TICKET-1 "Completed feature implementation" --type progress --completion 80 --spent 4.5

# Track time on a ticket
tickets time TICKET-1 --start --description "Working on bug fix"
tickets time TICKET-1 --stop
```

## How it works

Repo-tickets stores tickets as YAML files in a `.tickets/` directory in your repository root. This approach:

- Keeps tickets versioned alongside your code
- Allows tickets to be shared through normal VCS operations (push/pull/merge)
- Works offline and doesn't depend on external services
- Integrates naturally with your existing development workflow

## Commands

- `tickets init` - Initialize ticket system in current repository
- `tickets create TITLE` - Create a new ticket
- `tickets list` - List all tickets
- `tickets show ID` - Show ticket details
- `tickets update ID` - Update ticket properties
- `tickets close ID` - Close a ticket
- `tickets search QUERY` - Search tickets
- `tickets report` - Generate HTML report with analytics
- `tickets journal ID CONTENT` - Add PM journal entry with metrics
- `tickets time ID` - Track time spent on tickets
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