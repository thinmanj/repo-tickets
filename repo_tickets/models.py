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
    
    # AI Agent support
    assigned_agent: Optional[str] = None  # Agent ID
    agent_tasks: List[str] = field(default_factory=list)  # Task IDs
    
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
            'blocked_by', 'blocks', 'related_to', 'assigned_agent', 'agent_tasks'
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
    
    # Agent-related methods
    
    def assign_agent(self, agent_id: str) -> None:
        """Assign an AI agent to this ticket."""
        self.assigned_agent = agent_id
        self.updated_at = datetime.now()
    
    def unassign_agent(self) -> None:
        """Remove agent assignment from this ticket."""
        self.assigned_agent = None
        self.updated_at = datetime.now()
    
    def add_agent_task(self, task_id: str) -> None:
        """Add an agent task to this ticket."""
        if task_id not in self.agent_tasks:
            self.agent_tasks.append(task_id)
            self.updated_at = datetime.now()
    
    def remove_agent_task(self, task_id: str) -> None:
        """Remove an agent task from this ticket."""
        if task_id in self.agent_tasks:
            self.agent_tasks.remove(task_id)
            self.updated_at = datetime.now()
    
    @property
    def has_agent(self) -> bool:
        """Check if this ticket has an assigned agent."""
        return self.assigned_agent is not None
    
    @property
    def has_active_agent_tasks(self) -> bool:
        """Check if this ticket has active agent tasks."""
        return len(self.agent_tasks) > 0


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


# AI Agent Support

class AgentStatus(Enum):
    """Status of AI agents."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentType(Enum):
    """Types of AI agents."""
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    ANALYST = "analyst"
    DOCUMENTER = "documenter"
    PROJECT_MANAGER = "project_manager"
    GENERAL = "general"


class AgentTaskStatus(Enum):
    """Status of agent-assigned tasks."""
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


@dataclass
class AgentCapability:
    """Capability definition for an AI agent."""
    name: str
    description: str
    confidence_level: float  # 0.0 to 1.0
    enabled: bool = True
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate capability data."""
        if not 0.0 <= self.confidence_level <= 1.0:
            raise ValueError("Confidence level must be between 0.0 and 1.0")


@dataclass
class AgentMetrics:
    """Performance metrics for an AI agent."""
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time_minutes: int = 0
    average_response_time_seconds: float = 0.0
    success_rate: float = 0.0
    last_activity: Optional[datetime] = None
    
    def update_success_rate(self):
        """Recalculate success rate based on completed vs failed tasks."""
        total_tasks = self.tasks_completed + self.tasks_failed
        if total_tasks > 0:
            self.success_rate = self.tasks_completed / total_tasks
        else:
            self.success_rate = 0.0


