#!/usr/bin/env python3
"""
Ticket data models for repo-tickets.

Defines the structure and validation for tickets and related objects.
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Set, Union
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
class Requirement:
    """A requirement or user story for a ticket."""
    id: str
    title: str
    description: str = ""
    priority: str = "medium"  # critical, high, medium, low
    status: str = "draft"  # draft, approved, implemented, verified
    acceptance_criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    
    def __post_init__(self):
        """Validate requirement data."""
        if not self.title.strip():
            raise ValueError("Requirement title cannot be empty")
        
        # Validate priority
        valid_priorities = {"critical", "high", "medium", "low"}
        if self.priority not in valid_priorities:
            raise ValueError(f"Invalid priority: {self.priority}. Must be one of: {valid_priorities}")
        
        # Validate status
        valid_statuses = {"draft", "approved", "implemented", "verified"}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: {valid_statuses}")


@dataclass
class UserStory:
    """A user story with persona, goal, and benefit."""
    id: str
    persona: str  # As a [persona]
    goal: str  # I want [goal]
    benefit: str  # So that [benefit]
    priority: str = "medium"
    story_points: Optional[int] = None
    acceptance_criteria: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    
    def __post_init__(self):
        """Validate user story data."""
        if not self.persona.strip():
            raise ValueError("User story persona cannot be empty")
        if not self.goal.strip():
            raise ValueError("User story goal cannot be empty")
        if not self.benefit.strip():
            raise ValueError("User story benefit cannot be empty")
    
    @property
    def formatted_story(self) -> str:
        """Get the formatted user story."""
        return f"As a {self.persona}, I want {self.goal}, so that {self.benefit}."


@dataclass
class GherkinScenario:
    """A Gherkin-style acceptance test scenario."""
    id: str
    title: str
    background: str = ""  # Background steps (optional)
    given: List[str] = field(default_factory=list)  # Given steps
    when: List[str] = field(default_factory=list)  # When steps
    then: List[str] = field(default_factory=list)  # Then steps
    tags: List[str] = field(default_factory=list)  # @tags
    status: str = "draft"  # draft, ready, passing, failing, blocked
    created_at: datetime = field(default_factory=datetime.now)
    author: str = ""
    
    def __post_init__(self):
        """Validate Gherkin scenario data."""
        if not self.title.strip():
            raise ValueError("Scenario title cannot be empty")
        
        if not self.given and not self.when and not self.then:
            raise ValueError("Scenario must have at least one Given, When, or Then step")
        
        # Validate status
        valid_statuses = {"draft", "ready", "passing", "failing", "blocked"}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: {valid_statuses}")
    
    def to_gherkin_text(self) -> str:
        """Convert scenario to Gherkin text format."""
        lines = []
        
        # Add tags if present
        if self.tags:
            tag_line = " ".join(f"@{tag}" for tag in self.tags)
            lines.append(tag_line)
        
        # Add scenario title
        lines.append(f"Scenario: {self.title}")
        
        # Add background if present
        if self.background:
            lines.append("  Background:")
            for step in self.background.split('\n'):
                if step.strip():
                    lines.append(f"    {step.strip()}")
        
        # Add Given steps
        for i, step in enumerate(self.given):
            prefix = "  Given" if i == 0 else "  And"
            lines.append(f"{prefix} {step}")
        
        # Add When steps
        for i, step in enumerate(self.when):
            prefix = "  When" if i == 0 else "  And"
            lines.append(f"{prefix} {step}")
        
        # Add Then steps
        for i, step in enumerate(self.then):
            prefix = "  Then" if i == 0 else "  And"
            lines.append(f"{prefix} {step}")
        
        return "\n".join(lines)
    
    @classmethod
    def from_gherkin_text(cls, text: str, scenario_id: str = None, author: str = "") -> 'GherkinScenario':
        """Parse Gherkin text into a scenario object."""
        if scenario_id is None:
            scenario_id = str(uuid.uuid4())[:8]
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        title = ""
        background = ""
        given = []
        when = []
        then = []
        tags = []
        current_section = None
        
        for line in lines:
            # Parse tags
            if line.startswith('@'):
                tags.extend(tag[1:] for tag in line.split() if tag.startswith('@'))
            
            # Parse scenario title
            elif line.startswith('Scenario:'):
                title = line[9:].strip()
            
            # Parse background
            elif line.startswith('Background:'):
                current_section = 'background'
            
            # Parse Given/When/Then
            elif line.startswith('Given '):
                current_section = 'given'
                given.append(line[6:].strip())
            elif line.startswith('When '):
                current_section = 'when'
                when.append(line[5:].strip())
            elif line.startswith('Then '):
                current_section = 'then'
                then.append(line[5:].strip())
            elif line.startswith('And '):
                step = line[4:].strip()
                if current_section == 'background':
                    background += f"\n{step}" if background else step
                elif current_section == 'given':
                    given.append(step)
                elif current_section == 'when':
                    when.append(step)
                elif current_section == 'then':
                    then.append(step)
            elif current_section == 'background' and not line.startswith(('Given', 'When', 'Then', 'And')):
                background += f"\n{line}" if background else line
        
        return cls(
            id=scenario_id,
            title=title or "Untitled Scenario",
            background=background,
            given=given,
            when=when,
            then=then,
            tags=tags,
            author=author
        )


@dataclass
class ExpectedResult:
    """Expected result or outcome for a ticket."""
    id: str
    description: str
    success_criteria: List[str] = field(default_factory=list)
    verification_method: str = "manual"  # manual, automated, review
    status: str = "pending"  # pending, verified, failed, blocked
    created_at: datetime = field(default_factory=datetime.now)
    verified_at: Optional[datetime] = None
    verified_by: str = ""
    notes: str = ""
    
    def __post_init__(self):
        """Validate expected result data."""
        if not self.description.strip():
            raise ValueError("Expected result description cannot be empty")
        
        # Validate verification method
        valid_methods = {"manual", "automated", "review"}
        if self.verification_method not in valid_methods:
            raise ValueError(f"Invalid verification method: {self.verification_method}. Must be one of: {valid_methods}")
        
        # Validate status
        valid_statuses = {"pending", "verified", "failed", "blocked"}
        if self.status not in valid_statuses:
            raise ValueError(f"Invalid status: {self.status}. Must be one of: {valid_statuses}")
    
    def mark_verified(self, verified_by: str, notes: str = "") -> None:
        """Mark the expected result as verified."""
        self.status = "verified"
        self.verified_at = datetime.now()
        self.verified_by = verified_by
        if notes:
            self.notes = notes


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
    
    # Requirements and Acceptance Testing
    requirements: List[Requirement] = field(default_factory=list)
    user_stories: List[UserStory] = field(default_factory=list)
    expected_results: List[ExpectedResult] = field(default_factory=list)
    gherkin_scenarios: List[GherkinScenario] = field(default_factory=list)
    
    # Requirements metadata
    requirements_status: str = "draft"  # draft, review, approved, complete
    acceptance_criteria_met: bool = False
    test_coverage_percentage: Optional[float] = None
    
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
        
        # Validate requirements status
        valid_req_statuses = {"draft", "review", "approved", "complete"}
        if self.requirements_status not in valid_req_statuses:
            raise ValueError(f"Invalid requirements status: {self.requirements_status}. Must be one of: {valid_req_statuses}")
        
        # Validate test coverage percentage
        if self.test_coverage_percentage is not None:
            if not 0 <= self.test_coverage_percentage <= 100:
                raise ValueError("Test coverage percentage must be between 0 and 100")
        
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
            'blocked_by', 'blocks', 'related_to', 'assigned_agent', 'agent_tasks',
            'requirements_status', 'acceptance_criteria_met', 'test_coverage_percentage'
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
        
        # Convert requirement datetimes
        for req_data in data.get('requirements', []):
            if isinstance(req_data['created_at'], datetime):
                req_data['created_at'] = req_data['created_at'].isoformat()
            if isinstance(req_data['updated_at'], datetime):
                req_data['updated_at'] = req_data['updated_at'].isoformat()
        
        # Convert user story datetimes
        for story_data in data.get('user_stories', []):
            if isinstance(story_data['created_at'], datetime):
                story_data['created_at'] = story_data['created_at'].isoformat()
        
        # Convert expected result datetimes
        for result_data in data.get('expected_results', []):
            if isinstance(result_data['created_at'], datetime):
                result_data['created_at'] = result_data['created_at'].isoformat()
            if result_data.get('verified_at') and isinstance(result_data['verified_at'], datetime):
                result_data['verified_at'] = result_data['verified_at'].isoformat()
        
        # Convert Gherkin scenario datetimes
        for scenario_data in data.get('gherkin_scenarios', []):
            if isinstance(scenario_data['created_at'], datetime):
                scenario_data['created_at'] = scenario_data['created_at'].isoformat()
        
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
        
        # Convert requirements
        requirements = []
        for req_data in data.get('requirements', []):
            if isinstance(req_data.get('created_at'), str):
                req_data['created_at'] = datetime.fromisoformat(req_data['created_at'])
            if isinstance(req_data.get('updated_at'), str):
                req_data['updated_at'] = datetime.fromisoformat(req_data['updated_at'])
            requirements.append(Requirement(**req_data))
        data['requirements'] = requirements
        
        # Convert user stories
        user_stories = []
        for story_data in data.get('user_stories', []):
            if isinstance(story_data.get('created_at'), str):
                story_data['created_at'] = datetime.fromisoformat(story_data['created_at'])
            user_stories.append(UserStory(**story_data))
        data['user_stories'] = user_stories
        
        # Convert expected results
        expected_results = []
        for result_data in data.get('expected_results', []):
            if isinstance(result_data.get('created_at'), str):
                result_data['created_at'] = datetime.fromisoformat(result_data['created_at'])
            if result_data.get('verified_at') and isinstance(result_data['verified_at'], str):
                result_data['verified_at'] = datetime.fromisoformat(result_data['verified_at'])
            expected_results.append(ExpectedResult(**result_data))
        data['expected_results'] = expected_results
        
        # Convert Gherkin scenarios
        gherkin_scenarios = []
        for scenario_data in data.get('gherkin_scenarios', []):
            if isinstance(scenario_data.get('created_at'), str):
                scenario_data['created_at'] = datetime.fromisoformat(scenario_data['created_at'])
            gherkin_scenarios.append(GherkinScenario(**scenario_data))
        data['gherkin_scenarios'] = gherkin_scenarios
        
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
    
    # Requirement management methods
    
    def add_requirement(self, title: str, description: str = "", priority: str = "medium", 
                       acceptance_criteria: List[str] = None, author: str = "") -> Requirement:
        """Add a requirement to the ticket."""
        requirement = Requirement(
            id=str(uuid.uuid4())[:8],
            title=title,
            description=description,
            priority=priority,
            acceptance_criteria=acceptance_criteria or [],
            author=author
        )
        self.requirements.append(requirement)
        self.updated_at = datetime.now()
        return requirement
    
    def remove_requirement(self, requirement_id: str) -> bool:
        """Remove a requirement by ID."""
        original_count = len(self.requirements)
        self.requirements = [r for r in self.requirements if r.id != requirement_id]
        
        if len(self.requirements) < original_count:
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_requirement(self, requirement_id: str) -> Optional[Requirement]:
        """Get a requirement by ID."""
        return next((r for r in self.requirements if r.id == requirement_id), None)
    
    def add_user_story(self, persona: str, goal: str, benefit: str, priority: str = "medium",
                       story_points: Optional[int] = None, acceptance_criteria: List[str] = None,
                       author: str = "") -> UserStory:
        """Add a user story to the ticket."""
        story = UserStory(
            id=str(uuid.uuid4())[:8],
            persona=persona,
            goal=goal,
            benefit=benefit,
            priority=priority,
            story_points=story_points,
            acceptance_criteria=acceptance_criteria or [],
            author=author
        )
        self.user_stories.append(story)
        self.updated_at = datetime.now()
        return story
    
    def remove_user_story(self, story_id: str) -> bool:
        """Remove a user story by ID."""
        original_count = len(self.user_stories)
        self.user_stories = [s for s in self.user_stories if s.id != story_id]
        
        if len(self.user_stories) < original_count:
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_user_story(self, story_id: str) -> Optional[UserStory]:
        """Get a user story by ID."""
        return next((s for s in self.user_stories if s.id == story_id), None)
    
    def add_expected_result(self, description: str, success_criteria: List[str] = None,
                           verification_method: str = "manual") -> ExpectedResult:
        """Add an expected result to the ticket."""
        result = ExpectedResult(
            id=str(uuid.uuid4())[:8],
            description=description,
            success_criteria=success_criteria or [],
            verification_method=verification_method
        )
        self.expected_results.append(result)
        self.updated_at = datetime.now()
        return result
    
    def remove_expected_result(self, result_id: str) -> bool:
        """Remove an expected result by ID."""
        original_count = len(self.expected_results)
        self.expected_results = [r for r in self.expected_results if r.id != result_id]
        
        if len(self.expected_results) < original_count:
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_expected_result(self, result_id: str) -> Optional[ExpectedResult]:
        """Get an expected result by ID."""
        return next((r for r in self.expected_results if r.id == result_id), None)
    
    def add_gherkin_scenario(self, title: str, given: List[str] = None, when: List[str] = None,
                            then: List[str] = None, background: str = "", tags: List[str] = None,
                            author: str = "") -> GherkinScenario:
        """Add a Gherkin scenario to the ticket."""
        scenario = GherkinScenario(
            id=str(uuid.uuid4())[:8],
            title=title,
            background=background,
            given=given or [],
            when=when or [],
            then=then or [],
            tags=tags or [],
            author=author
        )
        self.gherkin_scenarios.append(scenario)
        self.updated_at = datetime.now()
        return scenario
    
    def add_gherkin_from_text(self, gherkin_text: str, author: str = "") -> GherkinScenario:
        """Add a Gherkin scenario from text format."""
        scenario = GherkinScenario.from_gherkin_text(gherkin_text, author=author)
        self.gherkin_scenarios.append(scenario)
        self.updated_at = datetime.now()
        return scenario
    
    def remove_gherkin_scenario(self, scenario_id: str) -> bool:
        """Remove a Gherkin scenario by ID."""
        original_count = len(self.gherkin_scenarios)
        self.gherkin_scenarios = [s for s in self.gherkin_scenarios if s.id != scenario_id]
        
        if len(self.gherkin_scenarios) < original_count:
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_gherkin_scenario(self, scenario_id: str) -> Optional[GherkinScenario]:
        """Get a Gherkin scenario by ID."""
        return next((s for s in self.gherkin_scenarios if s.id == scenario_id), None)
    
    # Requirements analysis properties and methods
    
    @property
    def requirements_count(self) -> int:
        """Get total number of requirements."""
        return len(self.requirements)
    
    @property
    def requirements_coverage(self) -> float:
        """Get percentage of requirements that are implemented or verified."""
        if not self.requirements:
            return 100.0
        
        covered = sum(1 for req in self.requirements if req.status in ['implemented', 'verified'])
        return (covered / len(self.requirements)) * 100
    
    @property
    def user_stories_count(self) -> int:
        """Get total number of user stories."""
        return len(self.user_stories)
    
    @property
    def total_story_points(self) -> int:
        """Get total story points for all user stories."""
        return sum(story.story_points or 0 for story in self.user_stories)
    
    @property
    def gherkin_scenarios_count(self) -> int:
        """Get total number of Gherkin scenarios."""
        return len(self.gherkin_scenarios)
    
    @property
    def passing_scenarios_count(self) -> int:
        """Get number of passing Gherkin scenarios."""
        return sum(1 for scenario in self.gherkin_scenarios if scenario.status == 'passing')
    
    @property
    def test_pass_rate(self) -> float:
        """Get percentage of passing test scenarios."""
        if not self.gherkin_scenarios:
            return 0.0
        
        return (self.passing_scenarios_count / len(self.gherkin_scenarios)) * 100
    
    @property
    def expected_results_count(self) -> int:
        """Get total number of expected results."""
        return len(self.expected_results)
    
    @property
    def verified_results_count(self) -> int:
        """Get number of verified expected results."""
        return sum(1 for result in self.expected_results if result.status == 'verified')
    
    @property
    def verification_rate(self) -> float:
        """Get percentage of verified expected results."""
        if not self.expected_results:
            return 100.0
        
        return (self.verified_results_count / len(self.expected_results)) * 100
    
    def update_acceptance_criteria_status(self) -> None:
        """Update acceptance criteria met status based on requirements and tests."""
        # Check if all requirements are verified
        req_verified = all(req.status == 'verified' for req in self.requirements)
        
        # Check if all expected results are verified
        results_verified = all(result.status == 'verified' for result in self.expected_results)
        
        # Check if all scenarios are passing
        scenarios_passing = all(scenario.status == 'passing' for scenario in self.gherkin_scenarios)
        
        # Require at least one of each type if any exist
        has_requirements = len(self.requirements) > 0
        has_results = len(self.expected_results) > 0
        has_scenarios = len(self.gherkin_scenarios) > 0
        
        if has_requirements or has_results or has_scenarios:
            self.acceptance_criteria_met = (
                (not has_requirements or req_verified) and
                (not has_results or results_verified) and
                (not has_scenarios or scenarios_passing)
            )
        else:
            # No acceptance criteria defined
            self.acceptance_criteria_met = False
    
    def get_requirements_summary(self) -> Dict[str, Any]:
        """Get a summary of all requirements data."""
        return {
            'requirements_count': self.requirements_count,
            'requirements_coverage': self.requirements_coverage,
            'requirements_status': self.requirements_status,
            'user_stories_count': self.user_stories_count,
            'total_story_points': self.total_story_points,
            'expected_results_count': self.expected_results_count,
            'verified_results_count': self.verified_results_count,
            'verification_rate': self.verification_rate,
            'gherkin_scenarios_count': self.gherkin_scenarios_count,
            'passing_scenarios_count': self.passing_scenarios_count,
            'test_pass_rate': self.test_pass_rate,
            'test_coverage_percentage': self.test_coverage_percentage,
            'acceptance_criteria_met': self.acceptance_criteria_met
        }


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
