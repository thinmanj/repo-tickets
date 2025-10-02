#!/usr/bin/env python3
"""
Advanced TUI (Terminal User Interface) for repo-tickets.

Provides a modern, interactive terminal interface using the Textual framework.
"""

import os
from datetime import datetime
from typing import List, Optional, Any, Dict

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, DataTable, Static, Input, Button, Select, TextArea,
    TabbedContent, TabPane, Tree, ProgressBar, Rule, Label, Checkbox,
    RadioSet, RadioButton, Collapsible, RichLog
)
from textual.containers import Horizontal, Vertical, Container, ScrollableContainer
from textual.screen import Screen, ModalScreen
from textual.message import Message
from textual import on
from textual.reactive import reactive
from textual.binding import Binding
from rich.text import Text
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.markdown import Markdown

from .models import Ticket, JournalEntry, TimeLog, JournalEntryType
from .storage import TicketStorage
from .vcs import detect_vcs, VCSError


class TicketDetailScreen(ModalScreen[Optional[str]]):
    """Modal screen for displaying detailed ticket information."""
    
    BINDINGS = [
        Binding("j", "add_journal", "Journal"),
        Binding("t", "track_time", "Time"),
        Binding("e", "edit_ticket", "Edit"),
        Binding("c", "add_comment", "Comment"),
        Binding("escape", "close_detail", "Close"),
    ]
    
    CSS = """
    TicketDetailScreen {
        align: center middle;
    }
    
    #ticket_detail_dialog {
        width: 90%;
        height: 90%;
        border: thick $background 80%;
        background: $surface;
    }
    
    .ticket-header {
        background: $primary;
        color: $text;
        padding: 1;
        text-align: center;
    }
    
    .metric-box {
        border: round $accent;
        margin: 1;
        padding: 1;
    }
    """
    
    def __init__(self, ticket: Ticket, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticket = ticket
    
    def compose(self) -> ComposeResult:
        with Container(id="ticket_detail_dialog"):
            # Header
            yield Static(f"🎫 {self.ticket.id}: {self.ticket.title}", classes="ticket-header")
            
            with ScrollableContainer():
                # Basic Info
                with Horizontal():
                    with Vertical():
                        yield Static(f"Status: {self.ticket.status}")
                        yield Static(f"Priority: {self.ticket.priority}")
                        yield Static(f"Assignee: {self.ticket.assignee or 'Unassigned'}")
                    
                    with Vertical():
                        yield Static(f"Reporter: {self.ticket.reporter}")
                        yield Static(f"Created: {self.ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
                        yield Static(f"Age: {self.ticket.age_days} days")
                
                yield Rule("Description")
                yield Static(self.ticket.description or "No description")
                
                # Time Tracking
                if self.ticket.time_logs or self.ticket.estimated_hours:
                    yield Rule("⏱️ Time Tracking")
                    total_time = self.ticket.get_total_time_spent()
                    
                    with Horizontal():
                        yield Static(f"Total logged: {total_time:.1f}h", classes="metric-box")
                        if self.ticket.estimated_hours:
                            remaining = self.ticket.estimated_hours - total_time
                            yield Static(f"Estimated: {self.ticket.estimated_hours}h", classes="metric-box")
                            yield Static(f"Remaining: {remaining:.1f}h", classes="metric-box")
                    
                    active_log = self.ticket.get_active_time_log()
                    if active_log:
                        current_duration = (datetime.now() - active_log.start_time).total_seconds() / 3600
                        yield Static(f"🔄 Active session: {current_duration:.1f}h", classes="metric-box")
                
                # Journal Entries
                if self.ticket.journal_entries:
                    yield Rule("📝 Journal Entries")
                    for entry in self.ticket.journal_entries[-5:]:  # Show last 5
                        with Collapsible(title=f"{entry.entry_type.upper()} - {entry.created_at.strftime('%Y-%m-%d %H:%M')}"):
                            yield Static(entry.content)
                            if entry.completion_percentage is not None:
                                yield Static(f"Completion: {entry.completion_percentage}%")
                            if entry.milestone:
                                yield Static(f"Milestone: {entry.milestone}")
                            if entry.risks:
                                yield Static(f"Risks: {', '.join(entry.risks)}")
                
                # Comments
                if self.ticket.comments:
                    yield Rule("💬 Comments")
                    for comment in self.ticket.comments[-3:]:  # Show last 3
                        with Collapsible(title=f"{comment.author} - {comment.created_at.strftime('%Y-%m-%d %H:%M')}"):
                            yield Static(comment.content)
            
            with Horizontal():
                yield Button("Close", variant="primary", id="close_detail")
                yield Button("Edit Ticket", variant="success", id="edit_ticket")
                yield Button("Add Journal", variant="warning", id="add_journal")
                yield Button("Track Time", variant="error", id="track_time")
    
    @on(Button.Pressed, "#close_detail")
    def close_detail(self) -> None:
        self.dismiss(None)
    
    @on(Button.Pressed, "#edit_ticket")
    def edit_ticket(self) -> None:
        self.dismiss(f"edit:{self.ticket.id}")
    
    @on(Button.Pressed, "#add_journal")
    def add_journal(self) -> None:
        self.dismiss(f"journal:{self.ticket.id}")
    
    @on(Button.Pressed, "#track_time")
    def track_time(self) -> None:
        self.dismiss(f"time:{self.ticket.id}")
    
    # Keyboard action handlers
    def action_add_journal(self) -> None:
        """Add journal entry via keyboard shortcut."""
        self.dismiss(f"journal:{self.ticket.id}")
    
    def action_track_time(self) -> None:
        """Track time via keyboard shortcut."""
        self.dismiss(f"time:{self.ticket.id}")
    
    def action_edit_ticket(self) -> None:
        """Edit ticket via keyboard shortcut."""
        self.dismiss(f"edit:{self.ticket.id}")
    
    def action_add_comment(self) -> None:
        """Add comment via keyboard shortcut."""
        # For now, same as edit (placeholder)
        self.notify("💬 Comment feature coming soon!", severity="information")
    
    def action_close_detail(self) -> None:
        """Close detail screen via keyboard shortcut."""
        self.dismiss(None)


class CreateTicketScreen(ModalScreen[Optional[Dict]]):
    """Modal screen for creating new tickets."""
    
    CSS = """
    CreateTicketScreen {
        align: center middle;
    }
    
    #create_dialog {
        width: 80%;
        height: 85%;
        border: thick $background 80%;
        background: $surface;
    }
    
    .form-field {
        margin: 1;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container(id="create_dialog"):
            yield Static("🆕 Create New Ticket", classes="ticket-header")
            
            with ScrollableContainer():
                with Vertical():
                    yield Static("Title *", classes="form-field")
                    yield Input(placeholder="Enter ticket title...", id="title_input")
                    
                    yield Static("Description", classes="form-field")
                    yield TextArea(id="description_input")
                    
                    with Horizontal():
                        with Vertical():
                            yield Static("Priority", classes="form-field")
                            yield Select([
                                ("Critical", "critical"),
                                ("High", "high"),
                                ("Medium", "medium"),
                                ("Low", "low")
                            ], value="medium", id="priority_select")
                        
                        with Vertical():
                            yield Static("Assignee", classes="form-field")
                            yield Input(placeholder="Assign to...", id="assignee_input")
                    
                    with Horizontal():
                        with Vertical():
                            yield Static("Estimated Hours", classes="form-field")
                            yield Input(placeholder="0.0", id="estimate_input")
                        
                        with Vertical():
                            yield Static("Story Points", classes="form-field")
                            yield Input(placeholder="0", id="points_input")
                    
                    yield Static("Labels (comma-separated)", classes="form-field")
                    yield Input(placeholder="bug, feature, urgent...", id="labels_input")
            
            with Horizontal():
                yield Button("Cancel", variant="error", id="cancel_create")
                yield Button("Create Ticket", variant="primary", id="confirm_create")
    
    @on(Button.Pressed, "#cancel_create")
    def cancel_create(self) -> None:
        self.dismiss(None)
    
    @on(Button.Pressed, "#confirm_create")
    def confirm_create(self) -> None:
        # Gather form data
        title = self.query_one("#title_input", Input).value.strip()
        if not title:
            self.notify("Title is required!", severity="error")
            return
        
        data = {
            'title': title,
            'description': self.query_one("#description_input", TextArea).text,
            'priority': self.query_one("#priority_select", Select).value,
            'assignee': self.query_one("#assignee_input", Input).value.strip() or None,
            'labels': [l.strip() for l in self.query_one("#labels_input", Input).value.split(',') if l.strip()],
        }
        
        # Handle optional numeric fields
        try:
            estimate_text = self.query_one("#estimate_input", Input).value.strip()
            data['estimated_hours'] = float(estimate_text) if estimate_text else None
        except ValueError:
            data['estimated_hours'] = None
        
        try:
            points_text = self.query_one("#points_input", Input).value.strip()
            data['story_points'] = int(points_text) if points_text else None
        except ValueError:
            data['story_points'] = None
        
        self.dismiss(data)


class JournalEntryScreen(ModalScreen[Optional[Dict]]):
    """Modal screen for adding journal entries."""
    
    CSS = """
    JournalEntryScreen {
        align: center middle;
    }
    
    #journal_dialog {
        width: 80%;
        height: 80%;
        border: thick $background 80%;
        background: $surface;
    }
    """
    
    def __init__(self, ticket_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticket_id = ticket_id
    
    def compose(self) -> ComposeResult:
        with Container(id="journal_dialog"):
            yield Static(f"📝 Add Journal Entry - {self.ticket_id}", classes="ticket-header")
            
            with ScrollableContainer():
                with Vertical():
                    yield Static("Entry Type", classes="form-field")
                    yield Select([
                        ("Progress Update", "progress"),
                        ("Blocker", "blocker"),
                        ("Milestone", "milestone"),
                        ("Decision", "decision"),
                        ("Risk Assessment", "risk"),
                        ("Meeting Notes", "meeting")
                    ], value="progress", id="type_select")
                    
                    yield Static("Content *", classes="form-field")
                    yield TextArea(id="content_input")
                    
                    with Horizontal():
                        with Vertical():
                            yield Static("Hours Spent", classes="form-field")
                            yield Input(placeholder="0.0", id="spent_input")
                        
                        with Vertical():
                            yield Static("Completion %", classes="form-field")
                            yield Input(placeholder="0-100", id="completion_input")
                    
                    yield Static("Milestone", classes="form-field")
                    yield Input(placeholder="Milestone name...", id="milestone_input")
                    
                    yield Static("Dependencies (ticket IDs)", classes="form-field")
                    yield Input(placeholder="TICKET-1, TICKET-2...", id="deps_input")
                    
                    yield Static("Risks", classes="form-field")
                    yield Input(placeholder="Risk 1, Risk 2...", id="risks_input")
            
            with Horizontal():
                yield Button("Cancel", variant="error", id="cancel_journal")
                yield Button("Add Entry", variant="primary", id="confirm_journal")
    
    @on(Button.Pressed, "#cancel_journal")
    def cancel_journal(self) -> None:
        self.dismiss(None)
    
    @on(Button.Pressed, "#confirm_journal")
    def confirm_journal(self) -> None:
        content = self.query_one("#content_input", TextArea).text.strip()
        if not content:
            self.notify("Content is required!", severity="error")
            return
        
        data = {
            'ticket_id': self.ticket_id,
            'content': content,
            'entry_type': self.query_one("#type_select", Select).value,
        }
        
        # Optional fields
        spent_text = self.query_one("#spent_input", Input).value.strip()
        if spent_text:
            try:
                data['effort_spent_hours'] = float(spent_text)
            except ValueError:
                pass
        
        completion_text = self.query_one("#completion_input", Input).value.strip()
        if completion_text:
            try:
                completion = int(completion_text)
                if 0 <= completion <= 100:
                    data['completion_percentage'] = completion
            except ValueError:
                pass
        
        milestone = self.query_one("#milestone_input", Input).value.strip()
        if milestone:
            data['milestone'] = milestone
        
        deps = self.query_one("#deps_input", Input).value.strip()
        if deps:
            data['dependencies'] = [d.strip().upper() for d in deps.split(',') if d.strip()]
        
        risks = self.query_one("#risks_input", Input).value.strip()
        if risks:
            data['risks'] = [r.strip() for r in risks.split(',') if r.strip()]
        
        self.dismiss(data)


class TimeTrackingScreen(ModalScreen[Optional[Dict]]):
    """Modal screen for time tracking operations."""
    
    BINDINGS = [
        Binding("s", "start_session", "Start"),
        Binding("x", "stop_session", "Stop"),
        Binding("a", "add_time", "Add Time"),
        Binding("enter", "confirm_time", "Execute"),
        Binding("escape", "cancel_time", "Cancel"),
    ]
    
    CSS = """
    TimeTrackingScreen {
        align: center middle;
    }
    
    #time_dialog {
        width: 70%;
        height: 60%;
        border: thick $background 80%;
        background: $surface;
    }
    """
    
    def __init__(self, ticket_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticket_id = ticket_id
    
    def compose(self) -> ComposeResult:
        with Container(id="time_dialog"):
            yield Static(f"⏱️ Time Tracking - {self.ticket_id}", classes="ticket-header")
            
            with ScrollableContainer():
                with Vertical():
                    yield Static("Action", classes="form-field")
                    yield RadioSet(
                        RadioButton("Start new session", value="start"),
                        RadioButton("Stop current session", value="stop"),
                        RadioButton("Add completed time", value="add"),
                        id="action_radio"
                    )
                    
                    yield Static("Work Type", classes="form-field")
                    yield Select([
                        ("Work", "work"),
                        ("Meeting", "meeting"),
                        ("Research", "research"),
                        ("Blocked", "blocked"),
                        ("Review", "review"),
                        ("Testing", "testing"),
                        ("Documentation", "documentation"),
                        ("Other", "other")
                    ], value="work", id="work_type_select")
                    
                    yield Static("Description", classes="form-field")
                    yield Input(placeholder="What are you working on?", id="desc_input")
                    
                    yield Static("Minutes (for 'Add completed time')", classes="form-field")
                    yield Input(placeholder="120", id="minutes_input")
            
            with Horizontal():
                yield Button("Cancel", variant="error", id="cancel_time")
                yield Button("Execute", variant="primary", id="confirm_time")
    
    @on(Button.Pressed, "#cancel_time")
    def cancel_time(self) -> None:
        self.dismiss(None)
    
    @on(Button.Pressed, "#confirm_time")
    def confirm_time(self) -> None:
        action = self.query_one("#action_radio", RadioSet).pressed_button.label
        
        data = {
            'ticket_id': self.ticket_id,
            'action': action.lower().split()[0],  # 'start', 'stop', or 'add'
            'work_type': self.query_one("#work_type_select", Select).value,
            'description': self.query_one("#desc_input", Input).value.strip(),
        }
        
        if data['action'] == 'add':
            minutes_text = self.query_one("#minutes_input", Input).value.strip()
            if not minutes_text:
                self.notify("Minutes required for adding completed time!", severity="error")
                return
            try:
                data['minutes'] = int(minutes_text)
                if data['minutes'] <= 0:
                    self.notify("Minutes must be positive!", severity="error")
                    return
            except ValueError:
                self.notify("Invalid minutes value!", severity="error")
                return
        
        self.dismiss(data)
    
    # Keyboard action handlers
    def action_start_session(self) -> None:
        """Select start session via keyboard."""
        radio_set = self.query_one("#action_radio", RadioSet)
        radio_set.pressed_index = 0  # Start new session
    
    def action_stop_session(self) -> None:
        """Select stop session via keyboard."""
        radio_set = self.query_one("#action_radio", RadioSet)
        radio_set.pressed_index = 1  # Stop current session
    
    def action_add_time(self) -> None:
        """Select add completed time via keyboard."""
        radio_set = self.query_one("#action_radio", RadioSet)
        radio_set.pressed_index = 2  # Add completed time
        # Focus on minutes input
        minutes_input = self.query_one("#minutes_input", Input)
        minutes_input.focus()
    
    def action_confirm_time(self) -> None:
        """Execute time tracking operation via keyboard."""
        self.confirm_time()
    
    def action_cancel_time(self) -> None:
        """Cancel time tracking via keyboard."""
        self.dismiss(None)


class HelpScreen(ModalScreen):
    """Modal screen showing keyboard shortcuts and help information."""
    
    CSS = """
    HelpScreen {
        align: center middle;
    }
    
    #help_dialog {
        width: 80%;
        height: 85%;
        border: thick $background 80%;
        background: $surface;
    }
    
    .help-section {
        margin: 1;
    }
    
    .shortcut-list {
        margin: 0 2;
    }
    """
    
    def compose(self) -> ComposeResult:
        with Container(id="help_dialog"):
            yield Static("⌨️ Keyboard Shortcuts & Help", classes="ticket-header")
            
            with ScrollableContainer():
                yield Static("🚀 Main Interface", classes="help-section")
                yield Static("""• n / N          Create new ticket
