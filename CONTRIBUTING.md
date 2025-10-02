# 🤝 Contributing to Repo Tickets

Thank you for your interest in contributing to **repo-tickets**! This project aims to provide the best possible ticket management experience directly in the terminal.

## 🚀 Quick Start

1. **Fork** the repository
2. **Clone** your fork: `git clone git@github.com:yourusername/repo-tickets.git`
3. **Install dependencies**: `pip install -e .`
4. **Create a branch**: `git checkout -b feature/amazing-feature`
5. **Make your changes** and test thoroughly
6. **Submit a pull request**

## 📋 Development Setup

### Prerequisites
- Python 3.8+
- git, mercurial, or jujutsu (for VCS testing)
- Modern terminal with mouse support (for TUI testing)

### Installation
```bash
# Clone the repository
git clone git@github.com:thinmanj/repo-tickets.git
cd repo-tickets

# Install in development mode
pip install -e .

# Install development dependencies
pip install textual[dev] pytest black flake8 mypy
```

### Testing Your Changes
```bash
# Test CLI functionality
tickets init
tickets create "Test ticket" --description "Testing my changes"
tickets list
tickets show TEST-1

# Test TUI interface
tickets tui

# Run with different VCS systems
cd /path/to/git/repo && tickets init && tickets tui
cd /path/to/hg/repo && tickets init && tickets tui
```

## 🎯 Types of Contributions

### 🐛 Bug Fixes
- Look for issues labeled `bug`
- Reproduce the issue first
- Write a test that fails before your fix
- Ensure the test passes after your fix
- Update documentation if needed

### ✨ New Features
- Check existing issues and discussions first
- Create an issue to discuss major features
- Follow the existing code style and patterns
- Add comprehensive tests
- Update documentation and help text
- Consider both CLI and TUI interfaces

### 📚 Documentation
- Improve README, guides, or code comments
- Add examples and use cases
- Fix typos and clarity issues
- Update keyboard shortcuts documentation

### 🎨 TUI Improvements
- Enhance the Textual-based interface
- Add new keyboard shortcuts (update KEYBOARD_SHORTCUTS.md)
- Improve visual design and user experience
- Test across different terminal sizes and types

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 for Python code style
- Use meaningful variable and function names
- Add docstrings to public functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Commit Messages
Use conventional commits format:
```
type(scope): description

feat(tui): add keyboard shortcut for quick ticket creation
fix(cli): resolve issue with ticket ID generation
docs(readme): update installation instructions
refactor(storage): improve JSON serialization performance
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `perf`, `style`

### Testing
- Test CLI commands with different VCS systems
- Test TUI interface functionality and keyboard shortcuts
- Test edge cases and error conditions
- Verify backwards compatibility
- Test report generation and HTML output

### Documentation
- Update relevant .md files for new features
- Add/update CLI help text for new commands
- Document new keyboard shortcuts in KEYBOARD_SHORTCUTS.md
- Include examples in documentation

## 🔧 Project Structure

```
repo-tickets/
├── repo_tickets/           # Main package
│   ├── cli.py             # CLI interface and commands
│   ├── tui.py             # TUI interface with Textual
│   ├── models.py          # Data models (Ticket, Agent, TimeLog, etc.)
│   ├── agents.py          # AI agent management and storage
│   ├── storage.py         # JSON storage backend
│   ├── vcs.py             # VCS integration (git/hg/jj)
│   └── reports.py         # HTML report generation
├── .github/               # GitHub templates and workflows
├── docs/                  # Documentation files
├── tests/                 # Test files (future)
└── examples/              # Example configurations and demos
```

## 🎫 Working with Tickets

### Data Models
- `Ticket`: Core ticket with status, priority, time tracking, agent assignments
- `Agent`: AI agent with capabilities, metrics, and task management
- `AgentTask`: Tasks assigned to agents with execution tracking
- `AgentMetrics`: Performance tracking for agent success rates and timing
- `JournalEntry`: Progress updates with PM tracking features
- `TimeLog`: Time tracking with work types and descriptions
- `Comment`: User comments and discussions

### Storage System
- JSON-based storage in `.tickets/` directory
- VCS-aware (ignores .tickets/ by default)
- Atomic writes to prevent corruption
- Backwards compatibility maintained

### VCS Integration
- Detects git, Mercurial (hg), and Jujutsu (jj)
- Uses VCS user info for author/email
- Branch-aware ticket creation
- Repository root detection

## 🎨 TUI Development

### Framework
- Built with [Textual](https://textual.textualize.io/)
- Rich terminal formatting with [Rich](https://rich.readthedocs.io/)
- Event-driven architecture
- Modal screens for forms and details

### Key Components
- `RepoTicketsTUI`: Main app class
- `TicketDetailScreen`: Detailed ticket view modal
- `CreateTicketScreen`: Ticket creation form
- `TimeTrackingScreen`: Time tracking interface
- `HelpScreen`: Keyboard shortcuts help

### Adding New Features
1. Create new screen classes if needed
2. Add keyboard bindings to appropriate `BINDINGS` arrays
3. Implement action handlers (`action_*` methods)
4. Update help screen with new shortcuts
5. Test keyboard and mouse interactions

## 📊 Report System

### HTML Reports
- Professional styling with Chart.js integration
- Interactive charts and metrics
- Responsive design for different screen sizes
- Browser integration for automatic opening

### Adding New Metrics
1. Add calculation logic to `TicketReportGenerator`
2. Create corresponding HTML/CSS/JS components
3. Update chart configurations
4. Test with various data sets

## 🚦 Pull Request Process

1. **Create an issue** for significant changes
2. **Fork and branch** from `master`
3. **Make focused changes** (one feature/fix per PR)
4. **Write descriptive commit messages**
5. **Test thoroughly** across CLI and TUI
6. **Update documentation** as needed
7. **Fill out the PR template** completely
8. **Address review feedback** promptly

### Review Criteria
- ✅ Functionality works as expected
- ✅ Code follows project patterns and style
- ✅ Tests pass and new tests added where appropriate  
- ✅ Documentation updated
- ✅ No breaking changes (or clearly documented)
- ✅ Performance impact considered
- ✅ Backwards compatibility maintained

## 🔒 Branch Protection

The `master` branch is protected with the following rules:
- ✅ Require pull request reviews (1 approver)
- ✅ Dismiss stale reviews when new commits are pushed
- ✅ Require branches to be up to date before merging
- ✅ Enforce restrictions for administrators
- ✅ Prevent force pushes and deletions

## ❓ Getting Help

- **Issues**: Create a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Documentation**: Check existing guides and README files

## 🎉 Recognition

Contributors will be:
- Listed in the project README
- Credited in release notes for significant contributions
- Welcomed as maintainers for sustained contributions

Thank you for helping make repo-tickets better! 🚀