#!/usr/bin/env python3
"""
Batch operations for repo-tickets.

Provides efficient bulk operations with transaction support and rollback capability.
"""

from typing import List, Dict, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time
from threading import RLock

from .models import Ticket, Epic, BacklogItem
from .storage import TicketStorage
from .events import EventType, publish_event
from .logging_utils import get_logger, log_performance


logger = get_logger()


class OperationType(Enum):
    """Types of batch operations."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    CUSTOM = "custom"


@dataclass
class Operation:
    """Represents a single operation in a batch."""
    
    type: OperationType
    data: Dict[str, Any]
    ticket_id: Optional[str] = None
    rollback_data: Optional[Dict[str, Any]] = None
    
    def __repr__(self) -> str:
        if self.ticket_id:
            return f"Operation({self.type.value}, {self.ticket_id})"
        return f"Operation({self.type.value})"


@dataclass
class BatchResult:
    """Result of a batch operation."""
    
    success: bool
    operations_executed: int
    operations_failed: int
    created_ids: List[str] = field(default_factory=list)
    updated_ids: List[str] = field(default_factory=list)
    deleted_ids: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    duration_ms: float = 0.0
    rolled_back: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'operations_executed': self.operations_executed,
            'operations_failed': self.operations_failed,
            'created_ids': self.created_ids,
            'updated_ids': self.updated_ids,
            'deleted_ids': self.deleted_ids,
            'errors': self.errors,
            'duration_ms': self.duration_ms,
            'rolled_back': self.rolled_back
        }


class BatchOperations:
    """
    Efficient batch operations for tickets.
    
    Provides atomic transactions with rollback capability.
    """
    
    def __init__(self, storage: TicketStorage):
        """
        Initialize batch operations.
        
        Args:
            storage: TicketStorage instance
        """
        self.storage = storage
        self._lock = RLock()
    
    def batch_create_tickets(
        self,
        tickets_data: List[Dict[str, Any]],
        atomic: bool = True
    ) -> BatchResult:
        """
        Create multiple tickets in batch.
        
        Args:
            tickets_data: List of ticket data dictionaries
            atomic: If True, rollback all on any failure
        
        Returns:
            BatchResult with created ticket IDs
        """
        with log_performance("batch_create_tickets", count=len(tickets_data)):
            with self._lock:
                result = BatchResult(
                    success=True,
                    operations_executed=0,
                    operations_failed=0
                )
                start_time = time.time()
                
                created_tickets = []
                
                try:
                    for i, ticket_data in enumerate(tickets_data):
                        try:
                            # Create ticket
                            ticket = Ticket(**ticket_data)
                            self.storage.save_ticket(ticket)
                            
                            result.created_ids.append(ticket.id)
                            created_tickets.append(ticket)
                            result.operations_executed += 1
                            
                            logger.log_ticket_operation(
                                "batch_created",
                                ticket.id,
                                index=i,
                                total=len(tickets_data)
                            )
                            
                        except Exception as e:
                            result.operations_failed += 1
                            result.errors.append({
                                'index': i,
                                'data': ticket_data,
                                'error': str(e)
                            })
                            
                            logger.error(
                                "Batch create failed for ticket",
                                index=i,
                                error=str(e)
                            )
                            
                            if atomic:
                                # Rollback all created tickets
                                self._rollback_creates(created_tickets)
                                result.rolled_back = True
                                result.success = False
                                raise
                
                except Exception as e:
                    result.success = False
                    if not atomic:
                        # Continue processing remaining tickets
                        pass
                
                result.duration_ms = (time.time() - start_time) * 1000
                
                # Publish batch event
                if result.created_ids:
                    publish_event(
                        EventType.TICKET_CREATED,
                        {
                            'ticket_ids': result.created_ids,
                            'count': len(result.created_ids),
                            'batch': True
                        }
                    )
                
                return result
    
    def batch_update(
        self,
        updates: Dict[str, Dict[str, Any]],
        atomic: bool = True
    ) -> BatchResult:
        """
        Update multiple tickets in batch.
        
        Args:
            updates: Dict mapping ticket_id to update fields
            atomic: If True, rollback all on any failure
        
        Returns:
            BatchResult with updated ticket IDs
        """
        with log_performance("batch_update", count=len(updates)):
            with self._lock:
                result = BatchResult(
                    success=True,
                    operations_executed=0,
                    operations_failed=0
                )
                start_time = time.time()
                
                original_states = {}
                
                try:
                    for ticket_id, update_data in updates.items():
                        try:
                            # Load ticket
                            ticket = self.storage.load_ticket(ticket_id)
                            
                            # Save original state for rollback
                            if atomic:
                                original_states[ticket_id] = ticket.to_dict()
                            
                            # Apply updates
                            for key, value in update_data.items():
                                if hasattr(ticket, key):
                                    setattr(ticket, key, value)
                            
                            # Save ticket
                            self.storage.save_ticket(ticket)
                            
                            result.updated_ids.append(ticket_id)
                            result.operations_executed += 1
                            
                            logger.log_ticket_operation(
                                "batch_updated",
                                ticket_id,
                                fields=list(update_data.keys())
                            )
                            
                        except Exception as e:
                            result.operations_failed += 1
                            result.errors.append({
                                'ticket_id': ticket_id,
                                'update_data': update_data,
                                'error': str(e)
                            })
                            
                            logger.error(
                                "Batch update failed for ticket",
                                ticket_id=ticket_id,
                                error=str(e)
                            )
                            
                            if atomic:
                                # Rollback all updates
                                self._rollback_updates(original_states)
                                result.rolled_back = True
                                result.success = False
                                raise
                
                except Exception as e:
                    result.success = False
                
                result.duration_ms = (time.time() - start_time) * 1000
                
                # Publish batch event
                if result.updated_ids:
                    publish_event(
                        EventType.TICKET_UPDATED,
                        {
                            'ticket_ids': result.updated_ids,
                            'count': len(result.updated_ids),
                            'batch': True
                        }
                    )
                
                return result
    
    def batch_delete(
        self,
        ticket_ids: List[str],
        atomic: bool = True
    ) -> BatchResult:
        """
        Delete multiple tickets in batch.
        
        Args:
            ticket_ids: List of ticket IDs to delete
            atomic: If True, rollback all on any failure
        
        Returns:
            BatchResult with deleted ticket IDs
        """
        with log_performance("batch_delete", count=len(ticket_ids)):
            with self._lock:
                result = BatchResult(
                    success=True,
                    operations_executed=0,
                    operations_failed=0
                )
                start_time = time.time()
                
                deleted_tickets = {}
                
                try:
                    for ticket_id in ticket_ids:
                        try:
                            # Load ticket for backup (if atomic)
                            if atomic:
                                ticket = self.storage.load_ticket(ticket_id)
                                deleted_tickets[ticket_id] = ticket
                            
                            # Delete ticket
                            self.storage.delete_ticket(ticket_id)
                            
                            result.deleted_ids.append(ticket_id)
                            result.operations_executed += 1
                            
                            logger.log_ticket_operation(
                                "batch_deleted",
                                ticket_id
                            )
                            
                        except Exception as e:
                            result.operations_failed += 1
                            result.errors.append({
                                'ticket_id': ticket_id,
                                'error': str(e)
                            })
                            
                            logger.error(
                                "Batch delete failed for ticket",
                                ticket_id=ticket_id,
                                error=str(e)
                            )
                            
                            if atomic:
                                # Rollback all deletes
                                self._rollback_deletes(deleted_tickets)
                                result.rolled_back = True
                                result.success = False
                                raise
                
                except Exception as e:
                    result.success = False
                
                result.duration_ms = (time.time() - start_time) * 1000
                
                # Publish batch event
                if result.deleted_ids:
                    publish_event(
                        EventType.TICKET_DELETED,
                        {
                            'ticket_ids': result.deleted_ids,
                            'count': len(result.deleted_ids),
                            'batch': True
                        }
                    )
                
                return result
    
    def execute_transaction(
        self,
        operations: List[Operation]
    ) -> BatchResult:
        """
        Execute multiple operations as a single atomic transaction.
        
        All operations succeed or all are rolled back.
        
        Args:
            operations: List of Operation objects
        
        Returns:
            BatchResult with all operation results
        """
        with log_performance("execute_transaction", count=len(operations)):
            with self._lock:
                result = BatchResult(
                    success=True,
                    operations_executed=0,
                    operations_failed=0
                )
                start_time = time.time()
                
                executed_operations = []
                
                try:
                    for i, op in enumerate(operations):
                        try:
                            if op.type == OperationType.CREATE:
                                ticket = Ticket(**op.data)
                                self.storage.save_ticket(ticket)
                                result.created_ids.append(ticket.id)
                                op.ticket_id = ticket.id
                                
                            elif op.type == OperationType.UPDATE:
                                ticket = self.storage.load_ticket(op.ticket_id)
                                op.rollback_data = ticket.to_dict()
                                
                                for key, value in op.data.items():
                                    if hasattr(ticket, key):
                                        setattr(ticket, key, value)
                                
                                self.storage.save_ticket(ticket)
                                result.updated_ids.append(op.ticket_id)
                                
                            elif op.type == OperationType.DELETE:
                                ticket = self.storage.load_ticket(op.ticket_id)
                                op.rollback_data = ticket.to_dict()
                                
                                self.storage.delete_ticket(op.ticket_id)
                                result.deleted_ids.append(op.ticket_id)
                            
                            executed_operations.append(op)
                            result.operations_executed += 1
                            
                        except Exception as e:
                            result.operations_failed += 1
                            result.errors.append({
                                'index': i,
                                'operation': str(op),
                                'error': str(e)
                            })
                            
                            logger.error(
                                "Transaction operation failed",
                                index=i,
                                operation=str(op),
                                error=str(e)
                            )
                            
                            # Rollback all executed operations
                            self._rollback_transaction(executed_operations)
                            result.rolled_back = True
                            result.success = False
                            raise
                
                except Exception as e:
                    result.success = False
                
                result.duration_ms = (time.time() - start_time) * 1000
                
                return result
    
    def _rollback_creates(self, tickets: List[Ticket]) -> None:
        """Rollback created tickets."""
        for ticket in reversed(tickets):
            try:
                self.storage.delete_ticket(ticket.id)
                logger.info("Rolled back created ticket", ticket_id=ticket.id)
            except Exception as e:
                logger.error(
                    "Rollback failed for created ticket",
                    ticket_id=ticket.id,
                    error=str(e)
                )
    
    def _rollback_updates(self, original_states: Dict[str, Dict[str, Any]]) -> None:
        """Rollback updated tickets."""
        for ticket_id, original_data in reversed(list(original_states.items())):
            try:
                ticket = Ticket.from_dict(original_data)
                self.storage.save_ticket(ticket)
                logger.info("Rolled back updated ticket", ticket_id=ticket_id)
            except Exception as e:
                logger.error(
                    "Rollback failed for updated ticket",
                    ticket_id=ticket_id,
                    error=str(e)
                )
    
    def _rollback_deletes(self, deleted_tickets: Dict[str, Ticket]) -> None:
        """Rollback deleted tickets."""
        for ticket_id, ticket in reversed(list(deleted_tickets.items())):
            try:
                self.storage.save_ticket(ticket)
                logger.info("Rolled back deleted ticket", ticket_id=ticket_id)
            except Exception as e:
                logger.error(
                    "Rollback failed for deleted ticket",
                    ticket_id=ticket_id,
                    error=str(e)
                )
    
    def _rollback_transaction(self, operations: List[Operation]) -> None:
        """Rollback a transaction."""
        for op in reversed(operations):
            try:
                if op.type == OperationType.CREATE and op.ticket_id:
                    self.storage.delete_ticket(op.ticket_id)
                    
                elif op.type == OperationType.UPDATE and op.rollback_data:
                    ticket = Ticket.from_dict(op.rollback_data)
                    self.storage.save_ticket(ticket)
                    
                elif op.type == OperationType.DELETE and op.rollback_data:
                    ticket = Ticket.from_dict(op.rollback_data)
                    self.storage.save_ticket(ticket)
                
                logger.info("Rolled back operation", operation=str(op))
                
            except Exception as e:
                logger.error(
                    "Rollback failed for operation",
                    operation=str(op),
                    error=str(e)
                )


def get_batch_operations(storage: Optional[TicketStorage] = None) -> BatchOperations:
    """
    Get a BatchOperations instance.
    
    Args:
        storage: TicketStorage instance. If None, creates new one.
    
    Returns:
        BatchOperations instance
    """
    if storage is None:
        storage = TicketStorage()
    
    return BatchOperations(storage)
