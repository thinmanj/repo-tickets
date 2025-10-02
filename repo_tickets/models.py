#!/usr/bin/env python3
"""
Ticket data models for repo-tickets.

Defines the structure and validation for tickets and related objects.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

import yaml


class JournalEntryType(Enum):
    """Types of journal entries for tickets."""
    WORK = "work"  # Time spent working
    MEETING = "meeting"  # Time in meetings
    RESEARCH = "research"  # Research and investigation
    BLOCKED = "blocked"  # Time spent blocked
    REVIEW = "review"  # Code/design review time
    TESTING = "testing"  # Testing and QA time
    DOCUMENTATION = "documentation"  # Documentation work
    OTHER = "other"  # Other activities


@dataclass
class TimeLog:
    """Time tracking entry for a ticket."""
    id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None  # If end_time not set
    description: str = ""
    entry_type: str = JournalEntryType.WORK.value
    author: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate and calculate duration."""
        if self.end_time and self.start_time:
            # Calculate duration from start/end times
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)
        elif not self.duration_minutes and self.end_time is not None:
            # If end_time is explicitly set but duration not calculated
            raise ValueError("Either end_time or duration_minutes must be provided")
        # Allow active sessions where both end_time and duration_minutes are None
    
    @property
    def duration_hours(self) -> float:
        """Get duration in hours."""
        return self.duration_minutes / 60 if self.duration_minutes else 0.0
    
    @property
    def is_active(self) -> bool:
        """Check if this is an active time tracking session."""
        return self.end_time is None and self.duration_minutes is None


@dataclass
class JournalEntry:
    """A journal entry for project management tracking."""
    id: str
    author: str
    email: str
    content: str
    entry_type: str  # progress, blocker, milestone, decision, etc.
    created_at: datetime = field(default_factory=datetime.now)
    
    # Performance metrics
    effort_estimate_hours: Optional[float] = None  # Original estimate
    effort_spent_hours: Optional[float] = None  # Actual time spent
    completion_percentage: Optional[int] = None  # 0-100%
    
    # PM tracking
    milestone: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)  # Ticket IDs
    risks: List[str] = field(default_factory=list)  # Risk descriptions
    decisions: List[str] = field(default_factory=list)  # Key decisions made
    
    def __post_init__(self):
        """Validate journal entry data."""
        if not self.content.strip():
            raise ValueError("Journal entry content cannot be empty")
        
        # Validate completion percentage
        if self.completion_percentage is not None:
            if not 0 <= self.completion_percentage <= 100:
                raise ValueError("Completion percentage must be between 0 and 100")
        
        # Validate effort values
        if self.effort_estimate_hours is not None and self.effort_estimate_hours < 0:
            raise ValueError("Effort estimate cannot be negative")
        if self.effort_spent_hours is not None and self.effort_spent_hours < 0:
            raise ValueError("Effort spent cannot be negative")


@dataclass
class Comment:
    """A comment on a ticket."""
    id: str
    author: str
    email: str
    content: str
    created_at: datetime
    
    def __post_init__(self):
        """Validate comment data after initialization."""
        if not self.content.strip():
            raise ValueError("Comment content cannot be empty")


