#!/usr/bin/env python3
"""
Storage system for repo-tickets.

Handles reading and writing tickets to/from the filesystem.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Set
import yaml

from .models import Ticket, TicketConfig, generate_ticket_id
from .vcs import ensure_in_repository


class TicketStorage:
    """Handles ticket persistence in the repository."""
    
    TICKETS_DIR = ".tickets"
    CONFIG_FILE = "config.yaml"
    INDEX_FILE = "index.yaml"
    
    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize storage.
        
        Args:
            repo_root: Repository root path. If None, auto-detect.
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
        
        # Update index
        self._update_index_for_ticket(ticket)
    
    def load_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """
        Load a ticket from storage.
        
        Args:
            ticket_id: ID of ticket to load.
            
        Returns:
            Ticket instance or None if not found.
        """
        self._ensure_initialized()
        
        ticket_path = self._get_ticket_path(ticket_id)
        if not ticket_path.exists():
            return None
        
        try:
            with open(ticket_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return Ticket.from_dict(data)
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
        if not self.index_path.exists():
            return {}
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except (yaml.YAMLError, FileNotFoundError):
            return {}
    
    def _save_index(self, index: Dict[str, Dict]) -> None:
        """Save the ticket index."""
        with open(self.index_path, 'w', encoding='utf-8') as f:
            yaml.dump(index, f, default_flow_style=False, sort_keys=True)
    
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