• r / R          Refresh tickets list
• g / G          Generate HTML report
• / (slash)      Focus search box
• ?              Show this help screen
• q / Q          Quit application
• Esc            Close modals / clear search
• Enter          View selected ticket details
• ↑ ↓            Navigate ticket table
• Tab            Move focus between elements""", classes="shortcut-list")
                
                yield Static("🔍 Search & Filters", classes="help-section")
                yield Static("""• 1              Show all tickets
• 2              Show open tickets
• 3              Show in-progress tickets  
• 4              Show blocked tickets
• 5              Show closed tickets
• 6              Show critical priority
• 7              Show high priority
• Ctrl+L         Clear search""", classes="shortcut-list")
                
                yield Static("🎫 Ticket Actions (in detail view)", classes="help-section")
                yield Static("""• j / J          Add journal entry
• t / T          Time tracking
• e / E          Edit ticket (coming soon)
• c / C          Add comment (coming soon)
• Esc            Close ticket details""", classes="shortcut-list")
                
                yield Static("⏱️ Time Tracking", classes="help-section")
                yield Static("""• s / S          Start time session
• x / X          Stop time session  
• a / A          Add completed time
• Enter          Execute selected action
• Esc            Cancel operation""", classes="shortcut-list")
                
                yield Static("💡 Tips", classes="help-section")
                yield Static("""• Use mouse clicks for quick navigation