@dataclass 
class Ticket:
    """A ticket in the system."""
    id: str
    title: str
    description: str = ""
    status: str = "open"
    priority: str = "medium"
    assignee: Optional[str] = None
    reporter: str = ""
    reporter_email: str = ""
    labels: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    comments: List[Comment] = field(default_factory=list)
    
    # Metadata
    branch: str = ""
    commit: Optional[str] = None
    
    # PM and Performance Tracking
    journal_entries: List[JournalEntry] = field(default_factory=list)
    time_logs: List[TimeLog] = field(default_factory=list)
    
    # Effort tracking
    estimated_hours: Optional[float] = None
    story_points: Optional[int] = None
    
    # Dependencies and relationships
    blocked_by: List[str] = field(default_factory=list)  # Ticket IDs
    blocks: List[str] = field(default_factory=list)  # Ticket IDs
    related_to: List[str] = field(default_factory=list)  # Ticket IDs
    
    def __post_init__(self):
        """Validate ticket data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate ticket data."""
        if not self.title.strip():
            raise ValueError("Ticket title cannot be empty")
        
        if not self.id:
            raise ValueError("Ticket ID cannot be empty")
        
        # Validate ID format (should be uppercase alphanumeric with dashes)
        if not re.match(r'^[A-Z0-9-]+$', self.id):
            raise ValueError(f"Invalid ticket ID format: {self.id}")
        
        # Validate status
        valid_statuses = {"open", "in-progress", "blocked", "closed", "cancelled"}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: {valid_statuses}")
        
        # Validate priority
        valid_priorities = {"critical", "high", "medium", "low"}
        if self.priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {self.priority}. Must be one of: {valid_priorities}")
        
        # Clean up labels - remove duplicates and empty strings
        self.labels = list(set(label.strip() for label in self.labels if label.strip()))
    
    def add_comment(self, author: str, email: str, content: str) -> Comment:
        """Add a comment to the ticket."""
        comment = Comment(
            id=str(uuid.uuid4())[:8],
            author=author,
            email=email,
            content=content.strip(),
            created_at=datetime.now()
        )
        self.comments.append(comment)
        self.updated_at = datetime.now()
        return comment
    
    def add_journal_entry(
        self, 
        author: str, 
        email: str, 
        content: str, 
        entry_type: str = "progress",
        **kwargs
    ) -> JournalEntry:
        """Add a journal entry to the ticket."""
        entry = JournalEntry(
            id=str(uuid.uuid4())[:8],
            author=author,
            email=email,
            content=content.strip(),
            entry_type=entry_type,
            created_at=datetime.now(),
            **kwargs
        )
        self.journal_entries.append(entry)
        self.updated_at = datetime.now()
        return entry
    
    def start_time_tracking(
        self,
        author: str,
        description: str = "",
        entry_type: str = JournalEntryType.WORK.value
    ) -> TimeLog:
        """Start a time tracking session."""
        # Stop any existing active sessions
        self.stop_active_time_tracking()
        
        time_log = TimeLog(
            id=str(uuid.uuid4())[:8],
            start_time=datetime.now(),
            description=description,
            entry_type=entry_type,
            author=author
        )
        # Set duration to None to indicate active session
        time_log.duration_minutes = None
        time_log.end_time = None
        
        self.time_logs.append(time_log)
        self.updated_at = datetime.now()
        return time_log
    
    def stop_time_tracking(self, time_log_id: Optional[str] = None) -> Optional[TimeLog]:
        """Stop a time tracking session."""
        if time_log_id:
            # Stop specific session
            time_log = next((tl for tl in self.time_logs if tl.id == time_log_id), None)
        else:
            # Stop most recent active session
            time_log = self.get_active_time_log()
        
        if time_log and time_log.is_active:
            time_log.end_time = datetime.now()
            if time_log.start_time:
                delta = time_log.end_time - time_log.start_time
                time_log.duration_minutes = int(delta.total_seconds() / 60)
            self.updated_at = datetime.now()
            return time_log
        
        return None
    
    def stop_active_time_tracking(self) -> List[TimeLog]:
        """Stop all active time tracking sessions."""
        stopped_logs = []
        for time_log in self.time_logs:
            if time_log.is_active:
                self.stop_time_tracking(time_log.id)
                stopped_logs.append(time_log)
        return stopped_logs
    
    def add_time_log(
        self,
        author: str,
        duration_minutes: int,
        description: str = "",
        entry_type: str = JournalEntryType.WORK.value
    ) -> TimeLog:
        """Add a completed time log entry."""
        time_log = TimeLog(
            id=str(uuid.uuid4())[:8],
            start_time=datetime.now() - timedelta(minutes=duration_minutes),
            end_time=datetime.now(),
            duration_minutes=duration_minutes,
            description=description,
            entry_type=entry_type,
            author=author
        )
        self.time_logs.append(time_log)
        self.updated_at = datetime.now()
        return time_log
    
    def get_active_time_log(self) -> Optional[TimeLog]:
        """Get the current active time tracking session."""
        for time_log in reversed(self.time_logs):
            if time_log.is_active:
                return time_log
        return None
    
    def get_total_time_spent(self, entry_type: Optional[str] = None) -> float:
        """Get total time spent on this ticket in hours."""
        total_minutes = 0
        for time_log in self.time_logs:
            if entry_type is None or time_log.entry_type == entry_type:
                if time_log.duration_minutes:
                    total_minutes += time_log.duration_minutes
                elif time_log.is_active and time_log.start_time:
                    # Calculate current duration for active sessions
                    delta = datetime.now() - time_log.start_time
                    total_minutes += int(delta.total_seconds() / 60)
        
        return total_minutes / 60
    
    def update(self, **kwargs) -> None:
        """Update ticket fields."""
        allowed_fields = {
            'title', 'description', 'status', 'priority', 'assignee', 
            'labels', 'branch', 'commit', 'estimated_hours', 'story_points',
            'blocked_by', 'blocks', 'related_to'
        }
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(self, key, value)
        
        self.updated_at = datetime.now()
        self._validate()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ticket to dictionary for serialization."""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        
        # Convert comment datetimes
        for comment_data in data['comments']:
            if isinstance(comment_data['created_at'], datetime):
                comment_data['created_at'] = comment_data['created_at'].isoformat()
        
        # Convert journal entry datetimes
        for entry_data in data.get('journal_entries', []):
            if isinstance(entry_data['created_at'], datetime):
                entry_data['created_at'] = entry_data['created_at'].isoformat()
        
        # Convert time log datetimes
        for log_data in data.get('time_logs', []):
            if isinstance(log_data['start_time'], datetime):
                log_data['start_time'] = log_data['start_time'].isoformat()
            if log_data.get('end_time') and isinstance(log_data['end_time'], datetime):
                log_data['end_time'] = log_data['end_time'].isoformat()
            if isinstance(log_data['created_at'], datetime):
                log_data['created_at'] = log_data['created_at'].isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Ticket':
        """Create ticket from dictionary."""
        # Convert ISO strings back to datetime objects
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Convert comment datetimes
        comments = []
        for comment_data in data.get('comments', []):
            if isinstance(comment_data.get('created_at'), str):
                comment_data['created_at'] = datetime.fromisoformat(comment_data['created_at'])
            comments.append(Comment(**comment_data))
        data['comments'] = comments
        
        # Convert journal entries
        journal_entries = []
        for entry_data in data.get('journal_entries', []):
            if isinstance(entry_data.get('created_at'), str):
                entry_data['created_at'] = datetime.fromisoformat(entry_data['created_at'])
            journal_entries.append(JournalEntry(**entry_data))
        data['journal_entries'] = journal_entries
        
        # Convert time logs
        time_logs = []
        for log_data in data.get('time_logs', []):
            if isinstance(log_data.get('start_time'), str):
                log_data['start_time'] = datetime.fromisoformat(log_data['start_time'])
            if log_data.get('end_time') and isinstance(log_data['end_time'], str):
                log_data['end_time'] = datetime.fromisoformat(log_data['end_time'])
            if isinstance(log_data.get('created_at'), str):
                log_data['created_at'] = datetime.fromisoformat(log_data['created_at'])
            time_logs.append(TimeLog(**log_data))
        data['time_logs'] = time_logs
        
        return cls(**data)
    
    @property
    def age_days(self) -> int:
        """Get the age of the ticket in days."""
        return (datetime.now() - self.created_at).days
    
    @property
    def is_open(self) -> bool:
        """Check if ticket is in an open state."""
        return self.status not in {'closed', 'cancelled'}
    
    @property
    def label_set(self) -> Set[str]:
        """Get labels as a set for easier operations."""
        return set(self.labels)


def generate_ticket_id(title: str, existing_ids: Set[str]) -> str:
    """
    Generate a unique ticket ID based on the title.
    
    Args:
        title: The ticket title
        existing_ids: Set of existing ticket IDs to avoid duplicates
        
    Returns:
        A unique ticket ID in format TICKET-N or WORD-N
    """
    # Extract first meaningful word from title
    words = re.findall(r'\w+', title.upper())
    if words:
        prefix = words[0][:8]  # Max 8 chars
    else:
        prefix = "TICKET"
    
    # Find the next available number
    counter = 1
    while True:
        ticket_id = f"{prefix}-{counter}"
        if ticket_id not in existing_ids:
            return ticket_id
        counter += 1


@dataclass
class TicketConfig:
    """Configuration for the ticket system."""
    default_status: str = "open"
    statuses: List[str] = field(default_factory=lambda: ["open", "in-progress", "blocked", "closed", "cancelled"])
    priorities: List[str] = field(default_factory=lambda: ["critical", "high", "medium", "low"])
    labels: List[str] = field(default_factory=lambda: ["bug", "feature", "enhancement", "documentation", "urgent"])
    id_prefix: str = "TICKET"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TicketConfig':
        """Create config from dictionary."""
        return cls(**data)
    
    @classmethod
    def load_from_file(cls, config_path: Path) -> 'TicketConfig':
        """Load configuration from YAML file."""
        if not config_path.exists():
            return cls()  # Return default config
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return cls.from_dict(data)
        except (yaml.YAMLError, TypeError) as e:
            raise ValueError(f"Invalid configuration file: {e}")
    
    def save_to_file(self, config_path: Path) -> None:
        """Save configuration to YAML file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=True)


def validate_status(status: str, config: TicketConfig) -> None:
    """Validate that a status is allowed by the configuration."""
    if status not in config.statuses:
        raise ValueError(f"Invalid status '{status}'. Allowed: {', '.join(config.statuses)}")


def validate_priority(priority: str, config: TicketConfig) -> None:
    """Validate that a priority is allowed by the configuration.""" 
    if priority not in config.priorities:
        raise ValueError(f"Invalid priority '{priority}'. Allowed: {', '.join(config.priorities)}")


def validate_labels(labels: List[str], config: TicketConfig) -> None:
    """Validate that labels are allowed by the configuration (if configured)."""
    # If no labels configured, allow any labels
    if not config.labels:
        return
    
    invalid_labels = [label for label in labels if label not in config.labels]
    if invalid_labels:
        raise ValueError(f"Invalid labels: {', '.join(invalid_labels)}. Allowed: {', '.join(config.labels)}")