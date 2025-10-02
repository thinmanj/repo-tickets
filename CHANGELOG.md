# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- 🤖 **AI Agent System** - Complete automated task management and coordination system
  - Create specialized AI agents (developer, tester, analyst, reviewer, documenter, project_manager, general)
  - Manual and automatic task assignment with intelligent agent matching
  - Comprehensive agent performance tracking and metrics
  - Agent task management with status tracking, priorities, and execution timing
  - Multiple output formats (table, JSON, simple) for agent information
  - Full CLI integration with `tickets agent` command group
  - Agent data storage integrated with ticket system in `.tickets/agents/` directory
- Agent capabilities system with confidence levels and parameters
- Agent metrics tracking including success rates, execution times, and activity monitoring
- Task assignment algorithms with scoring based on agent type, availability, and performance
- Agent status management (active, inactive, busy, error, maintenance)
- Full integration with existing ticket workflow - agents can be assigned to tickets

### Fixed
- **Agent.from_dict method** - Fixed metrics field initialization for agents without activity history
  - Previously caused `'dict' object has no attribute 'success_rate'` error
  - Now properly reconstructs AgentMetrics object for all agents regardless of activity status

### Enhanced
- README.md with comprehensive AI agent documentation
- CLI help text and command organization with agent command group
- Error handling and validation for agent operations
- Storage system to support both tickets and agent data

## [Previous Versions]

### Core Features (Existing)
- VCS-agnostic ticket system (git, mercurial, Jujutsu support)
- Self-contained ticket storage in `.tickets/` directory
- CLI-first design with comprehensive command set
- Professional HTML reports with charts and analytics
- Time tracking with start/stop timers and manual entry
- Project management features with journal entries and metrics
- Advanced search and filtering capabilities
- Flexible configuration system with custom labels and statuses
- Terminal User Interface (TUI) for interactive management
- Performance metrics and effort estimation with story points