• Search works across titles, descriptions, and IDs
• Filters can be combined with search queries
• Metrics update automatically when tickets change
• Risk scores are calculated from blocked/stale tickets
• HTML reports open in your default browser
• All data syncs with CLI operations""", classes="shortcut-list")
                
                yield Static("🔧 Technical Info", classes="help-section")
                yield Static("""• Built with Textual framework
• Compatible with modern terminals
• Supports mouse interaction
• Cross-platform (Windows/Mac/Linux)
• Integrates with git/hg/jj repositories
• JSON storage backend""", classes="shortcut-list")
            
            with Horizontal():
                yield Button("Close Help", variant="primary", id="close_help")
    
    @on(Button.Pressed, "#close_help")
    def close_help(self) -> None:
        self.dismiss()


class RepoTicketsTUI(App):
    """Main TUI application for repo-tickets."""
    
    # Keyboard bindings
    BINDINGS = [
        Binding("n", "new_ticket", "New Ticket"),
        Binding("r", "refresh", "Refresh"),
        Binding("g", "generate_report", "Generate Report"),
        Binding("/", "focus_search", "Search"),
        Binding("?", "show_help", "Help"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "clear_or_back", "Clear/Back"),
        
        # Filter shortcuts
        Binding("1", "filter_all", "All"),
        Binding("2", "filter_open", "Open"),
        Binding("3", "filter_in_progress", "In Progress"),
        Binding("4", "filter_blocked", "Blocked"),
        Binding("5", "filter_closed", "Closed"),
        Binding("6", "filter_critical", "Critical"),
        Binding("7", "filter_high", "High"),
        
        # Search shortcuts
        Binding("ctrl+l", "clear_search", "Clear Search"),
    ]
    
    CSS = """
    .title {
        dock: top;
        height: 3;
        background: $primary;
        color: $text;
        content-align: center middle;
        text-style: bold;
    }
    
    .sidebar {
        dock: left;
        width: 25;
        background: $surface;
        border-right: thick $background 20%;
    }
    
    .main-content {
        background: $background;
    }
    
    .status-bar {
        dock: bottom;
        height: 3;
        background: $accent;
        color: $text;
    }
    
    .ticket-table {
        border: round $accent;
    }
    
    .metric-panel {
        height: 8;
        border: round $primary;
        margin: 1;
    }
    
    .action-buttons {
        dock: bottom;
        height: 3;
    }
    
    Button {
        margin: 0 1;
    }
    
    .search-box {
        margin: 1;
    }
    """
    
    TITLE = "🎫 Repo Tickets TUI"
    SUB_TITLE = "Terminal User Interface for Advanced Project Management"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.storage: Optional[TicketStorage] = None
        self.tickets: List[Ticket] = []
        self.filtered_tickets: List[Ticket] = []
        self.current_filter = "all"
        self.search_query = ""
    
    def on_mount(self) -> None:
        """Initialize the application."""
        try:
            self.storage = TicketStorage()
            if not self.storage.is_initialized():
                self.notify("❌ Tickets not initialized in this repository!", severity="error")
                self.exit(1)
            
            # Get VCS info
            vcs = detect_vcs()
            if vcs:
                self.sub_title = f"📁 {vcs.repo_root.name} ({type(vcs).__name__.replace('VCS', '')})"
            
            self.refresh_tickets()
            self.notify("🚀 Welcome to Repo Tickets TUI!", severity="information")
            
        except VCSError as e:
            self.notify(f"❌ {e}", severity="error")
            self.exit(1)
        except Exception as e:
            self.notify(f"❌ Error initializing: {e}", severity="error")
            self.exit(1)
    
    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header(show_clock=True)
        
        with Horizontal():
            # Sidebar
            with Vertical(classes="sidebar"):
                yield Static("🔍 Search & Filter", classes="title")
                
                with Container(classes="search-box"):
                    yield Input(placeholder="Search tickets...", id="search_input")
                
                yield Static("Filters:")
                yield Button("All Tickets", id="filter_all", variant="primary")
                yield Button("Open", id="filter_open")
                yield Button("In Progress", id="filter_in_progress")
                yield Button("Blocked", id="filter_blocked")
                yield Button("Closed", id="filter_closed")
                
                yield Static("Priority:")
                yield Button("Critical", id="filter_critical")
                yield Button("High", id="filter_high")
                
                yield Rule()
                yield Static("Actions:")
                yield Button("➕ New Ticket", id="new_ticket", variant="success")
                yield Button("🔄 Refresh", id="refresh", variant="warning")
                yield Button("📊 Generate Report", id="generate_report")
            
            # Main content
            with Vertical(classes="main-content"):
                # Metrics panel
                with Horizontal():
                    with Container(classes="metric-panel"):
                        yield Static("📊 Project Metrics", id="metrics_title")
                        yield Static("Loading...", id="metrics_content")
                    
                    with Container(classes="metric-panel"):
                        yield Static("⏱️ Time Tracking", id="time_title")
                        yield Static("Loading...", id="time_content")
                    
                    with Container(classes="metric-panel"):
                        yield Static("⚠️ Risk Assessment", id="risk_title")
                        yield Static("Loading...", id="risk_content")
                
                # Tickets table
                yield DataTable(id="tickets_table", classes="ticket-table")
        
        yield Footer()
    
    def refresh_tickets(self) -> None:
        """Refresh the tickets list and update the display."""
        if not self.storage:
            return
        
        self.tickets = self.storage.list_tickets()
        self.apply_filters()
        self.update_table()
        self.update_metrics()
    
    def apply_filters(self) -> None:
        """Apply current filters to the tickets list."""
        filtered = self.tickets
        
        # Apply status filter
        if self.current_filter != "all":
            if self.current_filter == "critical":
                filtered = [t for t in filtered if t.priority == "critical"]
            elif self.current_filter == "high":
                filtered = [t for t in filtered if t.priority == "high"]
            else:
                filtered = [t for t in filtered if t.status == self.current_filter]
        
        # Apply search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            filtered = [
                t for t in filtered
                if (query_lower in t.title.lower() or 
                    query_lower in t.description.lower() or
                    query_lower in t.id.lower())
            ]
        
        self.filtered_tickets = filtered
    
    def update_table(self) -> None:
        """Update the tickets table with current filtered tickets."""
        table = self.query_one("#tickets_table", DataTable)
        table.clear(columns=True)
        
        # Add columns
        table.add_columns("ID", "Title", "Status", "Priority", "Assignee", "Age", "Time")
        
        # Add rows
        for ticket in self.filtered_tickets:
            # Format status with emoji
            status_emoji = {
                'open': '🔵',
                'in-progress': '🟡',
                'blocked': '🔴',
                'closed': '✅',
                'cancelled': '❌'
            }
            status = f"{status_emoji.get(ticket.status, '⚪')} {ticket.status}"
            
            # Format priority with emoji
            priority_emoji = {
                'critical': '🔥',
                'high': '🟠',
                'medium': '🟢',
                'low': '🔵'
            }
            priority = f"{priority_emoji.get(ticket.priority, '⚪')} {ticket.priority}"
            
            # Calculate total time
            total_time = ticket.get_total_time_spent()
            time_str = f"{total_time:.1f}h" if total_time > 0 else "-"
            
            # Truncate title if too long
            title = ticket.title[:40] + "..." if len(ticket.title) > 40 else ticket.title
            
            table.add_row(
                ticket.id,
                title,
                status,
                priority,
                ticket.assignee or "Unassigned",
                f"{ticket.age_days}d",
                time_str,
                key=ticket.id
            )
    
    def update_metrics(self) -> None:
        """Update the metrics panels."""
        if not self.tickets:
            return
        
        # Project metrics
        total = len(self.tickets)
        open_tickets = len([t for t in self.tickets if t.is_open])
        closed = len([t for t in self.tickets if not t.is_open])
        completion_rate = (closed / total * 100) if total > 0 else 0
        
        metrics_text = f"""Total: {total}
