#!/usr/bin/env python3
"""
Schema validation for repo-tickets using Pydantic.

Provides type-safe models and schema migration support.
"""

from typing import List, Dict, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator
from pathlib import Path
import json

from .logging_utils import get_logger


logger = get_logger()


# Enums for validation

class TicketStatusEnum(str, Enum):
    """Valid ticket statuses."""
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    BLOCKED = "blocked"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class PriorityEnum(str, Enum):
    """Valid priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AgentStatusEnum(str, Enum):
    """Valid agent statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


# Schema Models

class CommentSchema(BaseModel):
    """Schema for ticket comments."""
    
    id: str
    author: str
    email: str
    content: str
    created_at: datetime
    
    class Config:
        extra = "allow"  # Allow extra fields for forward compatibility


class TimeLogSchema(BaseModel):
    """Schema for time logs."""
    
    id: str
    entry_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_hours: Optional[float] = None
    description: Optional[str] = None
    
    @validator('duration_hours')
    def validate_duration(cls, v, values):
        """Ensure duration is non-negative."""
        if v is not None and v < 0:
            raise ValueError("Duration must be non-negative")
        return v
    
    class Config:
        extra = "allow"


class RequirementSchema(BaseModel):
    """Schema for requirements."""
    
    id: str
    title: str
    description: str
    priority: PriorityEnum
    status: str
    acceptance_criteria: List[str] = Field(default_factory=list)
    verified: bool = False
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    class Config:
        extra = "allow"


class UserStorySchema(BaseModel):
    """Schema for user stories."""
    
    id: str
    as_a: str
    i_want: str
    so_that: str
    priority: PriorityEnum
    story_points: Optional[int] = None
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    @validator('story_points')
    def validate_story_points(cls, v):
        """Ensure story points are positive."""
        if v is not None and v <= 0:
            raise ValueError("Story points must be positive")
        return v
    
    class Config:
        extra = "allow"


class TicketSchema(BaseModel):
    """
    Schema for tickets with validation.
    
    Provides type safety and validation for all ticket fields.
    """
    
    # Required fields
    id: str = Field(..., regex=r'^[A-Z]+-\d+$', description="Ticket ID (e.g., TICKET-123)")
    title: str = Field(..., min_length=1, max_length=200, description="Ticket title")
    status: TicketStatusEnum
    priority: PriorityEnum
    
    # Optional core fields
    description: str = ""
    assignee: Optional[str] = None
    reporter: str = "unknown"
    reporter_email: str = "unknown@localhost"
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    labels: List[str] = Field(default_factory=list)
    branch: Optional[str] = None
    
    # Estimation
    estimated_hours: Optional[float] = None
    story_points: Optional[int] = None
    
    # Related entities
    epic_id: Optional[str] = None
    parent_ticket_id: Optional[str] = None
    blocked_by: List[str] = Field(default_factory=list)
    related_tickets: List[str] = Field(default_factory=list)
    
    # Requirements
    requirements: List[RequirementSchema] = Field(default_factory=list)
    user_stories: List[UserStorySchema] = Field(default_factory=list)
    requirements_status: str = "not_started"
    
    # Interactions
    comments: List[CommentSchema] = Field(default_factory=list)
    time_logs: List[TimeLogSchema] = Field(default_factory=list)
    
    @validator('estimated_hours')
    def validate_estimated_hours(cls, v):
        """Ensure estimated hours are positive."""
        if v is not None and v <= 0:
            raise ValueError("Estimated hours must be positive")
        return v
    
    @validator('story_points')
    def validate_story_points(cls, v):
        """Ensure story points are positive."""
        if v is not None and v <= 0:
            raise ValueError("Story points must be positive")
        return v
    
    @validator('labels')
    def validate_labels(cls, v):
        """Ensure labels don't have duplicates."""
        if len(v) != len(set(v)):
            raise ValueError("Labels must be unique")
        return v
    
    @root_validator
    def validate_dependencies(cls, values):
        """Ensure ticket doesn't block itself."""
        ticket_id = values.get('id')
        blocked_by = values.get('blocked_by', [])
        
        if ticket_id in blocked_by:
            raise ValueError("Ticket cannot block itself")
        
        return values
    
    class Config:
        extra = "forbid"  # Strict validation - no extra fields
        validate_assignment = True


class EpicSchema(BaseModel):
    """Schema for epics."""
    
    id: str = Field(..., regex=r'^EPIC-[A-Z0-9-]+$')
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    status: str
    priority: PriorityEnum
    owner: str
    owner_email: str
    
    created_at: datetime
    updated_at: datetime
    
    labels: List[str] = Field(default_factory=list)
    ticket_ids: List[str] = Field(default_factory=list)
    
    target_version: Optional[str] = None
    target_date: Optional[datetime] = None
    estimated_story_points: Optional[int] = None
    
    goals: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


class AgentSchema(BaseModel):
    """Schema for AI agents."""
    
    id: str = Field(..., regex=r'^AGENT-[A-Z0-9-]+$')
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    agent_type: str
    status: AgentStatusEnum
    
    created_at: datetime
    last_seen: Optional[datetime] = None
    
    max_concurrent_tasks: int = Field(1, ge=1, le=100)
    preferred_task_types: List[str] = Field(default_factory=list)
    
    endpoint: Optional[str] = None
    model: Optional[str] = None
    
    class Config:
        extra = "allow"


