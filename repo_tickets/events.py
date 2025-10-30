#!/usr/bin/env python3
"""
Event bus system for repo-tickets.

Provides publish/subscribe pattern for real-time reactive automation.
Enables agents to respond to events without polling.
"""

import json
import time
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Any, Optional
from collections import defaultdict
from pathlib import Path
from threading import RLock


class EventType(Enum):
    """Types of events that can be published."""
    
    # Ticket events
    TICKET_CREATED = "ticket.created"
    TICKET_UPDATED = "ticket.updated"
    TICKET_CLOSED = "ticket.closed"
    TICKET_REOPENED = "ticket.reopened"
    TICKET_DELETED = "ticket.deleted"
    TICKET_ASSIGNED = "ticket.assigned"
    TICKET_COMMENTED = "ticket.commented"
    
    # Agent events
    AGENT_TASK_ASSIGNED = "agent.task.assigned"
    AGENT_TASK_STARTED = "agent.task.started"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"
    
    # Requirement events
    REQUIREMENT_ADDED = "requirement.added"
    REQUIREMENT_VERIFIED = "requirement.verified"
    TEST_PASSED = "test.passed"
    TEST_FAILED = "test.failed"
    
    # Epic events
    EPIC_CREATED = "epic.created"
    EPIC_UPDATED = "epic.updated"
    EPIC_COMPLETED = "epic.completed"
    
    # Milestone events
    MILESTONE_REACHED = "milestone.reached"
    SPRINT_STARTED = "sprint.started"
    SPRINT_COMPLETED = "sprint.completed"
    
    # System events
    INDEX_REBUILT = "system.index.rebuilt"
    CACHE_CLEARED = "system.cache.cleared"


