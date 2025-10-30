# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

repo-tickets is a VCS-agnostic CLI ticket management system that stores tickets as YAML files in the repository. It supports git, mercurial (hg), and Jujutsu (jj) version control systems. The system includes comprehensive features:

- Core ticket management (CRUD operations)
- Epic management for large features
- Product backlog with prioritization
- Requirements tracking (user stories, acceptance criteria, Gherkin scenarios)
- AI agent coordination system
- Time tracking and project management
- HTML report generation with analytics

## Development Commands

### Installation
```bash
# Install in development mode
pip install -e .

# Install with dependencies
pip install -r requirements.txt
```

### Running the CLI
```bash
# Main command
tickets --help

# Initialize in current repository
tickets init

# Common operations
tickets list
tickets create "Title" --description "Description"
tickets show TICKET-1
tickets update TICKET-1 --status in-progress
```

### Testing
```bash
# Run individual test scripts
python test_requirements.py
python test_epics_backlog.py

# These are comprehensive integration tests, not unit tests
# They test full workflows including storage, CLI, and models

# Run pytest if available (development dependency)
pytest -v
pytest --cov=repo_tickets

# Run demo scripts to validate features
./demo.sh
./journal_demo.sh
./report_demo.sh
```

### Code Quality
```bash
# Format code
black repo_tickets/

# Lint
flake8 repo_tickets/

# Type checking
mypy repo_tickets/
```

## Architecture

### Core Module Structure

```
repo_tickets/
├── cli.py         # Click-based CLI interface, all commands defined here
├── models.py      # Data models (Ticket, Epic, BacklogItem, Requirements, etc.)
├── storage.py     # Filesystem persistence layer (YAML-based)
├── vcs.py         # VCS abstraction (GitVCS, MercurialVCS, JujutsuVCS)
├── reports.py     # HTML report generation and analytics
├── agents.py      # AI agent coordination system
└── tui.py         # Textual-based TUI interface
```

### Data Storage Model

All data is stored in `.tickets/` directory as YAML files:

```
.tickets/
├── config.yaml                    # System configuration
├── index.yaml                     # Quick lookup index
├── open/                          # Active tickets
│   └── TICKET-*.yaml
├── closed/                        # Completed tickets
│   └── TICKET-*.yaml
├── epics/                         # Epic definitions
│   └── EPIC-*.yaml
├── backlog/                       # Product backlog items
│   └── BACKLOG-*.yaml
└── agents/                        # AI agent metadata
    └── AGENT-*.yaml
```

### VCS Abstraction Layer

The `vcs.py` module provides unified interface across VCS systems:

- `BaseVCS`: Abstract base class defining common operations
- `GitVCS`: Git implementation using subprocess calls
- `MercurialVCS`: Mercurial implementation
- `JujutsuVCS`: Jujutsu implementation
- `detect_vcs()`: Auto-detect VCS from repository structure
- `ensure_in_repository()`: Validate current directory is in repo

When adding VCS-specific features, extend the `BaseVCS` interface first, then implement for all three systems.

### Model Hierarchy

Key models in `models.py`:

- **Ticket**: Core work item with status, priority, assignee, labels, etc.
  - Contains: requirements, user_stories, expected_results, gherkin_scenarios
  - Has: comments, journal_entries, time_logs
  - Methods: `add_requirement()`, `add_user_story()`, `add_gherkin_scenario()`
  
- **Epic**: Large feature containing multiple tickets
  - Tracks: goals, success_criteria, target dates, story points
  - Bidirectional relationships with tickets
  
- **BacklogItem**: Prioritized product backlog
  - Has: business_value, effort_estimate, risk_level
  - Can be converted to full Ticket with `convert_to_ticket()`
  
- **Requirements**:
  - `Requirement`: Formal requirement with acceptance criteria
  - `UserStory`: As a/I want/So that format with story points
  - `ExpectedResult`: Verifiable outcome with success criteria
  - `GherkinScenario`: BDD Given-When-Then scenarios

All models use `@dataclass` with YAML serialization via `to_dict()` and `from_dict()` methods.

### CLI Command Pattern

All CLI commands in `cli.py` follow this pattern:

