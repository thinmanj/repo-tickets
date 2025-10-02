#!/usr/bin/env python3
"""
CLI interface for repo-tickets.

Provides command-line interface for managing tickets in repositories.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path
import re
import json

import click
import colorama
from colorama import Fore, Style
from tabulate import tabulate

from .models import Ticket, Comment, JournalEntry, TimeLog, JournalEntryType
from .storage import TicketStorage
from .vcs import ensure_in_repository, detect_vcs, VCSError
from .reports import TicketReportGenerator, open_in_browser


# Initialize colorama for cross-platform colored output
colorama.init()


def get_storage() -> TicketStorage:
    """Get ticket storage instance, ensuring we're in a repository."""
    try:
        return TicketStorage()
    except VCSError as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


def format_ticket_short(ticket: Ticket) -> List[str]:
    """Format a ticket for list display."""
    # Color status
    status_colors = {
        'open': Fore.GREEN,
        'in-progress': Fore.YELLOW,
        'blocked': Fore.RED,
        'closed': Fore.BLUE,
        'cancelled': Fore.MAGENTA,
    }
    
    status_color = status_colors.get(ticket.status, Fore.WHITE)
    colored_status = f"{status_color}{ticket.status}{Style.RESET_ALL}"
    
    # Color priority
    priority_colors = {
        'critical': Fore.RED,
        'high': Fore.YELLOW,
        'medium': Fore.WHITE,
        'low': Fore.CYAN,
    }
    
    priority_color = priority_colors.get(ticket.priority, Fore.WHITE)
    colored_priority = f"{priority_color}{ticket.priority}{Style.RESET_ALL}"
    
    # Truncate title if too long
    title = ticket.title[:50] + "..." if len(ticket.title) > 50 else ticket.title
    
    # Format labels
    labels_str = ", ".join(ticket.labels) if ticket.labels else ""
    
    return [
        f"{Fore.CYAN}{ticket.id}{Style.RESET_ALL}",
        title,
        colored_status,
        colored_priority,
        labels_str,
        str(ticket.age_days) + "d",
        ticket.assignee or "",
    ]