@dataclass
class AgentTask:
    """A task assigned to an AI agent."""
    id: str
    ticket_id: str
    agent_id: str
    task_type: str  # 'code', 'review', 'test', 'document', 'analyze'
    description: str
    status: str = AgentTaskStatus.ASSIGNED.value
    priority: str = "medium"
    
    # Task execution data
    assigned_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Task specification
    instructions: str = ""
    expected_output: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    output: str = ""
    artifacts: List[str] = field(default_factory=list)  # Files, URLs, etc.
    error_message: str = ""
    
    # Performance tracking
    estimated_duration_minutes: Optional[int] = None
    actual_duration_minutes: Optional[int] = None
    
    def __post_init__(self):
        """Validate task data."""
        if not self.description.strip():
            raise ValueError("Task description cannot be empty")
    
    def start_task(self) -> None:
        """Mark task as started."""
        if self.status != AgentTaskStatus.ASSIGNED.value:
            raise ValueError(f"Cannot start task in {self.status} status")
        
        self.status = AgentTaskStatus.IN_PROGRESS.value
        self.started_at = datetime.now()
    
    def complete_task(self, output: str = "", artifacts: List[str] = None) -> None:
        """Mark task as completed."""
        if self.status != AgentTaskStatus.IN_PROGRESS.value:
            raise ValueError(f"Cannot complete task in {self.status} status")
        
        self.status = AgentTaskStatus.COMPLETED.value
        self.completed_at = datetime.now()
        self.output = output
        
        if artifacts:
            self.artifacts = artifacts
        
        # Calculate actual duration
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.actual_duration_minutes = int(delta.total_seconds() / 60)
    
    def fail_task(self, error_message: str) -> None:
        """Mark task as failed."""
        self.status = AgentTaskStatus.FAILED.value
        self.completed_at = datetime.now()
        self.error_message = error_message
        
        # Calculate actual duration
        if self.started_at:
            delta = self.completed_at - self.started_at
            self.actual_duration_minutes = int(delta.total_seconds() / 60)
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Get task duration in minutes."""
        if self.actual_duration_minutes is not None:
            return self.actual_duration_minutes
        
        if self.started_at:
            end_time = self.completed_at or datetime.now()
            delta = end_time - self.started_at
            return int(delta.total_seconds() / 60)
        
        return None


@dataclass
class Agent:
    """An AI agent that can work on tickets."""
    id: str
    name: str
    description: str = ""
    agent_type: str = AgentType.GENERAL.value
    status: str = AgentStatus.ACTIVE.value
    
    # Agent configuration
    capabilities: List[AgentCapability] = field(default_factory=list)
    max_concurrent_tasks: int = 1
    preferred_task_types: List[str] = field(default_factory=list)
    
    # Connection information
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_seen: Optional[datetime] = None
    
    # Performance tracking
    metrics: AgentMetrics = field(default_factory=AgentMetrics)
    
    # Current assignments
    active_tasks: List[str] = field(default_factory=list)  # Task IDs
    
    def __post_init__(self):
        """Validate agent data."""
        if not self.name.strip():
            raise ValueError("Agent name cannot be empty")
        
        if not self.id.strip():
            raise ValueError("Agent ID cannot be empty")
        
        # Validate agent type
        valid_types = [t.value for t in AgentType]
        if self.agent_type not in valid_types:
            raise ValueError(f"Invalid agent type: {self.agent_type}. Must be one of: {valid_types}")
        
        # Validate status
        valid_statuses = [s.value for s in AgentStatus]
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: {valid_statuses}")
    
    def add_capability(self, name: str, description: str, confidence: float, **kwargs) -> AgentCapability:
        """Add a capability to the agent."""
        capability = AgentCapability(
            name=name,
            description=description,
            confidence_level=confidence,
            **kwargs
        )
        self.capabilities.append(capability)
        self.updated_at = datetime.now()
        return capability
    
    def remove_capability(self, name: str) -> bool:
        """Remove a capability by name."""
        original_count = len(self.capabilities)
        self.capabilities = [c for c in self.capabilities if c.name != name]
        
        if len(self.capabilities) < original_count:
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_capability(self, name: str) -> Optional[AgentCapability]:
        """Get a capability by name."""
        return next((c for c in self.capabilities if c.name == name), None)
    
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        if self.status != AgentStatus.ACTIVE.value:
            return False
        
        return len(self.active_tasks) < self.max_concurrent_tasks
    
    def can_handle_task(self, task_type: str) -> bool:
        """Check if agent can handle a specific task type."""
        if not self.preferred_task_types:
            return True  # Agent can handle any task type
        
        return task_type in self.preferred_task_types
    
    def assign_task(self, task_id: str) -> None:
        """Assign a task to this agent."""
        if not self.is_available():
            raise ValueError(f"Agent {self.name} is not available for new tasks")
        
        if task_id not in self.active_tasks:
            self.active_tasks.append(task_id)
            self.updated_at = datetime.now()
    
    def unassign_task(self, task_id: str) -> None:
        """Remove a task assignment from this agent."""
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)
            self.updated_at = datetime.now()
    
    def update_status(self, status: str) -> None:
        """Update agent status."""
        valid_statuses = [s.value for s in AgentStatus]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of: {valid_statuses}")
        
        self.status = status
        self.updated_at = datetime.now()
        self.last_seen = datetime.now()
    
    def ping(self) -> None:
        """Update last seen timestamp."""
        self.last_seen = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for serialization."""
        data = asdict(self)
        
        # Convert datetime objects to ISO strings
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        
        if self.last_seen:
            data['last_seen'] = self.last_seen.isoformat()
        
        if self.metrics.last_activity:
            data['metrics']['last_activity'] = self.metrics.last_activity.isoformat()
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create agent from dictionary."""
        # Convert ISO strings back to datetime objects
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if data.get('last_seen') and isinstance(data['last_seen'], str):
            data['last_seen'] = datetime.fromisoformat(data['last_seen'])
        
        # Process metrics field
        if 'metrics' in data:
            # Convert datetime fields if present
            if data['metrics'].get('last_activity') and isinstance(data['metrics']['last_activity'], str):
                data['metrics']['last_activity'] = datetime.fromisoformat(data['metrics']['last_activity'])
            
            # Always reconstruct AgentMetrics object
            data['metrics'] = AgentMetrics(**data['metrics'])
        
        # Reconstruct AgentCapability objects
        if 'capabilities' in data:
            capabilities = []
            for cap_data in data['capabilities']:
                capabilities.append(AgentCapability(**cap_data))
            data['capabilities'] = capabilities
        
        return cls(**data)


def generate_agent_id(name: str, existing_ids: Set[str]) -> str:
    """
    Generate a unique agent ID based on the name.
    
    Args:
        name: The agent name
        existing_ids: Set of existing agent IDs to avoid duplicates
        
    Returns:
        A unique agent ID in format AGENT-NAME or AGENT-NAME-N
    """
    # Clean up name for ID
    clean_name = re.sub(r'[^a-zA-Z0-9]', '-', name.upper())
    clean_name = re.sub(r'-+', '-', clean_name).strip('-')[:16]
    
    if not clean_name:
        clean_name = "AGENT"
    
    base_id = f"AGENT-{clean_name}"
    if base_id not in existing_ids:
        return base_id
    
    # Find the next available number
    counter = 1
    while True:
        agent_id = f"{base_id}-{counter}"
        if agent_id not in existing_ids:
            return agent_id
        counter += 1
