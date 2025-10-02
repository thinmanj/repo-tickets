#!/usr/bin/env python3
"""
VCS abstraction layer for repo-tickets.

Provides a unified interface to work with different version control systems:
- Git
- Mercurial (hg)
- Jujutsu (jj)
"""

import os
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Any


class VCSError(Exception):
    """Exception raised for VCS-related errors."""
    pass


class BaseVCS(ABC):
    """Abstract base class for version control system adapters."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
    
    @abstractmethod
    def is_repository(self) -> bool:
        """Check if the current directory is a repository of this VCS type."""
        pass
    
    @abstractmethod
    def get_current_branch(self) -> str:
        """Get the current branch name."""
        pass
    
    @abstractmethod
    def get_user_name(self) -> str:
        """Get the configured user name."""
        pass
    
    @abstractmethod
    def get_user_email(self) -> str:
        """Get the configured user email."""
        pass
    
    @abstractmethod
    def is_file_ignored(self, file_path: str) -> bool:
        """Check if a file would be ignored by VCS."""
        pass


class GitVCS(BaseVCS):
    """Git version control system adapter."""
    
    def is_repository(self) -> bool:
        return (self.repo_root / ".git").exists()
    
    def get_current_branch(self) -> str:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "main"  # fallback
    
    def get_user_name(self) -> str:
        try:
            result = subprocess.run(
                ["git", "config", "user.name"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return os.getenv("USER", "unknown")
    
    def get_user_email(self) -> str:
        try:
            result = subprocess.run(
                ["git", "config", "user.email"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return f"{self.get_user_name()}@localhost"
    
    def is_file_ignored(self, file_path: str) -> bool:
        try:
            subprocess.run(
                ["git", "check-ignore", file_path],
                cwd=self.repo_root,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError:
            return False


class MercurialVCS(BaseVCS):
    """Mercurial version control system adapter."""
    
    def is_repository(self) -> bool:
        return (self.repo_root / ".hg").exists()
    
    def get_current_branch(self) -> str:
        try:
            result = subprocess.run(
                ["hg", "branch"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "default"  # fallback
    
    def get_user_name(self) -> str:
        try:
            result = subprocess.run(
                ["hg", "config", "ui.username"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            # Mercurial returns "Name <email>", extract just the name
            username = result.stdout.strip()
            if "<" in username:
                return username.split("<")[0].strip()
            return username
        except subprocess.CalledProcessError:
            return os.getenv("USER", "unknown")
    
    def get_user_email(self) -> str:
        try:
            result = subprocess.run(
                ["hg", "config", "ui.username"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            # Mercurial returns "Name <email>", extract just the email
            username = result.stdout.strip()
            if "<" in username and ">" in username:
                return username.split("<")[1].split(">")[0]
            return f"{self.get_user_name()}@localhost"
        except subprocess.CalledProcessError:
            return f"{self.get_user_name()}@localhost"
    
    def is_file_ignored(self, file_path: str) -> bool:
        # Mercurial doesn't have a direct equivalent to git check-ignore
        # We'll implement a basic check against common patterns
        ignored_patterns = [".hg", ".hgignore"]
        return any(pattern in file_path for pattern in ignored_patterns)


class JujutsuVCS(BaseVCS):
    """Jujutsu version control system adapter."""
    
    def is_repository(self) -> bool:
        return (self.repo_root / ".jj").exists()
    
    def get_current_branch(self) -> str:
        try:
            result = subprocess.run(
                ["jj", "log", "-r", "@", "--no-graph", "-T", "branches"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            # Parse the branches output
            branches = result.stdout.strip()
            if branches and branches != "()":
                # Extract first branch name from the output
                return branches.replace("(", "").replace(")", "").split()[0]
            return "main"  # fallback
        except subprocess.CalledProcessError:
            return "main"  # fallback
    
    def get_user_name(self) -> str:
        try:
            result = subprocess.run(
                ["jj", "config", "get", "user.name"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().strip('"')
        except subprocess.CalledProcessError:
            return os.getenv("USER", "unknown")
    
    def get_user_email(self) -> str:
        try:
            result = subprocess.run(
                ["jj", "config", "get", "user.email"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().strip('"')
        except subprocess.CalledProcessError:
            return f"{self.get_user_name()}@localhost"
    
    def is_file_ignored(self, file_path: str) -> bool:
        # Jujutsu uses .gitignore format, but we'll keep it simple for now
        ignored_patterns = [".jj"]
        return any(pattern in file_path for pattern in ignored_patterns)


def detect_vcs(start_path: Optional[Path] = None) -> Optional[BaseVCS]:
    """
    Detect the version control system in use.
    
    Args:
        start_path: Path to start detection from. Defaults to current directory.
        
    Returns:
        VCS adapter instance, or None if no VCS is detected.
    """
    if start_path is None:
        start_path = Path.cwd()
    
    # Search up the directory tree for a VCS root
    current_path = start_path.resolve()
    
    while current_path != current_path.parent:
        # Check for each VCS type in order of preference
        vcs_adapters = [
            JujutsuVCS(current_path),
            GitVCS(current_path),
            MercurialVCS(current_path),
        ]
        
        for adapter in vcs_adapters:
            if adapter.is_repository():
                return adapter
        
        current_path = current_path.parent
    
    return None


def get_repository_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the repository root directory.
    
    Args:
        start_path: Path to start search from. Defaults to current directory.
        
    Returns:
        Path to repository root, or None if not in a repository.
    """
    vcs = detect_vcs(start_path)
    return vcs.repo_root if vcs else None


def ensure_in_repository() -> BaseVCS:
    """
    Ensure we're in a repository and return the VCS adapter.
    
    Raises:
        VCSError: If not in a repository.
        
    Returns:
        VCS adapter instance.
    """
    vcs = detect_vcs()
    if not vcs:
        raise VCSError(
            "Not in a repository. Please run this command from within a "
            "git, mercurial, or Jujutsu repository."
        )
    return vcs