def format_ticket_full(ticket: Ticket) -> str:
    """Format a ticket for detailed display."""
    lines = []
    
    # Header
    lines.append(f"{Fore.CYAN}Ticket: {ticket.id}{Style.RESET_ALL}")
    lines.append(f"{Fore.YELLOW}Title: {ticket.title}{Style.RESET_ALL}")
    lines.append("")
    
    # Basic info
    lines.append(f"Status: {ticket.status}")
    lines.append(f"Priority: {ticket.priority}")
    if ticket.assignee:
        lines.append(f"Assignee: {ticket.assignee}")
    lines.append(f"Reporter: {ticket.reporter} <{ticket.reporter_email}>")
    
    if ticket.labels:
        lines.append(f"Labels: {', '.join(ticket.labels)}")
    
    lines.append(f"Created: {ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Updated: {ticket.updated_at.strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Age: {ticket.age_days} days")
    
    if ticket.branch:
        lines.append(f"Branch: {ticket.branch}")
    if ticket.commit:
        lines.append(f"Commit: {ticket.commit}")
    
    lines.append("")
    
    # Description
    if ticket.description.strip():
        lines.append(f"{Fore.GREEN}Description:{Style.RESET_ALL}")
        lines.append(ticket.description)
        lines.append("")
    
    # Time tracking summary
    if ticket.time_logs or ticket.estimated_hours:
        lines.append(f"{Fore.GREEN}Time Tracking:{Style.RESET_ALL}")
        total_time = ticket.get_total_time_spent()
        lines.append(f"Total logged: {total_time:.1f}h")
        
        if ticket.estimated_hours:
            remaining = ticket.estimated_hours - total_time
            lines.append(f"Estimated: {ticket.estimated_hours}h | Remaining: {remaining:.1f}h")
        
        active_log = ticket.get_active_time_log()
        if active_log:
            current_duration = (datetime.now() - active_log.start_time).total_seconds() / 3600
            lines.append(f"{Fore.YELLOW}Active session: {current_duration:.1f}h{Style.RESET_ALL}")
        
        lines.append("")
    
    # Journal Entries
    if ticket.journal_entries:
        lines.append(f"{Fore.GREEN}Journal Entries:{Style.RESET_ALL}")
        lines.append("")
        for entry in ticket.journal_entries:
            lines.append(f"  {Fore.YELLOW}#{entry.id} - {entry.entry_type.upper()} by {entry.author}{Style.RESET_ALL}")
            lines.append(f"  {entry.created_at.strftime('%Y-%m-%d %H:%M')}")
            
            # Show performance metrics if available
            metrics = []
            if entry.effort_estimate_hours:
                metrics.append(f"Est: {entry.effort_estimate_hours}h")
            if entry.effort_spent_hours:
                metrics.append(f"Spent: {entry.effort_spent_hours}h")
            if entry.completion_percentage is not None:
                metrics.append(f"Complete: {entry.completion_percentage}%")
            if entry.milestone:
                metrics.append(f"Milestone: {entry.milestone}")
            
            if metrics:
                lines.append(f"  📊 {' | '.join(metrics)}")
            
            if entry.dependencies:
                lines.append(f"  🔗 Dependencies: {', '.join(entry.dependencies)}")
            if entry.risks:
                lines.append(f"  ⚠️ Risks: {', '.join(entry.risks)}")
            if entry.decisions:
                lines.append(f"  ✅ Decisions: {', '.join(entry.decisions)}")
            
            lines.append("")
            # Indent entry content
            for line in entry.content.split('\n'):
                lines.append(f"  {line}")
            lines.append("")
    
    # Comments
    if ticket.comments:
        lines.append(f"{Fore.GREEN}Comments:{Style.RESET_ALL}")
        lines.append("")
        for comment in ticket.comments:
            lines.append(f"  {Fore.YELLOW}#{comment.id} by {comment.author} <{comment.email}>{Style.RESET_ALL}")
            lines.append(f"  {comment.created_at.strftime('%Y-%m-%d %H:%M')}")
            lines.append("")
            # Indent comment content
            for line in comment.content.split('\n'):
                lines.append(f"  {line}")
            lines.append("")
    
    # Time logs (last 5)
    if ticket.time_logs:
        lines.append(f"{Fore.GREEN}Recent Time Logs:{Style.RESET_ALL}")
        for log in ticket.time_logs[-5:]:
            status = "[ACTIVE]" if log.is_active else f"{log.duration_hours:.1f}h"
            desc = f" - {log.description}" if log.description else ""
            lines.append(f"  {log.start_time.strftime('%Y-%m-%d %H:%M')} | {status} | {log.entry_type}{desc}")
        lines.append("")
    
    return "\n".join(lines)


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Repo Tickets - A CLI ticket system for git/hg/jj repositories."""
    pass


@main.command()
@click.option('--force', is_flag=True, help='Force initialization even if already exists')
def init(force):
    """Initialize tickets in the current repository."""
    try:
        storage = get_storage()
        storage.initialize(force=force)
        click.echo(f"{Fore.GREEN}✓ Tickets initialized successfully{Style.RESET_ALL}")
    except ValueError as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}", err=True)
        if not force:
            click.echo(f"Use --force to reinitialize", err=True)
        sys.exit(1)


@main.command()
@click.argument('title')
@click.option('--description', '-d', help='Ticket description')
@click.option('--priority', '-p', type=click.Choice(['critical', 'high', 'medium', 'low']), 
              default='medium', help='Ticket priority')
@click.option('--assignee', '-a', help='Assign ticket to user')
@click.option('--labels', '-l', help='Comma-separated labels')
@click.option('--estimate', '-e', type=float, help='Estimated effort in hours')
@click.option('--points', type=int, help='Story points for this ticket')
def create(title, description, priority, assignee, labels, estimate, points):
    """Create a new ticket."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    # Get VCS information
    vcs = detect_vcs()
    if vcs:
        reporter = vcs.get_user_name()
        reporter_email = vcs.get_user_email()
        branch = vcs.get_current_branch()
    else:
        reporter = os.getenv('USER', 'unknown')
        reporter_email = f"{reporter}@localhost"
        branch = ""
    
    # Parse labels
    label_list = []
    if labels:
        label_list = [label.strip() for label in labels.split(',') if label.strip()]
    
    # Generate unique ID
    ticket_id = storage.generate_unique_id(title)
    
    # Create ticket
    ticket = Ticket(
        id=ticket_id,
        title=title.strip(),
        description=description.strip() if description else "",
        priority=priority,
        assignee=assignee.strip() if assignee else None,
        reporter=reporter,
        reporter_email=reporter_email,
        labels=label_list,
        branch=branch,
        estimated_hours=estimate,
        story_points=points,
    )
    
    try:
        storage.save_ticket(ticket)
        click.echo(f"{Fore.GREEN}✓ Created ticket {ticket.id}: {ticket.title}{Style.RESET_ALL}")
        
        # Show estimation info if provided
        if estimate:
            click.echo(f"  📈 Estimated effort: {estimate}h")
        if points:
            click.echo(f"  🎯 Story points: {points}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error creating ticket: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@main.command()
@click.option('--status', '-s', help='Filter by status')
@click.option('--labels', '-l', help='Filter by labels (comma-separated)')
@click.option('--assignee', '-a', help='Filter by assignee')
@click.option('--all', '-A', is_flag=True, help='Show all tickets (including closed)')
def list(status, labels, assignee, all):
    """List tickets."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    # Parse labels filter
    label_list = []
    if labels:
        label_list = [label.strip() for label in labels.split(',') if label.strip()]
    
    # Get tickets
    if all:
        tickets = storage.list_tickets(labels=label_list)
    else:
        # Default to showing only open tickets
        tickets = storage.list_tickets(status=status or 'open', labels=label_list)
    
    # Apply assignee filter
    if assignee:
        tickets = [t for t in tickets if t.assignee == assignee]
    
    if not tickets:
        click.echo("No tickets found.")
        return
    
    # Format for table display
    headers = ["ID", "Title", "Status", "Priority", "Labels", "Age", "Assignee"]
    rows = [format_ticket_short(ticket) for ticket in tickets]
    
    table = tabulate(rows, headers=headers, tablefmt="grid")
    click.echo(table)
    
    # Show summary
    total = len(tickets)
    open_tickets = len([t for t in tickets if t.is_open])
    click.echo(f"\n{total} tickets ({open_tickets} open)")


@main.command()
@click.argument('ticket_id')
def show(ticket_id):
    """Show detailed information about a ticket."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    ticket = storage.load_ticket(ticket_id.upper())
    if not ticket:
        click.echo(f"{Fore.RED}Error: Ticket {ticket_id} not found{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    click.echo(format_ticket_full(ticket))


@main.command()
@click.argument('ticket_id')
@click.option('--title', '-t', help='Update ticket title')
@click.option('--description', '-d', help='Update ticket description')
@click.option('--status', '-s', type=click.Choice(['open', 'in-progress', 'blocked', 'closed', 'cancelled']),
              help='Update ticket status')
@click.option('--priority', '-p', type=click.Choice(['critical', 'high', 'medium', 'low']),
              help='Update ticket priority')
@click.option('--assignee', '-a', help='Update ticket assignee')
@click.option('--labels', '-l', help='Update labels (comma-separated)')
@click.option('--estimate', '-e', type=float, help='Update estimated effort in hours')
@click.option('--points', type=int, help='Update story points')
def update(ticket_id, title, description, status, priority, assignee, labels, estimate, points):
    """Update a ticket."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    ticket = storage.load_ticket(ticket_id.upper())
    if not ticket:
        click.echo(f"{Fore.RED}Error: Ticket {ticket_id} not found{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    # Prepare updates
    updates = {}
    if title is not None:
        updates['title'] = title.strip()
    if description is not None:
        updates['description'] = description.strip()
    if status is not None:
        updates['status'] = status
    if priority is not None:
        updates['priority'] = priority
    if assignee is not None:
        updates['assignee'] = assignee.strip() if assignee.strip() else None
    if labels is not None:
        updates['labels'] = [label.strip() for label in labels.split(',') if label.strip()]
    if estimate is not None:
        updates['estimated_hours'] = estimate
    if points is not None:
        updates['story_points'] = points
    
    if not updates:
        click.echo("No updates specified.")
        return
    
    try:
        ticket.update(**updates)
        storage.save_ticket(ticket)
        click.echo(f"{Fore.GREEN}✓ Updated ticket {ticket.id}{Style.RESET_ALL}")
        
        # Show what was updated
        for key, value in updates.items():
            click.echo(f"  {key}: {value}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error updating ticket: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@main.command()
@click.argument('ticket_id')
def close(ticket_id):
    """Close a ticket."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    ticket = storage.load_ticket(ticket_id.upper())
    if not ticket:
        click.echo(f"{Fore.RED}Error: Ticket {ticket_id} not found{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    if ticket.status == 'closed':
        click.echo(f"Ticket {ticket.id} is already closed.")
        return
    
    try:
        ticket.update(status='closed')
        storage.save_ticket(ticket)
        click.echo(f"{Fore.GREEN}✓ Closed ticket {ticket.id}: {ticket.title}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Error closing ticket: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@main.command()
@click.argument('query')
def search(query):
    """Search tickets by text query."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    tickets = storage.search_tickets(query)
    
    if not tickets:
        click.echo(f"No tickets found matching '{query}'.")
        return
    
    # Format for table display
    headers = ["ID", "Title", "Status", "Priority", "Labels", "Age", "Assignee"]
    rows = [format_ticket_short(ticket) for ticket in tickets]
    
    table = tabulate(rows, headers=headers, tablefmt="grid")
    click.echo(table)
    
    click.echo(f"\n{len(tickets)} tickets found matching '{query}'")


@main.command()
@click.argument('ticket_id')
@click.argument('comment')
def comment(ticket_id, comment):
    """Add a comment to a ticket."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    ticket = storage.load_ticket(ticket_id.upper())
    if not ticket:
        click.echo(f"{Fore.RED}Error: Ticket {ticket_id} not found{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    # Get VCS information
    vcs = detect_vcs()
    if vcs:
        author = vcs.get_user_name()
        email = vcs.get_user_email()
    else:
        author = os.getenv('USER', 'unknown')
        email = f"{author}@localhost"
    
    try:
        new_comment = ticket.add_comment(author, email, comment.strip())
        storage.save_ticket(ticket)
        click.echo(f"{Fore.GREEN}✓ Added comment {new_comment.id} to ticket {ticket.id}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Error adding comment: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@main.command()
def stats():
    """Show ticket statistics."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    stats_data = storage.get_stats()
    
    click.echo(f"{Fore.CYAN}Ticket Statistics{Style.RESET_ALL}")
    click.echo(f"Total: {stats_data['total']}")
    click.echo(f"Open: {Fore.GREEN}{stats_data['open']}{Style.RESET_ALL}")
    click.echo(f"In Progress: {Fore.YELLOW}{stats_data['in_progress']}{Style.RESET_ALL}")
    click.echo(f"Blocked: {Fore.RED}{stats_data['blocked']}{Style.RESET_ALL}")
    click.echo(f"Closed: {Fore.BLUE}{stats_data['closed']}{Style.RESET_ALL}")
    click.echo(f"Cancelled: {Fore.MAGENTA}{stats_data['cancelled']}{Style.RESET_ALL}")


@main.command()
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--edit', is_flag=True, help='Edit configuration file')
@click.option('--reset', is_flag=True, help='Reset to default configuration')
def config(show, edit, reset):
    """Manage ticket system configuration."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    if reset:
        # Reset to default configuration
        from .models import TicketConfig
        default_config = TicketConfig()
        default_config.save_to_file(storage.config_path)
        click.echo(f"{Fore.GREEN}✓ Configuration reset to defaults{Style.RESET_ALL}")
        return
    
    if edit:
        # Open configuration file in editor
        editor = os.getenv('EDITOR', 'vi')
        try:
            os.system(f"{editor} {storage.config_path}")
            click.echo(f"{Fore.GREEN}✓ Configuration file edited{Style.RESET_ALL}")
        except Exception as e:
            click.echo(f"{Fore.RED}Error opening editor: {e}{Style.RESET_ALL}", err=True)
        return
    
    # Show configuration (default behavior)
    config_data = storage.config
    
    click.echo(f"{Fore.CYAN}Current Configuration:{Style.RESET_ALL}")
    click.echo(f"Config file: {storage.config_path}")
    click.echo("")
    click.echo(f"Default status: {config_data.default_status}")
    click.echo(f"Statuses: {', '.join(config_data.statuses)}")
    click.echo(f"Priorities: {', '.join(config_data.priorities)}")
    click.echo(f"Labels: {', '.join(config_data.labels)}")
    click.echo(f"ID prefix: {config_data.id_prefix}")


@main.command()
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: ticket_report.html)')
@click.option('--no-open', is_flag=True, help='Don\'t automatically open in browser')
def report(output, no_open):
    """Generate a comprehensive HTML report and open it in browser."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    try:
        # Generate report
        click.echo(f"{Fore.CYAN}🔄 Generating HTML report...{Style.RESET_ALL}")
        
        from pathlib import Path
        output_path = Path(output) if output else None
        
        generator = TicketReportGenerator(storage)
        report_path = generator.generate_html_report(output_path)
        
        click.echo(f"{Fore.GREEN}✅ Report generated successfully!{Style.RESET_ALL}")
        click.echo(f"📄 Report saved to: {report_path}")
        
        # Open in browser unless disabled
        if not no_open:
            click.echo(f"{Fore.CYAN}🌐 Opening report in browser...{Style.RESET_ALL}")
            
            if open_in_browser(report_path):
                click.echo(f"{Fore.GREEN}✓ Report opened in default browser{Style.RESET_ALL}")
            else:
                click.echo(f"{Fore.YELLOW}⚠️  Could not open browser automatically{Style.RESET_ALL}")
                click.echo(f"Please open: file://{report_path.resolve()}")
        else:
            click.echo(f"To view the report, open: file://{report_path.resolve()}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error generating report: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@main.command()
@click.argument('ticket_id')
@click.argument('content')
@click.option('--type', '-t', 'entry_type', default='progress', 
              type=click.Choice(['progress', 'blocker', 'milestone', 'decision', 'risk', 'meeting']),
              help='Type of journal entry')
@click.option('--estimate', '-e', type=float, help='Effort estimate in hours')
@click.option('--spent', '-s', type=float, help='Effort spent in hours')
@click.option('--completion', '-c', type=click.IntRange(0, 100), help='Completion percentage (0-100)')
@click.option('--milestone', '-m', help='Milestone name')
@click.option('--dependencies', '-d', help='Comma-separated list of dependent ticket IDs')
@click.option('--risks', '-r', help='Comma-separated list of risks')
def journal(ticket_id, content, entry_type, estimate, spent, completion, milestone, dependencies, risks):
    """Add a journal entry with PM tracking to a ticket."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    ticket = storage.load_ticket(ticket_id.upper())
    if not ticket:
        click.echo(f"{Fore.RED}Error: Ticket {ticket_id} not found{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    # Get VCS information
    vcs = detect_vcs()
    if vcs:
        author = vcs.get_user_name()
        email = vcs.get_user_email()
    else:
        author = os.getenv('USER', 'unknown')
        email = f"{author}@localhost"
    
    try:
        # Prepare journal entry kwargs
        journal_kwargs = {}
        if estimate is not None:
            journal_kwargs['effort_estimate_hours'] = estimate
        if spent is not None:
            journal_kwargs['effort_spent_hours'] = spent
        if completion is not None:
            journal_kwargs['completion_percentage'] = completion
        if milestone:
            journal_kwargs['milestone'] = milestone
        if dependencies:
            journal_kwargs['dependencies'] = [dep.strip().upper() for dep in dependencies.split(',') if dep.strip()]
        if risks:
            journal_kwargs['risks'] = [risk.strip() for risk in risks.split(',') if risk.strip()]
        
        new_entry = ticket.add_journal_entry(
            author, email, content.strip(), entry_type, **journal_kwargs
        )
        storage.save_ticket(ticket)
        
        click.echo(f"{Fore.GREEN}✓ Added {entry_type} journal entry {new_entry.id} to ticket {ticket.id}{Style.RESET_ALL}")
        
        # Show summary of what was recorded
        if estimate:
            click.echo(f"  📈 Estimated effort: {estimate}h")
        if spent:
            click.echo(f"  ⏱️ Time spent: {spent}h")
        if completion is not None:
            click.echo(f"  📊 Completion: {completion}%")
        if milestone:
            click.echo(f"  🎯 Milestone: {milestone}")
        if dependencies:
            click.echo(f"  🔗 Dependencies: {', '.join(journal_kwargs['dependencies'])}")
        if risks:
            click.echo(f"  ⚠️ Risks: {', '.join(journal_kwargs['risks'])}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error adding journal entry: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@main.command()
@click.argument('ticket_id')
@click.option('--start', '-s', is_flag=True, help='Start time tracking')
@click.option('--stop', '-t', is_flag=True, help='Stop time tracking')
@click.option('--add', '-a', type=int, help='Add completed time in minutes')
@click.option('--type', 'entry_type', default='work',
              type=click.Choice(['work', 'meeting', 'research', 'blocked', 'review', 'testing', 'documentation', 'other']),
              help='Type of work being tracked')
@click.option('--description', '-d', help='Description of work performed')
def time(ticket_id, start, stop, add, entry_type, description):
    """Track time spent on a ticket."""
    storage = get_storage()
    
    if not storage.is_initialized():
        click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    ticket = storage.load_ticket(ticket_id.upper())
    if not ticket:
        click.echo(f"{Fore.RED}Error: Ticket {ticket_id} not found{Style.RESET_ALL}", err=True)
        sys.exit(1)
    
    # Get VCS information
    vcs = detect_vcs()
    if vcs:
        author = vcs.get_user_name()
    else:
        author = os.getenv('USER', 'unknown')
    
    try:
        if start:
            # Start time tracking
            active_log = ticket.get_active_time_log()
            if active_log:
                click.echo(f"{Fore.YELLOW}Warning: Already tracking time for this ticket (session {active_log.id}){Style.RESET_ALL}")
                click.echo(f"Use --stop first to end the current session")
                return
            
            time_log = ticket.start_time_tracking(
                author, description or "", entry_type
            )
            storage.save_ticket(ticket)
            
            click.echo(f"{Fore.GREEN}⏱️ Started time tracking for {ticket.id} (session {time_log.id}){Style.RESET_ALL}")
            if description:
                click.echo(f"  📝 {description}")
            click.echo(f"  🏷️ Type: {entry_type}")
            
        elif stop:
            # Stop time tracking
            stopped_log = ticket.stop_time_tracking()
            if not stopped_log:
                click.echo(f"{Fore.YELLOW}No active time tracking session found for {ticket.id}{Style.RESET_ALL}")
                return
            
            storage.save_ticket(ticket)
            
            click.echo(f"{Fore.GREEN}✓ Stopped time tracking for {ticket.id}{Style.RESET_ALL}")
            click.echo(f"  ⏱️ Duration: {stopped_log.duration_hours:.1f}h ({stopped_log.duration_minutes}m)")
            if stopped_log.description:
                click.echo(f"  📝 {stopped_log.description}")
            
        elif add is not None:
            # Add completed time
            if add <= 0:
                click.echo(f"{Fore.RED}Error: Duration must be positive{Style.RESET_ALL}", err=True)
                return
            
            time_log = ticket.add_time_log(
                author, add, description or "", entry_type
            )
            storage.save_ticket(ticket)
            
            hours = add / 60
            click.echo(f"{Fore.GREEN}✓ Added {hours:.1f}h ({add}m) to {ticket.id}{Style.RESET_ALL}")
            if description:
                click.echo(f"  📝 {description}")
            click.echo(f"  🏷️ Type: {entry_type}")
            
        else:
            # Show time tracking summary
            active_log = ticket.get_active_time_log()
            total_time = ticket.get_total_time_spent()
            
            click.echo(f"{Fore.CYAN}Time Tracking Summary for {ticket.id}{Style.RESET_ALL}")
            click.echo(f"Total time logged: {total_time:.1f}h")
            
            if active_log:
                from datetime import datetime
                current_duration = (datetime.now() - active_log.start_time).total_seconds() / 3600
                click.echo(f"{Fore.YELLOW}⏱️ Active session: {current_duration:.1f}h (started {active_log.start_time.strftime('%H:%M')}){Style.RESET_ALL}")
            
            if ticket.estimated_hours:
                remaining = ticket.estimated_hours - total_time
                click.echo(f"📈 Estimated: {ticket.estimated_hours}h | Remaining: {remaining:.1f}h")
            
            # Show recent time logs
            if ticket.time_logs:
                click.echo(f"\n📅 Recent time logs:")
                for log in ticket.time_logs[-5:]:
                    status = "[ACTIVE]" if log.is_active else f"{log.duration_hours:.1f}h"
                    desc = f" - {log.description}" if log.description else ""
                    click.echo(f"  {log.start_time.strftime('%Y-%m-%d %H:%M')} | {status} | {log.entry_type}{desc}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error with time tracking: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@main.command()
@click.option('--update-readme', is_flag=True, help='Update README.md with ticket status summary')
@click.option('--generate-report', is_flag=True, help='Generate STATUS.md report file')
@click.option('--days', default=7, type=int, help='Number of days for recent activity (default: 7)')
@click.option('--format', 'output_format', default='summary', 
              type=click.Choice(['summary', 'detailed', 'json']), help='Output format')
def status(update_readme, generate_report, days, output_format):
    """Show project status and optionally update README or generate reports."""
    try:
        storage = get_storage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}❌ Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        # Get all tickets
        tickets = storage.list_tickets()
        
        if not tickets:
            click.echo(f"{Fore.YELLOW}No tickets found.{Style.RESET_ALL}")
            return
        
        # Calculate statistics
        total_tickets = len(tickets)
        open_tickets = [t for t in tickets if t.status == 'open']
        in_progress_tickets = [t for t in tickets if t.status == 'in-progress']
        closed_tickets = [t for t in tickets if t.status == 'closed']
        
        # Recent activity (tickets closed in last N days)
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_closed = [t for t in closed_tickets if t.updated_at >= cutoff_date]
        
        # Priority breakdown
        critical_tickets = [t for t in tickets if t.priority == 'critical' and t.status != 'closed']
        high_priority = [t for t in tickets if t.priority == 'high' and t.status != 'closed']
        
        # Agent statistics (if available)
        agent_stats = {}
        try:
            from .agents import AgentStorage
            agent_storage = AgentStorage()
            if agent_storage.is_initialized():
                agents = agent_storage.list_agents()
                agent_tasks = agent_storage.list_tasks()
                agent_stats = {
                    'total_agents': len(agents),
                    'active_agents': len([a for a in agents if a.status == 'active']),
                    'total_tasks': len(agent_tasks),
                    'active_tasks': len([t for t in agent_tasks if t.status in ['assigned', 'in_progress']])
                }
        except ImportError:
            pass
        
        # Generate summary
        summary_data = {
            'total_tickets': total_tickets,
            'open_tickets': len(open_tickets),
            'in_progress': len(in_progress_tickets),
            'closed_tickets': len(closed_tickets),
            'critical_open': len(critical_tickets),
            'high_priority_open': len(high_priority),
            'recent_closed': len(recent_closed),
            'recent_closed_list': [{'id': t.id, 'title': t.title, 'closed_at': t.updated_at.strftime('%Y-%m-%d')} for t in recent_closed],
            'agent_stats': agent_stats
        }
        
        # Output based on format
        if output_format == 'json':
            click.echo(json.dumps(summary_data, indent=2, default=str))
        elif output_format == 'detailed':
            _print_detailed_status(summary_data, tickets, days)
        else:
            _print_status_summary(summary_data, days)
        
        # Update README if requested
        if update_readme:
            _update_readme_status(summary_data)
        
        # Generate report file if requested
        if generate_report:
            _generate_status_report(summary_data, tickets, days)
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error generating status: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


def _print_status_summary(data, days):
    """Print a concise status summary."""
    click.echo(f"{Fore.CYAN}📊 Project Status Summary{Style.RESET_ALL}")
    click.echo(f"\n🎫 Tickets Overview:")
    click.echo(f"  Total: {data['total_tickets']}")
    click.echo(f"  📂 Open: {data['open_tickets']}")
    click.echo(f"  ⚡ In Progress: {data['in_progress']}")
    click.echo(f"  ✅ Closed: {data['closed_tickets']}")
    
    if data['critical_open'] > 0 or data['high_priority_open'] > 0:
        click.echo(f"\n🚨 Priority Items:")
        if data['critical_open'] > 0:
            click.echo(f"  🔴 Critical: {data['critical_open']}")
        if data['high_priority_open'] > 0:
            click.echo(f"  🟡 High: {data['high_priority_open']}")
    
    if data['recent_closed'] > 0:
        click.echo(f"\n🎉 Recent Progress ({days} days):")
        click.echo(f"  ✅ Closed: {data['recent_closed']} tickets")
        for ticket in data['recent_closed_list'][:5]:  # Show up to 5 recent
            click.echo(f"    • {ticket['id']}: {ticket['title'][:50]}{'...' if len(ticket['title']) > 50 else ''} ({ticket['closed_at']})")
        if len(data['recent_closed_list']) > 5:
            click.echo(f"    ... and {len(data['recent_closed_list']) - 5} more")
    
    if data['agent_stats']:
        click.echo(f"\n🤖 AI Agents:")
        click.echo(f"  Total: {data['agent_stats']['total_agents']}")
        click.echo(f"  Active: {data['agent_stats']['active_agents']}")
        click.echo(f"  Tasks: {data['agent_stats']['active_tasks']}/{data['agent_stats']['total_tasks']} active")


def _print_detailed_status(data, all_tickets, days):
    """Print detailed status information."""
    _print_status_summary(data, days)
    
    # Add detailed breakdowns
    open_tickets = [t for t in all_tickets if t.status == 'open']
    in_progress_tickets = [t for t in all_tickets if t.status == 'in-progress']
    
    if open_tickets:
        click.echo(f"\n{Fore.BLUE}📂 Open Tickets:{Style.RESET_ALL}")
        for ticket in open_tickets[:10]:  # Show up to 10
            priority_icon = {'critical': '🔴', 'high': '🟡', 'medium': '🟢', 'low': '⚪'}.get(ticket.priority, '⚪')
            click.echo(f"  {priority_icon} {ticket.id}: {ticket.title}")
        if len(open_tickets) > 10:
            click.echo(f"    ... and {len(open_tickets) - 10} more")
    
    if in_progress_tickets:
        click.echo(f"\n{Fore.YELLOW}⚡ In Progress:{Style.RESET_ALL}")
        for ticket in in_progress_tickets:
            assignee = f" ({ticket.assignee})" if ticket.assignee else ""
            click.echo(f"  ▶ {ticket.id}: {ticket.title}{assignee}")


def _update_readme_status(data):
    """Update README.md with status summary."""
    try:
        readme_path = Path.cwd() / "README.md"
        if not readme_path.exists():
            click.echo(f"{Fore.YELLOW}README.md not found, creating new one.{Style.RESET_ALL}")
            readme_content = "# Project\n\n"
        else:
            with open(readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        
        # Generate status section
        status_section = f"""## 📊 Project Status

<!-- AUTO-GENERATED STATUS - DO NOT EDIT MANUALLY -->
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Ticket Overview:**
- 🎫 Total: {data['total_tickets']}
- 📂 Open: {data['open_tickets']}
- ⚡ In Progress: {data['in_progress']}
- ✅ Closed: {data['closed_tickets']}
"""
        
        if data['critical_open'] > 0 or data['high_priority_open'] > 0:
            status_section += f"\n**Priority Items:**\n"
            if data['critical_open'] > 0:
                status_section += f"- 🔴 Critical: {data['critical_open']}\n"
            if data['high_priority_open'] > 0:
                status_section += f"- 🟡 High Priority: {data['high_priority_open']}\n"
        
        if data['recent_closed'] > 0:
            status_section += f"\n**Recent Progress:**\n"
            for ticket in data['recent_closed_list'][:3]:  # Show top 3 in README
                status_section += f"- ✅ {ticket['id']}: {ticket['title']} ({ticket['closed_at']})\n"
        
        if data['agent_stats']:
            status_section += f"\n**🤖 AI Agents:** {data['agent_stats']['active_agents']}/{data['agent_stats']['total_agents']} active, {data['agent_stats']['active_tasks']} active tasks\n"
        
        status_section += "\n<!-- END AUTO-GENERATED STATUS -->\n"
        
        # Update or insert status section
        status_pattern = r'## 📊 Project Status.*?<!-- END AUTO-GENERATED STATUS -->\n'
        if re.search(status_pattern, readme_content, re.DOTALL):
            # Update existing section
            readme_content = re.sub(status_pattern, status_section, readme_content, flags=re.DOTALL)
        else:
            # Insert after first heading or at beginning
            lines = readme_content.split('\n')
            insert_index = 1 if lines and lines[0].startswith('#') else 0
            lines.insert(insert_index, status_section)
            readme_content = '\n'.join(lines)
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        click.echo(f"{Fore.GREEN}✅ Updated README.md with status summary{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error updating README: {e}{Style.RESET_ALL}", err=True)


def _generate_status_report(data, all_tickets, days):
    """Generate detailed STATUS.md report."""
    try:
        status_path = Path.cwd() / "STATUS.md"
        
        # Generate comprehensive report
        report = f"""# Project Status Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Report Period:** Last {days} days

## 📊 Overview

| Metric | Count |
|--------|-------|
| Total Tickets | {data['total_tickets']} |
| Open | {data['open_tickets']} |
| In Progress | {data['in_progress']} |
| Closed | {data['closed_tickets']} |
| Critical (Open) | {data['critical_open']} |
| High Priority (Open) | {data['high_priority_open']} |
| Recently Closed | {data['recent_closed']} |
"""
        
        if data['agent_stats']:
            report += f"""\n## 🤖 AI Agent Status

| Metric | Count |
|--------|-------|
| Total Agents | {data['agent_stats']['total_agents']} |
| Active Agents | {data['agent_stats']['active_agents']} |
| Total Tasks | {data['agent_stats']['total_tasks']} |
| Active Tasks | {data['agent_stats']['active_tasks']} |
"""
        
        # Recent closed tickets section
        if data['recent_closed'] > 0:
            report += f"\n## 🎉 Recently Resolved ({days} days)\n\n"
            for ticket in data['recent_closed_list']:
                report += f"- **{ticket['id']}**: {ticket['title']} *(closed {ticket['closed_at']})*\n"
        
        # Open tickets by priority
        open_tickets = [t for t in all_tickets if t.status == 'open']
        if open_tickets:
            critical = [t for t in open_tickets if t.priority == 'critical']
            high = [t for t in open_tickets if t.priority == 'high']
            medium = [t for t in open_tickets if t.priority == 'medium']
            low = [t for t in open_tickets if t.priority == 'low']
            
            report += f"\n## 📂 Open Tickets by Priority\n\n"
            
            for priority, tickets, icon in [('Critical', critical, '🔴'), ('High', high, '🟡'), 
                                           ('Medium', medium, '🟢'), ('Low', low, '⚪')]:
                if tickets:
                    report += f"### {icon} {priority} Priority\n\n"
                    for ticket in tickets:
                        assignee = f" *@{ticket.assignee}*" if ticket.assignee else ""
                        labels = f" `{', '.join(ticket.labels)}`" if ticket.labels else ""
                        report += f"- **{ticket.id}**: {ticket.title}{assignee}{labels}\n"
                    report += "\n"
        
        # In progress tickets
        in_progress = [t for t in all_tickets if t.status == 'in-progress']
        if in_progress:
            report += f"## ⚡ In Progress\n\n"
            for ticket in in_progress:
                assignee = f" *@{ticket.assignee}*" if ticket.assignee else ""
                report += f"- **{ticket.id}**: {ticket.title}{assignee}\n"
        
        # Write report
        with open(status_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        click.echo(f"{Fore.GREEN}✅ Generated STATUS.md report{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error generating status report: {e}{Style.RESET_ALL}", err=True)


@main.command()
def tui():
    """Launch the interactive Terminal User Interface (TUI)."""
    try:
        storage = get_storage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}❌ Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        # Check if textual is available
        try:
            from .tui import run_tui
        except ImportError:
            click.echo(f"{Fore.RED}❌ TUI dependencies not installed. Please install with:{Style.RESET_ALL}")
            click.echo(f"   {Fore.CYAN}pip install textual rich{Style.RESET_ALL}")
            sys.exit(1)
        
        click.echo(f"{Fore.GREEN}🚀 Launching Repo Tickets TUI...{Style.RESET_ALL}")
        run_tui()
        
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.BLUE}👋 TUI closed by user.{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Error launching TUI: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


# AI Agent Management Commands

@main.group()
def agent():
    """🤖 Manage AI agents for ticket automation."""
    pass


@agent.command()
@click.option('--all', '-a', is_flag=True, help='Show all agents including inactive')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json', 'simple']), 
              help='Output format')
def list(all, output_format):
    """List available AI agents."""
    try:
        from .agents import AgentStorage
        from .models import AgentStatus
        
        storage = AgentStorage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        # Get agents
        if all:
            agents = storage.list_agents()
        else:
            agents = storage.list_agents(status=AgentStatus.ACTIVE.value)
        
        if not agents:
            click.echo(f"{Fore.YELLOW}No agents found.{Style.RESET_ALL}")
            return
        
        if output_format == 'json':
            import json
            data = [agent.to_dict() for agent in agents]
            click.echo(json.dumps(data, indent=2, default=str))
        elif output_format == 'simple':
            for agent in agents:
                status_color = Fore.GREEN if agent.status == 'active' else Fore.YELLOW
                click.echo(f"{agent.id}: {agent.name} ({status_color}{agent.status}{Style.RESET_ALL})")
        else:
            # Table format
            from tabulate import tabulate
            
            table_data = []
            for agent in agents:
                status_icon = {
                    'active': f"{Fore.GREEN}✓{Style.RESET_ALL}",
                    'inactive': f"{Fore.YELLOW}●{Style.RESET_ALL}",
                    'busy': f"{Fore.BLUE}▶{Style.RESET_ALL}",
                    'error': f"{Fore.RED}✗{Style.RESET_ALL}",
                    'maintenance': f"{Fore.MAGENTA}🔧{Style.RESET_ALL}"
                }.get(agent.status, agent.status)
                
                table_data.append([
                    agent.id,
                    agent.name,
                    agent.agent_type,
                    status_icon,
                    len(agent.active_tasks),
                    f"{agent.metrics.success_rate:.1%}",
                    agent.metrics.tasks_completed,
                    agent.created_at.strftime('%Y-%m-%d')
                ])
            
            headers = ['ID', 'Name', 'Type', 'Status', 'Tasks', 'Success', 'Completed', 'Created']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
            click.echo(f"\n{len(agents)} agents total")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error listing agents: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@agent.command()
@click.argument('name')
@click.option('--description', '-d', help='Agent description')
@click.option('--type', 'agent_type', default='general', 
              type=click.Choice(['developer', 'reviewer', 'tester', 'analyst', 'documenter', 'project_manager', 'general']),
              help='Agent type')
@click.option('--max-tasks', default=1, type=int, help='Maximum concurrent tasks')
@click.option('--endpoint', help='API endpoint for the agent')
@click.option('--model', help='AI model identifier')
def create(name, description, agent_type, max_tasks, endpoint, model):
    """Create a new AI agent."""
    try:
        from .agents import AgentStorage
        
        storage = AgentStorage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        # Create agent
        agent = storage.create_agent(
            name=name,
            description=description or f"AI agent for {agent_type} tasks",
            agent_type=agent_type,
            max_concurrent_tasks=max_tasks,
            endpoint=endpoint,
            model=model
        )
        
        click.echo(f"{Fore.GREEN}✓ Created agent {agent.id}: {agent.name}{Style.RESET_ALL}")
        click.echo(f"  Type: {agent.agent_type}")
        click.echo(f"  Max tasks: {agent.max_concurrent_tasks}")
        if agent.endpoint:
            click.echo(f"  Endpoint: {agent.endpoint}")
        if agent.model:
            click.echo(f"  Model: {agent.model}")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error creating agent: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@agent.command()
@click.argument('agent_id')
def show(agent_id):
    """Show detailed information about an agent."""
    try:
        from .agents import AgentStorage
        
        storage = AgentStorage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        agent = storage.load_agent(agent_id)
        if not agent:
            click.echo(f"{Fore.RED}Error: Agent {agent_id} not found{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        stats = storage.get_agent_stats(agent_id)
        
        # Agent info
        click.echo(f"{Fore.CYAN}Agent: {agent.name} ({agent.id}){Style.RESET_ALL}")
        click.echo(f"Type: {agent.agent_type}")
        click.echo(f"Status: {agent.status}")
        click.echo(f"Description: {agent.description or 'No description'}")
        click.echo(f"Created: {agent.created_at.strftime('%Y-%m-%d %H:%M')}")
        
        if agent.last_seen:
            click.echo(f"Last seen: {agent.last_seen.strftime('%Y-%m-%d %H:%M')}")
        
        # Configuration
        click.echo(f"\n{Fore.YELLOW}Configuration:{Style.RESET_ALL}")
        click.echo(f"Max concurrent tasks: {agent.max_concurrent_tasks}")
        if agent.preferred_task_types:
            click.echo(f"Preferred task types: {', '.join(agent.preferred_task_types)}")
        if agent.endpoint:
            click.echo(f"Endpoint: {agent.endpoint}")
        if agent.model:
            click.echo(f"Model: {agent.model}")
        
        # Capabilities
        if agent.capabilities:
            click.echo(f"\n{Fore.YELLOW}Capabilities:{Style.RESET_ALL}")
            for cap in agent.capabilities:
                status = "enabled" if cap.enabled else "disabled"
                click.echo(f"  • {cap.name}: {cap.confidence_level:.1%} confidence ({status})")
                if cap.description:
                    click.echo(f"    {cap.description}")
        
        # Performance metrics
        click.echo(f"\n{Fore.YELLOW}Performance Metrics:{Style.RESET_ALL}")
        click.echo(f"Total tasks: {stats['total_tasks']}")
        click.echo(f"Active tasks: {stats['active_tasks']}")
        click.echo(f"Completed: {stats['completed_tasks']}")
        click.echo(f"Failed: {stats['failed_tasks']}")
        click.echo(f"Success rate: {agent.metrics.success_rate:.1%}")
        
        if agent.metrics.total_execution_time_minutes > 0:
            hours = agent.metrics.total_execution_time_minutes / 60
            click.echo(f"Total execution time: {hours:.1f}h")
        
        # Task type breakdown
        if stats['task_types']:
            click.echo(f"\n{Fore.YELLOW}Task Type Breakdown:{Style.RESET_ALL}")
            for task_type, counts in stats['task_types'].items():
                success_rate = counts['completed'] / counts['total'] if counts['total'] > 0 else 0
                click.echo(f"  {task_type}: {counts['total']} total, {success_rate:.1%} success rate")
        
        # Recent tasks
        if stats['recent_tasks']:
            click.echo(f"\n{Fore.YELLOW}Recent Tasks:{Style.RESET_ALL}")
            for task in stats['recent_tasks'][:5]:
                status_color = {
                    'completed': Fore.GREEN,
                    'failed': Fore.RED,
                    'in_progress': Fore.BLUE,
                    'assigned': Fore.YELLOW
                }.get(task.status, '')
                click.echo(f"  {task.id}: {task.description[:50]}... ({status_color}{task.status}{Style.RESET_ALL})")
                
    except Exception as e:
        click.echo(f"{Fore.RED}Error showing agent: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@agent.command()
@click.argument('ticket_id')
@click.argument('agent_id')
@click.argument('task_type')
@click.argument('description')
@click.option('--priority', default='medium', type=click.Choice(['critical', 'high', 'medium', 'low']), 
              help='Task priority')
@click.option('--instructions', help='Detailed instructions for the task')
def assign(ticket_id, agent_id, task_type, description, priority, instructions):
    """Assign a task to an agent."""
    try:
        from .agents import AgentStorage
        
        storage = AgentStorage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        task = storage.assign_task(
            ticket_id=ticket_id.upper(),
            agent_id=agent_id,
            task_type=task_type,
            description=description,
            priority=priority,
            instructions=instructions or ""
        )
        
        click.echo(f"{Fore.GREEN}✓ Assigned task {task.id} to agent {agent_id}{Style.RESET_ALL}")
        click.echo(f"  Ticket: {task.ticket_id}")
        click.echo(f"  Type: {task.task_type}")
        click.echo(f"  Priority: {task.priority}")
        click.echo(f"  Description: {task.description}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error assigning task: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@agent.command()
@click.argument('ticket_id')
@click.argument('task_type')
@click.argument('description')
@click.option('--priority', default='medium', type=click.Choice(['critical', 'high', 'medium', 'low']),
              help='Task priority')
def auto_assign(ticket_id, task_type, description, priority):
    """Automatically assign a task to the best available agent."""
    try:
        from .agents import AgentStorage
        
        storage = AgentStorage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        task = storage.auto_assign_task(
            ticket_id=ticket_id.upper(),
            task_type=task_type,
            description=description,
            priority=priority
        )
        
        if task:
            click.echo(f"{Fore.GREEN}✓ Auto-assigned task {task.id} to agent {task.agent_id}{Style.RESET_ALL}")
            click.echo(f"  Ticket: {task.ticket_id}")
            click.echo(f"  Type: {task.task_type}")
            click.echo(f"  Description: {task.description}")
        else:
            click.echo(f"{Fore.YELLOW}No available agents found for task type: {task_type}{Style.RESET_ALL}")
            click.echo("Consider creating an agent or checking agent availability.")
        
    except Exception as e:
        click.echo(f"{Fore.RED}Error auto-assigning task: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


@agent.command()
@click.option('--agent', help='Filter by agent ID')
@click.option('--ticket', help='Filter by ticket ID')
@click.option('--status', help='Filter by task status')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']),
              help='Output format')
def tasks(agent, ticket, status, output_format):
    """List agent tasks."""
    try:
        from .agents import AgentStorage
        
        storage = AgentStorage()
        if not storage.is_initialized():
            click.echo(f"{Fore.RED}Error: Tickets not initialized. Run 'tickets init' first.{Style.RESET_ALL}", err=True)
            sys.exit(1)
        
        tasks = storage.list_tasks(
            agent_id=agent,
            ticket_id=ticket.upper() if ticket else None,
            status=status
        )
        
        if not tasks:
            click.echo(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
            return
        
        if output_format == 'json':
            import json
            data = [task.__dict__ for task in tasks]
            # Convert datetime objects to strings for JSON serialization
            for task_data in data:
                for key, value in task_data.items():
                    if hasattr(value, 'isoformat'):
                        task_data[key] = value.isoformat()
            click.echo(json.dumps(data, indent=2, default=str))
        else:
            # Table format
            from tabulate import tabulate
            
            table_data = []
            for task in tasks:
                status_icon = {
                    'assigned': f"{Fore.YELLOW}●{Style.RESET_ALL}",
                    'in_progress': f"{Fore.BLUE}▶{Style.RESET_ALL}", 
                    'completed': f"{Fore.GREEN}✓{Style.RESET_ALL}",
                    'failed': f"{Fore.RED}✗{Style.RESET_ALL}",
                    'cancelled': f"{Fore.MAGENTA}■{Style.RESET_ALL}"
                }.get(task.status, task.status)
                
                duration = f"{task.duration_minutes}m" if task.duration_minutes else "-"
                description = task.description[:50] + "..." if len(task.description) > 50 else task.description
                
                table_data.append([
                    task.id,
                    task.ticket_id,
                    task.agent_id,
                    task.task_type,
                    description,
                    status_icon,
                    task.priority,
                    duration,
                    task.assigned_at.strftime('%m-%d %H:%M')
                ])
            
            headers = ['Task ID', 'Ticket', 'Agent', 'Type', 'Description', 'Status', 'Priority', 'Duration', 'Assigned']
            click.echo(tabulate(table_data, headers=headers, tablefmt='grid'))
            click.echo(f"\n{len(tasks)} tasks total")
            
    except Exception as e:
        click.echo(f"{Fore.RED}Error listing tasks: {e}{Style.RESET_ALL}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
