#!/usr/bin/env python3
"""
CLI interface for repo-tickets.

Provides command-line interface for managing tickets in repositories.
"""

import os
import sys
from datetime import datetime
from typing import List, Optional

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


if __name__ == '__main__':
    main()