Open: {open_tickets}
Closed: {closed}
Complete: {completion_rate:.1f}%"""
        
        self.query_one("#metrics_content", Static).update(metrics_text)
        
        # Time tracking metrics
        total_time = sum(t.get_total_time_spent() for t in self.tickets)
        estimated = sum(t.estimated_hours for t in self.tickets if t.estimated_hours)
        active_sessions = len([t for t in self.tickets if t.get_active_time_log()])
        
        time_text = f"""Logged: {total_time:.1f}h
Estimated: {estimated:.1f}h
Active: {active_sessions}
Remaining: {max(0, estimated - total_time):.1f}h"""
        
        self.query_one("#time_content", Static).update(time_text)
        
        # Risk assessment
        blocked = len([t for t in self.tickets if t.status == 'blocked'])
        critical_open = len([t for t in self.tickets if t.priority == 'critical' and t.is_open])
        stale = len([t for t in self.tickets if t.age_days > 30 and t.is_open])
        
        risk_score = min(100, blocked * 20 + critical_open * 15 + stale * 5)
        risk_level = "🟢 Low" if risk_score < 20 else "🟡 Medium" if risk_score < 50 else "🔴 High"
        
        risk_text = f"""Level: {risk_level}
Score: {risk_score}/100
Blocked: {blocked}
Stale: {stale}"""
        
        self.query_one("#risk_content", Static).update(risk_text)
    
    @on(Input.Changed, "#search_input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self.search_query = event.value
        self.apply_filters()
        self.update_table()
    
    @on(Button.Pressed)
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        
        # Filter buttons
        if button_id and button_id.startswith("filter_"):
            self.current_filter = button_id.replace("filter_", "").replace("_", "-")
            
            # Update button styles
            for btn in self.query("Button"):
                if btn.id and btn.id.startswith("filter_"):
                    btn.variant = "primary" if btn.id == button_id else "default"
            
            self.apply_filters()
            self.update_table()
        
        # Action buttons
        elif button_id == "new_ticket":
            self.push_screen(CreateTicketScreen(), self.handle_create_ticket)
        elif button_id == "refresh":
            self.refresh_tickets()
            self.notify("🔄 Tickets refreshed!", severity="information")
        elif button_id == "generate_report":
            self.generate_html_report()
    
    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle ticket selection."""
        ticket_id = event.row_key
        ticket = next((t for t in self.tickets if t.id == ticket_id), None)
        
        if ticket:
            self.push_screen(TicketDetailScreen(ticket), self.handle_ticket_action)
    
    def handle_create_ticket(self, result: Optional[Dict]) -> None:
        """Handle ticket creation result."""
        if not result or not self.storage:
            return
        
        try:
            # Get VCS info
            vcs = detect_vcs()
            if vcs:
                reporter = vcs.get_user_name()
                reporter_email = vcs.get_user_email()
                branch = vcs.get_current_branch()
            else:
                reporter = os.getenv('USER', 'unknown')
                reporter_email = f"{reporter}@localhost"
                branch = ""
            
            # Generate ID
            ticket_id = self.storage.generate_unique_id(result['title'])
            
            # Create ticket
            ticket = Ticket(
                id=ticket_id,
                title=result['title'],
                description=result['description'],
                priority=result['priority'],
                assignee=result['assignee'],
                reporter=reporter,
                reporter_email=reporter_email,
                labels=result['labels'],
                branch=branch,
                estimated_hours=result['estimated_hours'],
                story_points=result['story_points'],
            )
            
            self.storage.save_ticket(ticket)
            self.refresh_tickets()
            self.notify(f"✅ Created ticket {ticket_id}", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Error creating ticket: {e}", severity="error")
    
    def handle_ticket_action(self, result: Optional[str]) -> None:
        """Handle actions from ticket detail screen."""
        if not result:
            return
        
        action, ticket_id = result.split(':', 1)
        
        if action == "journal":
            self.push_screen(JournalEntryScreen(ticket_id), self.handle_journal_entry)
        elif action == "time":
            self.push_screen(TimeTrackingScreen(ticket_id), self.handle_time_tracking)
        elif action == "edit":
            # For now, just show a notification
            self.notify(f"✏️ Edit functionality coming soon for {ticket_id}", severity="information")
    
    def handle_journal_entry(self, result: Optional[Dict]) -> None:
        """Handle journal entry creation."""
        if not result or not self.storage:
            return
        
        try:
            ticket = self.storage.load_ticket(result['ticket_id'])
            if not ticket:
                self.notify("❌ Ticket not found!", severity="error")
                return
            
            # Get VCS info
            vcs = detect_vcs()
            if vcs:
                author = vcs.get_user_name()
                email = vcs.get_user_email()
            else:
                author = os.getenv('USER', 'unknown')
                email = f"{author}@localhost"
            
            # Create journal entry
            journal_kwargs = {k: v for k, v in result.items() if k not in ['ticket_id', 'content', 'entry_type']}
            
            entry = ticket.add_journal_entry(
                author, email, result['content'], result['entry_type'], **journal_kwargs
            )
            
            self.storage.save_ticket(ticket)
            self.refresh_tickets()
            self.notify(f"📝 Added {result['entry_type']} entry to {result['ticket_id']}", severity="success")
            
        except Exception as e:
            self.notify(f"❌ Error adding journal entry: {e}", severity="error")
    
    def handle_time_tracking(self, result: Optional[Dict]) -> None:
        """Handle time tracking operations."""
        if not result or not self.storage:
            return
        
        try:
            ticket = self.storage.load_ticket(result['ticket_id'])
            if not ticket:
                self.notify("❌ Ticket not found!", severity="error")
                return
            
            # Get VCS info
            vcs = detect_vcs()
            author = vcs.get_user_name() if vcs else os.getenv('USER', 'unknown')
            
            action = result['action']
            
            if action == 'start':
                time_log = ticket.start_time_tracking(
                    author, result['description'], result['work_type']
                )
                self.notify(f"⏱️ Started tracking time for {result['ticket_id']}", severity="success")
                
            elif action == 'stop':
                stopped = ticket.stop_time_tracking()
                if stopped:
                    self.notify(f"✅ Stopped tracking: {stopped.duration_hours:.1f}h", severity="success")
                else:
                    self.notify("❌ No active session found", severity="warning")
                    return
                    
            elif action == 'add':
                time_log = ticket.add_time_log(
                    author, result['minutes'], result['description'], result['work_type']
                )
                hours = result['minutes'] / 60
                self.notify(f"✅ Added {hours:.1f}h to {result['ticket_id']}", severity="success")
            
            self.storage.save_ticket(ticket)
            self.refresh_tickets()
            
        except Exception as e:
            self.notify(f"❌ Error with time tracking: {e}", severity="error")
    
    def generate_html_report(self) -> None:
        """Generate HTML report."""
        if not self.storage:
            return
        
        try:
            from .reports import TicketReportGenerator, open_in_browser
            from pathlib import Path
            
            generator = TicketReportGenerator(self.storage)
            report_path = generator.generate_html_report()
            
            if open_in_browser(report_path):
                self.notify(f"📊 Report generated and opened: {report_path.name}", severity="success")
            else:
                self.notify(f"📊 Report generated: {report_path}", severity="information")
                
        except Exception as e:
            self.notify(f"❌ Error generating report: {e}", severity="error")
    
    # Keyboard action handlers
    def action_new_ticket(self) -> None:
        """Create a new ticket via keyboard shortcut."""
        self.push_screen(CreateTicketScreen(), self.handle_create_ticket)
    
    def action_refresh(self) -> None:
        """Refresh tickets via keyboard shortcut."""
        self.refresh_tickets()
        self.notify("🔄 Tickets refreshed!", severity="information")
    
    def action_generate_report(self) -> None:
        """Generate HTML report via keyboard shortcut."""
        self.generate_html_report()
    
    def action_focus_search(self) -> None:
        """Focus the search input box."""
        search_input = self.query_one("#search_input", Input)
        search_input.focus()
    
    def action_show_help(self) -> None:
        """Show the help screen."""
        self.push_screen(HelpScreen())
    
    def action_clear_or_back(self) -> None:
        """Clear search or close modals."""
        search_input = self.query_one("#search_input", Input)
        if search_input.value:
            search_input.value = ""
            self.search_query = ""
            self.apply_filters()
            self.update_table()
            self.notify("Search cleared", severity="information")
    
    def action_clear_search(self) -> None:
        """Clear the search box."""
        search_input = self.query_one("#search_input", Input)
        search_input.value = ""
        search_input.focus()
        self.search_query = ""
        self.apply_filters()
        self.update_table()
        self.notify("Search cleared", severity="information")
    
    # Filter action handlers
    def action_filter_all(self) -> None:
        """Show all tickets."""
        self._set_filter("all", "filter_all")
    
    def action_filter_open(self) -> None:
        """Show open tickets."""
        self._set_filter("open", "filter_open")
    
    def action_filter_in_progress(self) -> None:
        """Show in-progress tickets."""
        self._set_filter("in-progress", "filter_in_progress")
    
    def action_filter_blocked(self) -> None:
        """Show blocked tickets."""
        self._set_filter("blocked", "filter_blocked")
    
    def action_filter_closed(self) -> None:
        """Show closed tickets."""
        self._set_filter("closed", "filter_closed")
    
    def action_filter_critical(self) -> None:
        """Show critical priority tickets."""
        self._set_filter("critical", "filter_critical")
    
    def action_filter_high(self) -> None:
        """Show high priority tickets."""
        self._set_filter("high", "filter_high")
    
    def _set_filter(self, filter_value: str, button_id: str) -> None:
        """Helper method to set filter and update button states."""
        self.current_filter = filter_value
        
        # Update button styles
        for btn in self.query("Button"):
            if btn.id and btn.id.startswith("filter_"):
                btn.variant = "primary" if btn.id == button_id else "default"
        
        self.apply_filters()
        self.update_table()
        
        # Show notification
        filter_name = filter_value.replace("-", " ").title()
        if filter_value == "all":
            filter_name = "All Tickets"
        count = len(self.filtered_tickets)
        self.notify(f"Showing {count} {filter_name.lower()} tickets", severity="information")


def run_tui():
    """Entry point for the TUI application."""
    app = RepoTicketsTUI()
    app.run()


if __name__ == "__main__":
    run_tui()