class BacklogItemSchema(BaseModel):
    """Schema for backlog items."""
    
    id: str = Field(..., regex=r'^BACKLOG-\d+$')
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    priority: PriorityEnum
    
    created_at: datetime
    created_by: str
    
    business_value: int = Field(0, ge=0, le=100)
    effort_estimate: int = Field(0, ge=0, le=100)
    risk_level: str = "medium"
    
    labels: List[str] = Field(default_factory=list)
    
    class Config:
        extra = "allow"


# Schema Migration System

class SchemaVersion(BaseModel):
    """Schema version information."""
    
    version: int
    name: str
    applied_at: datetime
    description: str


class SchemaMigrator:
    """
    Handles schema migrations between versions.
    
    Ensures data compatibility when schema changes.
    """
    
    CURRENT_VERSION = 1
    
    def __init__(self, data_dir: Path):
        """
        Initialize migrator.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.versions_file = data_dir / "schema_versions.json"
        
        # Load or create version history
        self.versions = self._load_versions()
    
    def _load_versions(self) -> List[SchemaVersion]:
        """Load schema version history."""
        if not self.versions_file.exists():
            return []
        
        try:
            with open(self.versions_file, 'r') as f:
                data = json.load(f)
            
            return [SchemaVersion(**v) for v in data]
        except Exception as e:
            logger.error("Failed to load schema versions", error=str(e))
            return []
    
    def _save_versions(self) -> None:
        """Save schema version history."""
        try:
            data = [v.dict() for v in self.versions]
            
            with open(self.versions_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.debug("Saved schema versions")
        except Exception as e:
            logger.error("Failed to save schema versions", error=str(e))
    
    def get_current_version(self) -> int:
        """Get current schema version from data."""
        if not self.versions:
            return 0
        return max(v.version for v in self.versions)
    
    def needs_migration(self) -> bool:
        """Check if migration is needed."""
        current = self.get_current_version()
        return current < self.CURRENT_VERSION
    
    def migrate(self) -> bool:
        """
        Migrate data to current schema version.
        
        Returns:
            True if migration was successful
        """
        current = self.get_current_version()
        
        if current >= self.CURRENT_VERSION:
            logger.info("Schema is up to date", version=current)
            return True
        
        logger.info(
            "Starting schema migration",
            from_version=current,
            to_version=self.CURRENT_VERSION
        )
        
        try:
            # Apply migrations sequentially
            for version in range(current + 1, self.CURRENT_VERSION + 1):
                migration_method = getattr(self, f'_migrate_to_v{version}', None)
                
                if migration_method:
                    logger.info(f"Applying migration to v{version}")
                    migration_method()
                    
                    # Record migration
                    self.versions.append(SchemaVersion(
                        version=version,
                        name=f"v{version}",
                        applied_at=datetime.now(),
                        description=migration_method.__doc__ or ""
                    ))
                else:
                    logger.warning(f"No migration method for v{version}")
            
            self._save_versions()
            
            logger.info("Schema migration completed", version=self.CURRENT_VERSION)
            return True
            
        except Exception as e:
            logger.error("Schema migration failed", error=str(e))
            return False
    
    def _migrate_to_v1(self) -> None:
        """Initial schema version - add version tracking."""
        logger.info("Initializing schema version tracking")
    
    def validate_ticket(self, ticket_data: Dict[str, Any]) -> TicketSchema:
        """
        Validate ticket data against schema.
        
        Args:
            ticket_data: Ticket data dictionary
        
        Returns:
            Validated TicketSchema
        
        Raises:
            ValidationError if validation fails
        """
        return TicketSchema(**ticket_data)
    
    def validate_epic(self, epic_data: Dict[str, Any]) -> EpicSchema:
        """Validate epic data against schema."""
        return EpicSchema(**epic_data)
    
    def validate_agent(self, agent_data: Dict[str, Any]) -> AgentSchema:
        """Validate agent data against schema."""
        return AgentSchema(**agent_data)
    
    def validate_backlog_item(self, backlog_data: Dict[str, Any]) -> BacklogItemSchema:
        """Validate backlog item data against schema."""
        return BacklogItemSchema(**backlog_data)


# Validation Helpers

def validate_ticket_dict(ticket_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate a ticket dictionary.
    
    Args:
        ticket_data: Ticket data
    
    Returns:
        (is_valid, error_message)
    """
    try:
        TicketSchema(**ticket_data)
        return (True, None)
    except Exception as e:
        return (False, str(e))


def get_schema_migrator(data_dir: Optional[Path] = None) -> SchemaMigrator:
    """
    Get SchemaMigrator instance.
    
    Args:
        data_dir: Data directory
    
    Returns:
        SchemaMigrator instance
    """
    if data_dir is None:
        from .storage import TicketStorage
        storage = TicketStorage()
        data_dir = storage.tickets_dir
    
    return SchemaMigrator(data_dir)


# Export validation functions

__all__ = [
    # Enums
    'TicketStatusEnum',
    'PriorityEnum',
    'AgentStatusEnum',
    
    # Schemas
    'TicketSchema',
    'EpicSchema',
    'AgentSchema',
    'BacklogItemSchema',
    'CommentSchema',
    'TimeLogSchema',
    'RequirementSchema',
    'UserStorySchema',
    
    # Migration
    'SchemaMigrator',
    'SchemaVersion',
    
    # Helpers
    'validate_ticket_dict',
    'get_schema_migrator',
]
