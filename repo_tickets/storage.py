#!/usr/bin/env python3
"""
Storage system for repo-tickets.

Handles reading and writing tickets to/from the filesystem.
"""

import os
import shutil
import time
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from threading import RLock
import yaml

from .models import Ticket, TicketConfig, Epic, BacklogItem, generate_ticket_id
from .vcs import ensure_in_repository


class TicketStorage:
    """Handles ticket persistence in the repository."""
    
    TICKETS_DIR = ".tickets"
    CONFIG_FILE = "config.yaml"
    INDEX_FILE = "index.yaml"
    CACHE_TTL = 300  # 5 minutes in seconds
    
    def __init__(self, repo_root: Optional[Path] = None, enable_cache: bool = True):
        """
        Initialize storage.
        
        Args:
            repo_root: Repository root path. If None, auto-detect.
            enable_cache: Enable caching for performance. Default True.
        """
        if repo_root is None:
            vcs = ensure_in_repository()
            repo_root = vcs.repo_root
        
        self.repo_root = Path(repo_root)
        self.tickets_dir = self.repo_root / self.TICKETS_DIR
        self.config_path = self.tickets_dir / self.CONFIG_FILE
        self.index_path = self.tickets_dir / self.INDEX_FILE
        
        # Load configuration
        self._config = None
        
        # Caching system
        self._enable_cache = enable_cache
        self._ticket_cache: Dict[str, Tuple[Ticket, float]] = {}  # ticket_id -> (ticket, timestamp)
        self._index_cache: Optional[Tuple[Dict, float]] = None  # (index, timestamp)
        self._cache_lock = RLock()
        self._cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    @property
    def config(self) -> TicketConfig:
        """Get the current configuration."""
        if self._config is None:
            self._config = TicketConfig.load_from_file(self.config_path)
        return self._config
    
    def initialize(self, force: bool = False) -> None:
        """
        Initialize the tickets directory structure.
        
        Args:
            force: If True, reinitialize even if already exists.
        """
        if self.tickets_dir.exists() and not force:
            raise ValueError(f"Tickets directory already exists: {self.tickets_dir}")
        
        if force and self.tickets_dir.exists():
            shutil.rmtree(self.tickets_dir)
        
        # Create directory structure
        self.tickets_dir.mkdir(exist_ok=True)
        (self.tickets_dir / "open").mkdir(exist_ok=True)
        (self.tickets_dir / "closed").mkdir(exist_ok=True)
        (self.tickets_dir / "epics").mkdir(exist_ok=True)
        (self.tickets_dir / "backlog").mkdir(exist_ok=True)
        
        # Create default configuration
        config = TicketConfig()
        config.save_to_file(self.config_path)
        
        # Create empty index
        self._save_index({})
        
        print(f"Initialized tickets in {self.tickets_dir}")
    
    def is_initialized(self) -> bool:
        """Check if tickets are initialized in this repository."""
        return self.tickets_dir.exists() and self.config_path.exists()
    
    def _ensure_initialized(self) -> None:
        """Ensure tickets are initialized, raise error if not."""
        if not self.is_initialized():
            raise ValueError(
                f"Tickets not initialized. Run 'tickets init' first."
            )
    
    # Cache management methods
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached item is still valid based on TTL."""
        return (time.time() - timestamp) < self.CACHE_TTL
    
    def _get_cached_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """Get ticket from cache if valid."""
        if not self._enable_cache:
            return None
        
        with self._cache_lock:
            if ticket_id in self._ticket_cache:
                ticket, timestamp = self._ticket_cache[ticket_id]
                if self._is_cache_valid(timestamp):
                    self._cache_stats['hits'] += 1
                    return ticket
                else:
                    # Expired, remove from cache
                    del self._ticket_cache[ticket_id]
                    self._cache_stats['evictions'] += 1
        
        self._cache_stats['misses'] += 1
        return None
    
    def _cache_ticket(self, ticket: Ticket) -> None:
        """Add ticket to cache."""
        if not self._enable_cache:
            return
        
        with self._cache_lock:
            self._ticket_cache[ticket.id] = (ticket, time.time())
    
    def _invalidate_ticket_cache(self, ticket_id: str) -> None:
        """Remove ticket from cache."""
        if not self._enable_cache:
            return
        
        with self._cache_lock:
            if ticket_id in self._ticket_cache:
                del self._ticket_cache[ticket_id]
    
    def _get_cached_index(self) -> Optional[Dict]:
        """Get index from cache if valid."""
        if not self._enable_cache:
            return None
        
        with self._cache_lock:
            if self._index_cache is not None:
                index, timestamp = self._index_cache
                if self._is_cache_valid(timestamp):
                    return index
                else:
                    self._index_cache = None
        
        return None
    
    def _cache_index(self, index: Dict) -> None:
        """Add index to cache."""
        if not self._enable_cache:
            return
        
        with self._cache_lock:
            self._index_cache = (index, time.time())
    
    def _invalidate_index_cache(self) -> None:
        """Remove index from cache."""
        if not self._enable_cache:
            return
        
        with self._cache_lock:
            self._index_cache = None
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        with self._cache_lock:
            self._ticket_cache.clear()
            self._index_cache = None
            self._cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def get_cache_stats(self) -> Dict:
        """Get cache performance statistics."""
        with self._cache_lock:
            stats = self._cache_stats.copy()
            stats['cache_size'] = len(self._ticket_cache)
            stats['enabled'] = self._enable_cache
            
            total_requests = stats['hits'] + stats['misses']
            if total_requests > 0:
                stats['hit_rate'] = stats['hits'] / total_requests
            else:
                stats['hit_rate'] = 0.0
            
            return stats
    
    def _get_ticket_path(self, ticket_id: str, status: str = None) -> Path:
        """Get the file path for a ticket."""
        if status is None:
            # Try to find the ticket in any status directory
            for status_dir in ["open", "closed"]:
                path = self.tickets_dir / status_dir / f"{ticket_id}.yaml"
                if path.exists():
                    return path
            # Default to open if not found
            status = "open"
        
        status_dir = "closed" if status in {"closed", "cancelled"} else "open"
        return self.tickets_dir / status_dir / f"{ticket_id}.yaml"
    
    def save_ticket(self, ticket: Ticket) -> None:
        """
        Save a ticket to storage.
        
        Args:
            ticket: Ticket to save.
        """
        self._ensure_initialized()
        
        # Get the current path (in case status changed)
        old_path = self._get_ticket_path(ticket.id)
        new_path = self._get_ticket_path(ticket.id, ticket.status)
        
        # Create status directory if needed
        new_path.parent.mkdir(exist_ok=True)
        
        # Save ticket data
        data = ticket.to_dict()
        with open(new_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        # Remove old file if path changed (status change)
        if old_path != new_path and old_path.exists():
            old_path.unlink()
        
        # Invalidate caches since data changed
        self._invalidate_ticket_cache(ticket.id)
        self._invalidate_index_cache()
        
        # Update index
        self._update_index_for_ticket(ticket)
        
        # Cache the ticket after save
        self._cache_ticket(ticket)
    
    def load_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """
        Load a ticket from storage.
        
        Args:
            ticket_id: ID of ticket to load.
            
        Returns:
            Ticket instance or None if not found.
        """
        self._ensure_initialized()
        
        # Try cache first
        cached_ticket = self._get_cached_ticket(ticket_id)
        if cached_ticket is not None:
            return cached_ticket
        
        # Cache miss, load from file
        ticket_path = self._get_ticket_path(ticket_id)
        if not ticket_path.exists():
            return None
        
        try:
            with open(ticket_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            ticket = Ticket.from_dict(data)
            
            # Cache the loaded ticket
            self._cache_ticket(ticket)
            
            return ticket
        except (yaml.YAMLError, TypeError, ValueError) as e:
            raise ValueError(f"Failed to load ticket {ticket_id}: {e}")
    
    def delete_ticket(self, ticket_id: str) -> bool:
        """
        Delete a ticket from storage.
        
        Args:
            ticket_id: ID of ticket to delete.
            
        Returns:
            True if ticket was deleted, False if not found.
        """
        self._ensure_initialized()
        
        ticket_path = self._get_ticket_path(ticket_id)
        if not ticket_path.exists():
            return False
        
        ticket_path.unlink()
        
        # Invalidate caches
        self._invalidate_ticket_cache(ticket_id)
        self._invalidate_index_cache()
        
        # Update index
        index = self._load_index()
        index.pop(ticket_id, None)
        self._save_index(index)
        
        return True
    
    def list_tickets(self, status: Optional[str] = None, 
                    labels: Optional[List[str]] = None) -> List[Ticket]:
        """
        List tickets with optional filtering.
        
        Args:
            status: Filter by status (None for all).
            labels: Filter by labels (ticket must have all specified labels).
            
        Returns:
            List of matching tickets.
        """
        self._ensure_initialized()
        
        tickets = []
        
        # Determine which directories to search
        if status is None:
            search_dirs = ["open", "closed"]
        elif status in {"closed", "cancelled"}:
            search_dirs = ["closed"]
        else:
            search_dirs = ["open"]
        
        for status_dir in search_dirs:
            dir_path = self.tickets_dir / status_dir
            if not dir_path.exists():
                continue
                
            for ticket_file in dir_path.glob("*.yaml"):
                try:
                    ticket = self.load_ticket(ticket_file.stem)
                    if ticket is None:
                        continue
                    
                    # Apply status filter
                    if status is not None and ticket.status != status:
                        continue
                    
                    # Apply labels filter
                    if labels:
                        ticket_labels = set(ticket.labels)
                        required_labels = set(labels)
                        if not required_labels.issubset(ticket_labels):
                            continue
                    
                    tickets.append(ticket)
                    
                except Exception as e:
                    print(f"Warning: Failed to load {ticket_file}: {e}")
                    continue
        
        return sorted(tickets, key=lambda t: t.created_at, reverse=True)
    
    def search_tickets(self, query: str) -> List[Ticket]:
        """
        Search tickets by text query.
        
        Args:
            query: Search query (searches title, description, and comments).
            
        Returns:
            List of matching tickets.
        """
        self._ensure_initialized()
        
        query_lower = query.lower()
        matching_tickets = []
        
        all_tickets = self.list_tickets()
        for ticket in all_tickets:
            # Search in title
            if query_lower in ticket.title.lower():
                matching_tickets.append(ticket)
                continue
            
            # Search in description
            if query_lower in ticket.description.lower():
                matching_tickets.append(ticket)
                continue
            
            # Search in comments
            for comment in ticket.comments:
                if query_lower in comment.content.lower():
                    matching_tickets.append(ticket)
                    break
        
        return matching_tickets
    
    def get_existing_ids(self) -> Set[str]:
        """Get set of all existing ticket IDs."""
        self._ensure_initialized()
        
        ids = set()
        
        for status_dir in ["open", "closed"]:
            dir_path = self.tickets_dir / status_dir
            if dir_path.exists():
                ids.update(f.stem for f in dir_path.glob("*.yaml"))
        
        return ids
    
    def generate_unique_id(self, title: str) -> str:
        """Generate a unique ticket ID."""
        existing_ids = self.get_existing_ids()
        return generate_ticket_id(title, existing_ids)
    
    def _load_index(self) -> Dict[str, Dict]:
        """Load the ticket index."""
        # Try cache first
        cached_index = self._get_cached_index()
        if cached_index is not None:
            return cached_index
        
        # Cache miss, load from file
        if not self.index_path.exists():
            return {}
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                index = yaml.safe_load(f) or {}
            
            # Cache the loaded index
            self._cache_index(index)
            
            return index
        except (yaml.YAMLError, FileNotFoundError):
            return {}
    
    def _save_index(self, index: Dict[str, Dict]) -> None:
        """Save the ticket index."""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            yaml.dump(index, f, default_flow_style=False, sort_keys=True)
        
        # Cache the index after save
        self._cache_index(index)
    
    def _update_index_for_ticket(self, ticket: Ticket) -> None:
        """Update index entry for a ticket."""
        index = self._load_index()
        index[ticket.id] = {
            'title': ticket.title,
            'status': ticket.status,
            'priority': ticket.priority,
            'labels': ticket.labels,
            'created_at': ticket.created_at.isoformat(),
            'updated_at': ticket.updated_at.isoformat(),
        }
        self._save_index(index)
    
    def get_stats(self) -> Dict[str, int]:
        """Get ticket statistics."""
        self._ensure_initialized()
        
        index = self._load_index()
        stats = {
            'total': len(index),
            'open': 0,
            'in_progress': 0,
            'closed': 0,
            'blocked': 0,
            'cancelled': 0,
        }
        
        for ticket_data in index.values():
            status = ticket_data.get('status', 'open')
            if status in stats:
                stats[status] += 1
            else:
                stats['open'] += 1  # fallback
        
        return stats
    
    # Fast index-based operations (Phase 1.4 optimization)
    
    def search_tickets_fast(self, query: str) -> List[str]:
        """Fast search using index only, returns ticket IDs.
        
        This is 10-100x faster than search_tickets() as it only searches
        the index without loading full ticket data.
        
        Args:
            query: Search query (searches title and labels in index).
            
        Returns:
            List of matching ticket IDs.
        """
        self._ensure_initialized()
        
        query_lower = query.lower()
        results = []
        
        index = self._load_index()
        for ticket_id, ticket_info in index.items():
            # Search in title
            if query_lower in ticket_info.get('title', '').lower():
                results.append(ticket_id)
                continue
            
            # Search in labels
            labels = ticket_info.get('labels', [])
            if any(query_lower in label.lower() for label in labels):
                results.append(ticket_id)
        
        return results
    
    def list_tickets_summary(self, status: Optional[str] = None,
                            priority: Optional[str] = None,
                            labels: Optional[List[str]] = None) -> List[Dict]:
        """Return ticket summaries from index without loading full tickets.
        
        This is much faster than list_tickets() for displaying ticket lists.
        Returns lightweight dict objects instead of full Ticket instances.
        
        Args:
            status: Filter by status (None for all).
            priority: Filter by priority (None for all).
            labels: Filter by labels (ticket must have all specified labels).
            
        Returns:
            List of ticket summary dicts with id, title, status, priority, labels, dates.
        """
        self._ensure_initialized()
        
        index = self._load_index()
        summaries = []
        
        for ticket_id, ticket_info in index.items():
            # Apply status filter
            if status is not None and ticket_info.get('status') != status:
                continue
            
            # Apply priority filter
            if priority is not None and ticket_info.get('priority') != priority:
                continue
            
            # Apply labels filter
            if labels:
                ticket_labels = set(ticket_info.get('labels', []))
                required_labels = set(labels)
                if not required_labels.issubset(ticket_labels):
                    continue
            
            summaries.append({
                'id': ticket_id,
                'title': ticket_info.get('title', ''),
                'status': ticket_info.get('status', 'open'),
                'priority': ticket_info.get('priority', 'medium'),
                'labels': ticket_info.get('labels', []),
                'created_at': ticket_info.get('created_at', ''),
                'updated_at': ticket_info.get('updated_at', ''),
            })
        
        # Sort by created_at (most recent first)
        summaries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return summaries
    
    def get_tickets_by_ids(self, ticket_ids: List[str]) -> List[Ticket]:
        """Load multiple tickets efficiently.
        
        Args:
            ticket_ids: List of ticket IDs to load.
            
        Returns:
            List of Ticket objects (None values filtered out).
        """
        tickets = []
        for ticket_id in ticket_ids:
            ticket = self.load_ticket(ticket_id)
            if ticket:
                tickets.append(ticket)
        return tickets
    
    def rebuild_index(self) -> int:
        """Rebuild the index from scratch by scanning all ticket files.
        
        Returns:
            Number of tickets indexed.
        """
        self._ensure_initialized()
        
        index = {}
        ticket_count = 0
        
        for status_dir in ['open', 'closed']:
            dir_path = self.tickets_dir / status_dir
            if not dir_path.exists():
                continue
            
            for ticket_file in dir_path.glob('*.yaml'):
                try:
                    ticket = self.load_ticket(ticket_file.stem)
                    if ticket:
                        index[ticket.id] = {
                            'title': ticket.title,
                            'status': ticket.status,
                            'priority': ticket.priority,
                            'labels': ticket.labels,
                            'created_at': ticket.created_at.isoformat(),
                            'updated_at': ticket.updated_at.isoformat(),
                        }
                        ticket_count += 1
                except Exception as e:
                    print(f"Warning: Failed to index {ticket_file}: {e}")
        
        self._save_index(index)
        return ticket_count
    
    # Epic Management Methods
    
    def save_epic(self, epic: Epic) -> None:
        """Save an epic to storage."""
        self._ensure_initialized()
        
        epic_path = self.tickets_dir / "epics" / f"{epic.id}.yaml"
        epic_path.parent.mkdir(exist_ok=True)
        
        data = epic.to_dict()
        with open(epic_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def load_epic(self, epic_id: str) -> Optional[Epic]:
        """Load an epic from storage."""
        self._ensure_initialized()
        
        epic_path = self.tickets_dir / "epics" / f"{epic_id}.yaml"
        if not epic_path.exists():
            return None
        
        try:
            with open(epic_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return Epic.from_dict(data)
        except (yaml.YAMLError, TypeError, ValueError) as e:
            raise ValueError(f"Failed to load epic {epic_id}: {e}")
    
    def delete_epic(self, epic_id: str) -> bool:
        """Delete an epic from storage."""
        self._ensure_initialized()
        
        epic_path = self.tickets_dir / "epics" / f"{epic_id}.yaml"
        if not epic_path.exists():
            return False
        
        epic_path.unlink()
        return True
    
    def list_epics(self, status: Optional[str] = None) -> List[Epic]:
        """List epics with optional filtering."""
        self._ensure_initialized()
        
        epics = []
        epics_dir = self.tickets_dir / "epics"
        
        if not epics_dir.exists():
            return epics
        
        for epic_file in epics_dir.glob("*.yaml"):
            try:
                with open(epic_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                epic = Epic.from_dict(data)
                
                # Apply status filter
                if status is None or epic.status == status:
                    epics.append(epic)
            except Exception:
                # Skip corrupted files
                continue
        
        return sorted(epics, key=lambda e: e.created_at)
    
    def generate_epic_id(self, title: str) -> str:
        """Generate a unique epic ID based on title."""
        existing_epics = self.list_epics()
        existing_ids = {epic.id for epic in existing_epics}
        
        # Extract first meaningful word from title
        import re
        words = re.findall(r'\w+', title.upper())
        if words:
            prefix = words[0][:8]  # Max 8 chars
        else:
            prefix = "EPIC"
        
        # Find the next available number
        counter = 1
        while True:
            epic_id = f"{prefix}-{counter}"
            if epic_id not in existing_ids:
                return epic_id
            counter += 1
    
    def add_ticket_to_epic(self, epic_id: str, ticket_id: str) -> bool:
        """Add a ticket to an epic."""
        epic = self.load_epic(epic_id)
        ticket = self.load_ticket(ticket_id)
        
        if not epic or not ticket:
            return False
        
        # Update epic
        epic.add_ticket(ticket_id)
        self.save_epic(epic)
        
        # Update ticket
        ticket.assign_to_epic(epic_id)
        self.save_ticket(ticket)
        
        return True
    
    def remove_ticket_from_epic(self, epic_id: str, ticket_id: str) -> bool:
        """Remove a ticket from an epic."""
        epic = self.load_epic(epic_id)
        ticket = self.load_ticket(ticket_id)
        
        if not epic or not ticket:
            return False
        
        # Update epic
        epic.remove_ticket(ticket_id)
        self.save_epic(epic)
        
        # Update ticket
        ticket.remove_from_epic()
        self.save_ticket(ticket)
        
        return True
    
    # Backlog Management Methods
    
    def save_backlog_item(self, item: BacklogItem) -> None:
        """Save a backlog item to storage."""
        self._ensure_initialized()
        
        item_path = self.tickets_dir / "backlog" / f"{item.id}.yaml"
        item_path.parent.mkdir(exist_ok=True)
        
        data = item.to_dict()
        with open(item_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def load_backlog_item(self, item_id: str) -> Optional[BacklogItem]:
        """Load a backlog item from storage."""
        self._ensure_initialized()
        
        item_path = self.tickets_dir / "backlog" / f"{item_id}.yaml"
        if not item_path.exists():
            return None
        
        try:
            with open(item_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return BacklogItem.from_dict(data)
        except (yaml.YAMLError, TypeError, ValueError) as e:
            raise ValueError(f"Failed to load backlog item {item_id}: {e}")
    
    def delete_backlog_item(self, item_id: str) -> bool:
        """Delete a backlog item from storage."""
        self._ensure_initialized()
        
        item_path = self.tickets_dir / "backlog" / f"{item_id}.yaml"
        if not item_path.exists():
            return False
        
        item_path.unlink()
        return True
    
    def list_backlog_items(self, status: Optional[str] = None, 
                          epic_id: Optional[str] = None,
                          sprint_id: Optional[str] = None) -> List[BacklogItem]:
        """List backlog items with optional filtering."""
        self._ensure_initialized()
        
        items = []
        backlog_dir = self.tickets_dir / "backlog"
        
        if not backlog_dir.exists():
            return items
        
        for item_file in backlog_dir.glob("*.yaml"):
            try:
                with open(item_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                item = BacklogItem.from_dict(data)
                
                # Apply filters
                if status is not None and item.status != status:
                    continue
                if epic_id is not None and item.epic_id != epic_id:
                    continue
                if sprint_id is not None and item.sprint_id != sprint_id:
                    continue
                
                items.append(item)
            except Exception:
                # Skip corrupted files
                continue
        
        return sorted(items, key=lambda i: i.priority_score, reverse=True)
    
    def generate_backlog_item_id(self, title: str) -> str:
        """Generate a unique backlog item ID based on title."""
        existing_items = self.list_backlog_items()
        existing_ids = {item.id for item in existing_items}
        
        # Extract first meaningful word from title
        import re
        words = re.findall(r'\w+', title.upper())
        if words:
            prefix = words[0][:6]  # Max 6 chars for backlog
        else:
            prefix = "BL"
        
        # Find the next available number
        counter = 1
        while True:
            item_id = f"{prefix}-{counter}"
            if item_id not in existing_ids:
                return item_id
            counter += 1
    
    def convert_backlog_to_ticket(self, item_id: str, reporter: str = "", reporter_email: str = "") -> Optional[Ticket]:
        """Convert a backlog item to a ticket."""
        item = self.load_backlog_item(item_id)
        if not item:
            return None
        
        # Generate ticket ID
        existing_tickets = self.list_tickets()
        existing_ids = {ticket.id for ticket in existing_tickets}
        ticket_id = generate_ticket_id(item.title, existing_ids)
        
        # Create ticket from backlog item
        ticket = Ticket(
            id=ticket_id,
            title=item.title,
            description=item.description,
            status="open",
            priority=item.priority,
            assignee=item.assigned_to if item.assigned_to else None,
            reporter=reporter or item.product_owner,
            reporter_email=reporter_email,
            labels=item.labels.copy(),
            story_points=item.story_points,
            epic_id=item.epic_id
        )
        
        # Add acceptance criteria as requirements
        for criterion in item.acceptance_criteria:
            ticket.add_requirement(
                title=f"AC: {criterion[:50]}...",
                description=criterion,
                priority=item.priority,
                author=reporter or item.product_owner
            )
        
        # Save ticket
        self.save_ticket(ticket)
        
        # Update backlog item to reference ticket
        item.update(ticket_id=ticket_id, status="in-progress")
        self.save_backlog_item(item)
        
        return ticket