class Event:
    """Represents a single event."""
    
    def __init__(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an event.
        
        Args:
            event_type: Type of event.
            data: Event payload data.
            source: Source that generated the event.
            metadata: Additional metadata.
        """
        self.id = self._generate_event_id()
        self.type = event_type
        self.data = data
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
    
    @staticmethod
    def _generate_event_id() -> str:
        """Generate unique event ID."""
        return f"evt_{int(time.time() * 1000000)}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'id': self.id,
            'type': self.type.value,
            'data': self.data,
            'source': self.source,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f"Event(id={self.id}, type={self.type.value}, timestamp={self.timestamp})"


class EventBus:
    """
    Event bus for publish/subscribe pattern.
    
    Enables real-time reactive automation by allowing components
    to subscribe to events and respond automatically.
    """
    
    def __init__(self, enable_history: bool = True, max_history: int = 1000):
        """
        Initialize event bus.
        
        Args:
            enable_history: Whether to keep event history.
            max_history: Maximum number of events to keep in history.
        """
        self._subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._global_subscribers: List[Callable] = []
        self._event_history: List[Event] = []
        self._enable_history = enable_history
        self._max_history = max_history
        self._lock = RLock()
        self._stats = {
            'total_events': 0,
            'events_by_type': defaultdict(int),
            'total_subscribers': 0,
            'handler_errors': 0,
        }
    
    def subscribe(
        self,
        event_type: EventType,
        handler: Callable[[Event], None],
        handler_id: Optional[str] = None
    ) -> str:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to.
            handler: Callback function that receives Event object.
            handler_id: Optional identifier for the handler.
            
        Returns:
            Handler ID for unsubscribing.
        """
        with self._lock:
            if handler_id is None:
                handler_id = f"handler_{id(handler)}"
            
            # Store handler with ID
            handler._handler_id = handler_id
            self._subscribers[event_type].append(handler)
            self._stats['total_subscribers'] += 1
            
            return handler_id
    
    def subscribe_all(
        self,
        handler: Callable[[Event], None],
        handler_id: Optional[str] = None
    ) -> str:
        """
        Subscribe to all events.
        
        Args:
            handler: Callback function that receives Event object.
            handler_id: Optional identifier for the handler.
            
        Returns:
            Handler ID for unsubscribing.
        """
        with self._lock:
            if handler_id is None:
                handler_id = f"global_handler_{id(handler)}"
            
            handler._handler_id = handler_id
            self._global_subscribers.append(handler)
            self._stats['total_subscribers'] += 1
            
            return handler_id
    
    def unsubscribe(self, event_type: EventType, handler_id: str) -> bool:
        """
        Unsubscribe a handler.
        
        Args:
            event_type: Event type to unsubscribe from.
            handler_id: Handler ID returned from subscribe().
            
        Returns:
            True if handler was found and removed.
        """
        with self._lock:
            handlers = self._subscribers.get(event_type, [])
            for handler in handlers:
                if hasattr(handler, '_handler_id') and handler._handler_id == handler_id:
                    handlers.remove(handler)
                    self._stats['total_subscribers'] -= 1
                    return True
            return False
    
    def unsubscribe_all(self, handler_id: str) -> bool:
        """
        Unsubscribe a global handler.
        
        Args:
            handler_id: Handler ID returned from subscribe_all().
            
        Returns:
            True if handler was found and removed.
        """
        with self._lock:
            for handler in self._global_subscribers[:]:
                if hasattr(handler, '_handler_id') and handler._handler_id == handler_id:
                    self._global_subscribers.remove(handler)
                    self._stats['total_subscribers'] -= 1
                    return True
            return False
    
    def publish(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        source: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event.
            data: Event payload data.
            source: Source that generated the event.
            metadata: Additional metadata.
            
        Returns:
            The published Event object.
        """
        event = Event(event_type, data, source, metadata)
        
        with self._lock:
            # Update statistics
            self._stats['total_events'] += 1
            self._stats['events_by_type'][event_type.value] += 1
            
            # Add to history
            if self._enable_history:
                self._event_history.append(event)
                # Trim history if needed
                if len(self._event_history) > self._max_history:
                    self._event_history = self._event_history[-self._max_history:]
            
            # Notify type-specific subscribers
            handlers = self._subscribers.get(event_type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    self._stats['handler_errors'] += 1
                    print(f"Error in event handler for {event_type.value}: {e}")
            
            # Notify global subscribers
            for handler in self._global_subscribers:
                try:
                    handler(event)
                except Exception as e:
                    self._stats['handler_errors'] += 1
                    print(f"Error in global event handler: {e}")
        
        return event
    
    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_type: Filter by event type (None for all).
            limit: Maximum number of events to return.
            since: Only return events after this time.
            
        Returns:
            List of events (most recent first).
        """
        with self._lock:
            events = self._event_history[:]
        
        # Filter by type
        if event_type:
            events = [e for e in events if e.type == event_type]
        
        # Filter by time
        if since:
            events = [e for e in events if e.timestamp >= since]
        
        # Sort by timestamp (most recent first)
        events.sort(key=lambda e: e.timestamp, reverse=True)
        
        return events[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        with self._lock:
            return {
                'total_events': self._stats['total_events'],
                'total_subscribers': self._stats['total_subscribers'],
                'handler_errors': self._stats['handler_errors'],
                'events_by_type': dict(self._stats['events_by_type']),
                'history_size': len(self._event_history),
                'history_enabled': self._enable_history,
            }
    
    def clear_history(self) -> int:
        """
        Clear event history.
        
        Returns:
            Number of events cleared.
        """
        with self._lock:
            count = len(self._event_history)
            self._event_history.clear()
            return count
    
    def save_history(self, file_path: Path) -> int:
        """
        Save event history to file.
        
        Args:
            file_path: Path to save history.
            
        Returns:
            Number of events saved.
        """
        with self._lock:
            history = [event.to_dict() for event in self._event_history]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, default=str)
        
        return len(history)
    
    def load_history(self, file_path: Path) -> int:
        """
        Load event history from file.
        
        Args:
            file_path: Path to load history from.
            
        Returns:
            Number of events loaded.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        # Note: This loads raw dicts, not Event objects
        # Actual implementation would need to reconstruct Events
        return len(history_data)


# Global event bus instance
_global_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (useful for testing)."""
    global _global_event_bus
    _global_event_bus = None


# Convenience functions

def publish_event(
    event_type: EventType,
    data: Dict[str, Any],
    source: str = "system"
) -> Event:
    """Publish an event to the global event bus."""
    return get_event_bus().publish(event_type, data, source)


def subscribe_event(
    event_type: EventType,
    handler: Callable[[Event], None]
) -> str:
    """Subscribe to an event on the global event bus."""
    return get_event_bus().subscribe(event_type, handler)
