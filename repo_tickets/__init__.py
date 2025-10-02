#!/usr/bin/env python3
"""
Repo Tickets - A CLI ticket system for VCS repositories.

A self-contained ticketing system that works with git, mercurial, 
and Jujutsu repositories without external dependencies.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .models import Ticket, Comment, TicketConfig
from .storage import TicketStorage
from .vcs import detect_vcs, ensure_in_repository, VCSError

__all__ = [
    'Ticket',
    'Comment', 
    'TicketConfig',
    'TicketStorage',
    'detect_vcs',
    'ensure_in_repository',
    'VCSError',
]