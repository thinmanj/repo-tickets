#!/usr/bin/env python3
"""
Example demonstrating structured logging for agents.

Shows how to use JSON-formatted logs for analysis and debugging.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from repo_tickets.logging_utils import (
    get_logger,
    configure_logging,
    log_performance,
    StructuredLogger
)


def example_basic_logging():
    """Basic structured logging example."""
    print("=" * 60)
    print("Basic Structured Logging")
    print("=" * 60)
    
    # Configure logging
    logger = configure_logging(
        level=logging.INFO,
        json_format=False  # Human-readable for demo
    )
    
    # Simple logs
    logger.info("Application started")
    logger.debug("Debug information (won't show at INFO level)")
    logger.warning("This is a warning")
    logger.error("An error occurred")
    
    print()


def example_context_logging():
    """Logging with context fields."""
    print("=" * 60)
    print("Logging with Context")
    print("=" * 60)
    
    logger = get_logger()
    
    # Log with ticket context
    logger.info(
        "Processing ticket",
        ticket_id="TICKET-123",
        status="in-progress",
        priority="high"
    )
    
    # Log with agent context
    logger.info(
        "Agent started task",
        agent_id="AGENT-BOT-1",
        task_type="code",
        ticket_id="TICKET-123"
    )
    
    # Log with user context
    logger.info(
        "User action",
        user="john.doe",
        action="create_ticket",
        ticket_id="TICKET-124"
    )
    
    print()


def example_convenience_methods():
    """Using convenience logging methods."""
    print("=" * 60)
    print("Convenience Methods")
    print("=" * 60)
    
    logger = get_logger()
    
    # Ticket operations
    logger.log_ticket_operation(
        "created",
        "TICKET-200",
        priority="critical",
        assignee="emergency-team"
    )
    
    # Agent operations
    logger.log_agent_operation(
        "task_completed",
        "AGENT-TESTER-1",
        ticket_id="TICKET-200",
        duration_ms=1250.5
    )
    
    # Performance logging
    logger.log_performance(
        "load_ticket",
        duration_ms=5.2,
        ticket_id="TICKET-200",
        cache_hit=True
    )
    
    print()


def example_performance_context_manager():
    """Using performance logging context manager."""
    print("=" * 60)
    print("Performance Context Manager")
    print("=" * 60)
    
    logger = get_logger()
    
    # Automatic performance tracking
    with log_performance("process_tickets", count=10):
        import time
        time.sleep(0.1)  # Simulate work
    
    with log_performance("search_index", query="login", fast=True):
        time.sleep(0.005)  # Simulate fast search
    
    # With error handling
    try:
        with log_performance("failing_operation", ticket_id="TICKET-500"):
            raise ValueError("Something went wrong")
    except ValueError:
        pass  # Error is logged automatically
    
    print()


def example_json_output():
    """JSON-formatted logs for log aggregation."""
    print("=" * 60)
    print("JSON-Formatted Logs (for parsing)")
    print("=" * 60)
    
    # Reconfigure for JSON output
    logger = configure_logging(
        level=logging.INFO,
        json_format=True
    )
    
    # These will output as JSON
    logger.info("Ticket created", ticket_id="TICKET-300", priority="high")
    logger.log_performance("api_call", duration_ms=150.5, endpoint="/tickets")
    logger.error(
        "Database connection failed",
        error_type="ConnectionError",
        retry_count=3
    )
    
    print()


def example_error_logging():
    """Logging errors with context."""
    print("=" * 60)
    print("Error Logging with Context")
    print("=" * 60)
    
    logger = configure_logging(json_format=False)
    
    # Error with ticket context
    try:
        raise ValueError("Invalid ticket status")
    except ValueError as e:
        logger.log_error_with_ticket(
            "Failed to update ticket",
            ticket_id="TICKET-400",
            error=e,
            attempted_status="invalid-status"
        )
    
    # Generic error
    logger.error(
        "Agent task failed",
        agent_id="AGENT-BOT-2",
        task_id="TASK-999",
        error_type="TimeoutError",
        error_message="Operation timed out after 30s"
    )
    
    print()


def example_agent_workflow_logging():
    """Logging a complete agent workflow."""
    print("=" * 60)
    print("Agent Workflow Logging")
    print("=" * 60)
    
    logger = configure_logging(json_format=False)
    
    # Workflow start
    logger.info(
        "Starting feature development workflow",
        workflow_id="WF-001",
        ticket_id="TICKET-500"
    )
    
    # Requirements phase
    with log_performance("requirements_analysis", workflow_id="WF-001"):
        import time
        time.sleep(0.05)
        logger.info(
            "Requirements analyzed",
            workflow_id="WF-001",
            requirements_count=5
        )
    
    # Design phase
    with log_performance("technical_design", workflow_id="WF-001"):
        time.sleep(0.03)
        logger.info(
            "Design completed",
            workflow_id="WF-001",
            components=["auth", "api", "db"]
        )
    
    # Implementation phase
    with log_performance("code_implementation", workflow_id="WF-001"):
        time.sleep(0.08)
        logger.info(
            "Code implemented",
            workflow_id="WF-001",
            files_changed=12,
            lines_added=450
        )
    
    # Testing phase
    with log_performance("testing", workflow_id="WF-001"):
        time.sleep(0.04)
        logger.info(
            "Tests completed",
            workflow_id="WF-001",
            tests_run=25,
            tests_passed=25
        )
    
    # Workflow complete
    logger.info(
        "Workflow completed successfully",
        workflow_id="WF-001",
        ticket_id="TICKET-500",
        total_duration_ms=200
    )
    
    print()


def main():
    """Run all examples."""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║  Structured Logging Examples for Agentic Development    ║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    example_basic_logging()
    example_context_logging()
    example_convenience_methods()
    example_performance_context_manager()
    example_error_logging()
    example_agent_workflow_logging()
    example_json_output()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print()
    print("Benefits for Agents:")
    print("  ✓ Structured logs are machine-parseable")
    print("  ✓ Context fields enable filtering and analysis")
    print("  ✓ Performance tracking identifies bottlenecks")
    print("  ✓ Error tracking with full context")
    print("  ✓ Works with log aggregation tools (ELK, Splunk)")
    print()


if __name__ == "__main__":
    main()