```python
@click.command()
@click.argument('arg_name')
@click.option('--option-name', help="Description")
def command_name(arg_name, option_name):
    """Command description shown in help."""
    storage = get_storage()  # Get TicketStorage instance
    # Perform operation
    # Format output with colorama
```

Commands are organized into command groups:
- Base commands: `init`, `list`, `create`, `show`, `update`, `close`, `search`
- Epic commands: `epic create/list/show/update/add-ticket/remove-ticket`
- Backlog commands: `backlog add/list/show/update/convert`
- Requirements: `requirements add/story/result/gherkin/list/verify`
- Agent commands: `agent create/list/show/assign/auto-assign/tasks`
- Analytics: `status`, `report`, `journal`, `time`

### Testing Approach

This project uses **integration test scripts** rather than traditional unit tests:

1. `test_requirements.py` - Tests requirements management system end-to-end
2. `test_epics_backlog.py` - Tests epic and backlog workflows
3. Demo scripts (`demo.sh`, `journal_demo.sh`) - Manual validation workflows

When modifying features:
- Run relevant test script to validate changes
- Test scripts create temp directories and run full workflows
- They test storage, models, and CLI together

### Agent Integration Architecture

The system is designed for AI agent interaction:

- All commands support `--format json` for machine-readable output
- `AGENT_GUIDE.md` and `AGENT_API.md` provide agent documentation
- `examples/bulk_operations.py` shows automation patterns
- Agents can be created in-system via `tickets agent create`
- Agent tasks are tracked with performance metrics

When building agent features, ensure:
- JSON output is complete and parseable
- Commands are idempotent where possible
- Error messages are structured
- All operations can be scripted

## Common Development Patterns

### Adding a New Command

1. Define command in `cli.py` using `@click.command()` decorator
2. Use `get_storage()` to get TicketStorage instance
3. Call storage methods or model methods
4. Format output with colorama for terminal display
5. Support `--format json` option for programmatic use

### Adding a New Field to Tickets

1. Update `Ticket` dataclass in `models.py`
2. Add field to `to_dict()` and `from_dict()` methods
3. Update YAML serialization/deserialization
4. Update CLI commands to accept new field
5. Update display formatting in `cli.py`
6. Run test scripts to ensure backward compatibility

### Supporting a New VCS

1. Create new class inheriting from `BaseVCS` in `vcs.py`
2. Implement all abstract methods
3. Add detection logic to `detect_vcs()` function
4. Test with actual repository of that VCS type

### Working with Requirements

Requirements are stored **inside** tickets, not as separate files:
- Use `ticket.add_requirement()`, `ticket.add_user_story()`, etc.
- All requirements have unique IDs within the ticket
- Requirements affect ticket's `requirements_status` field
- Analytics calculate coverage from requirements data

## Important Notes

- **VCS Pager Handling**: When using VCS commands (git, hg, jj), always use `--no-pager` flag to avoid hanging on paginated output
- **YAML Serialization**: datetime objects must be converted to ISO format strings in `to_dict()` methods
- **File Permissions**: `.tickets/` directory is typically not added to `.gitignore` - tickets should be tracked
- **Ticket IDs**: Generated using `generate_ticket_id()` which uses prefixes + incremental numbers
- **Status Directories**: Tickets physically move between `open/` and `closed/` directories when status changes
- **Colorama**: Cross-platform terminal colors, initialized with `colorama.init()` at CLI startup

## Key Dependencies

- **click**: CLI framework (all commands use Click decorators)
- **pyyaml**: YAML serialization for ticket storage
- **colorama**: Cross-platform colored terminal output
- **tabulate**: Pretty table formatting for lists
- **python-dateutil**: Date parsing and manipulation
- **rich**: Advanced terminal formatting
- **textual**: TUI framework for interactive interface

## Documentation Structure

Reference documentation in repository:
- `README.md` - User-facing documentation and examples
- `AGENT_GUIDE.md` - AI agent integration patterns
- `AGENT_API.md` - Technical API reference for agents
- `REQUIREMENTS.md` - Requirements management features
- `EPICS.md` - Epic and backlog management
- `REPORTING.md` - Analytics and reporting
- `TUI_GUIDE.md` - Text UI documentation
