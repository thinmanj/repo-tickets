#!/usr/bin/env python3
"""
AI Agent management system for repo-tickets.

Provides storage, assignment, and coordination of AI agents for ticket work.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set, Any

from .models import (
    Agent, AgentTask, AgentStatus, AgentType, AgentTaskStatus,
    generate_agent_id
)
from .storage import TicketStorage


class AgentStorage:
    """Storage and management for AI agents and their tasks."""
    
    def __init__(self, tickets_dir: Optional[Path] = None):
        """Initialize agent storage."""
        self.ticket_storage = TicketStorage(tickets_dir)
        self.agents_dir = self.ticket_storage.tickets_dir / "agents"
        self.tasks_dir = self.ticket_storage.tickets_dir / "tasks"
        
        # Ensure directories exist
        self.agents_dir.mkdir(exist_ok=True)
        self.tasks_dir.mkdir(exist_ok=True)
    
    def is_initialized(self) -> bool:
        """Check if the agent system is initialized."""
        return self.ticket_storage.is_initialized() and self.agents_dir.exists()
    
    def save_agent(self, agent: Agent) -> None:
        """Save an agent to storage."""
        agent_file = self.agents_dir / f"{agent.id}.json"
        
        try:
            # Convert to dict and save
            data = agent.to_dict()
            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save agent {agent.id}: {e}")
    
    def load_agent(self, agent_id: str) -> Optional[Agent]:
        """Load an agent from storage."""
        agent_file = self.agents_dir / f"{agent_id}.json"
        
        if not agent_file.exists():
            return None
        
        try:
            with open(agent_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Agent.from_dict(data)
        except Exception as e:
            raise RuntimeError(f"Failed to load agent {agent_id}: {e}")
    
    def list_agents(self, status: Optional[str] = None) -> List[Agent]:
        """List all agents, optionally filtered by status."""
        agents = []
        
        for agent_file in self.agents_dir.glob("*.json"):
            try:
                agent = self.load_agent(agent_file.stem)
                if agent and (status is None or agent.status == status):
                    agents.append(agent)
            except Exception:
                # Skip corrupted files
                continue
        
        return sorted(agents, key=lambda a: a.created_at)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent from storage."""
        agent_file = self.agents_dir / f"{agent_id}.json"
        
        if agent_file.exists():
            # First check if agent has active tasks
            active_tasks = self.list_tasks(agent_id=agent_id, status=AgentTaskStatus.IN_PROGRESS.value)
            if active_tasks:
                raise ValueError(f"Cannot delete agent {agent_id} with active tasks")
            
            agent_file.unlink()
            return True
        return False
    
    def generate_unique_agent_id(self, name: str) -> str:
        """Generate a unique agent ID."""
        existing_ids = {agent.id for agent in self.list_agents()}
        return generate_agent_id(name, existing_ids)
    
    def save_task(self, task: AgentTask) -> None:
        """Save an agent task to storage."""
        task_file = self.tasks_dir / f"{task.id}.json"
        
        try:
            # Convert to dict for serialization
            data = task.__dict__.copy()
            
            # Convert datetime objects to ISO strings
            for field in ['assigned_at', 'started_at', 'completed_at']:
                if hasattr(task, field):
                    value = getattr(task, field)
                    if isinstance(value, datetime):
                        data[field] = value.isoformat()
            
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save task {task.id}: {e}")
    
    def load_task(self, task_id: str) -> Optional[AgentTask]:
        """Load an agent task from storage."""
        task_file = self.tasks_dir / f"{task_id}.json"
        
        if not task_file.exists():
            return None
        
        try:
            with open(task_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert ISO strings back to datetime objects
            for field in ['assigned_at', 'started_at', 'completed_at']:
                if field in data and isinstance(data[field], str):
                    data[field] = datetime.fromisoformat(data[field])
            
            return AgentTask(**data)
        except Exception as e:
            raise RuntimeError(f"Failed to load task {task_id}: {e}")
    
    def list_tasks(
        self,
        agent_id: Optional[str] = None,
        ticket_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[AgentTask]:
        """List agent tasks with optional filtering."""
        tasks = []
        
        for task_file in self.tasks_dir.glob("*.json"):
            try:
                task = self.load_task(task_file.stem)
                if not task:
                    continue
                
                # Apply filters
                if agent_id and task.agent_id != agent_id:
                    continue
                if ticket_id and task.ticket_id != ticket_id:
                    continue
                if status and task.status != status:
                    continue
                
                tasks.append(task)
            except Exception:
                # Skip corrupted files
                continue
        
        return sorted(tasks, key=lambda t: t.assigned_at, reverse=True)
    
    def delete_task(self, task_id: str) -> bool:
        """Delete an agent task from storage."""
        task_file = self.tasks_dir / f"{task_id}.json"
        
        if task_file.exists():
            task_file.unlink()
            return True
        return False
    
    def create_agent(
        self,
        name: str,
        description: str = "",
        agent_type: str = AgentType.GENERAL.value,
        capabilities: List[Dict[str, Any]] = None,
        **kwargs
    ) -> Agent:
        """Create a new AI agent."""
        agent_id = self.generate_unique_agent_id(name)
        
        agent = Agent(
            id=agent_id,
            name=name,
            description=description,
            agent_type=agent_type,
            **kwargs
        )
        
        # Add capabilities if provided
        if capabilities:
            for cap in capabilities:
                agent.add_capability(**cap)
        
        self.save_agent(agent)
        return agent
    
    def assign_task(
        self,
        ticket_id: str,
        agent_id: str,
        task_type: str,
        description: str,
        instructions: str = "",
        priority: str = "medium",
        **kwargs
    ) -> AgentTask:
        """Assign a task to an agent."""
        # Verify agent exists and is available
        agent = self.load_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        if not agent.is_available():
            raise ValueError(f"Agent {agent.name} is not available for new tasks")
        
        if not agent.can_handle_task(task_type):
            raise ValueError(f"Agent {agent.name} cannot handle task type: {task_type}")
        
        # Verify ticket exists
        ticket = self.ticket_storage.load_ticket(ticket_id)
        if not ticket:
            raise ValueError(f"Ticket {ticket_id} not found")
        
        # Create task
        task_id = str(uuid.uuid4())[:8].upper()
        task = AgentTask(
            id=task_id,
            ticket_id=ticket_id,
            agent_id=agent_id,
            task_type=task_type,
            description=description,
            instructions=instructions,
            priority=priority,
            **kwargs
        )
        
        # Update agent and ticket
        agent.assign_task(task_id)
        ticket.add_agent_task(task_id)
        
        # If ticket doesn't have an assigned agent, assign this one
        if not ticket.assigned_agent:
            ticket.assign_agent(agent_id)
        
        # Save everything
        self.save_task(task)
        self.save_agent(agent)
        self.ticket_storage.save_ticket(ticket)
        
        return task
    
    def start_task(self, task_id: str) -> AgentTask:
        """Start a task execution."""
        task = self.load_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.start_task()
        
        # Update agent metrics
        agent = self.load_agent(task.agent_id)
        if agent:
            agent.metrics.last_activity = datetime.now()
            self.save_agent(agent)
        
        self.save_task(task)
        return task
    
    def complete_task(
        self,
        task_id: str,
        output: str = "",
        artifacts: List[str] = None
    ) -> AgentTask:
        """Complete a task."""
        task = self.load_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.complete_task(output, artifacts)
        
        # Update agent metrics
        agent = self.load_agent(task.agent_id)
        if agent:
            agent.metrics.tasks_completed += 1
            agent.metrics.last_activity = datetime.now()
            agent.metrics.update_success_rate()
            agent.unassign_task(task_id)
            
            # Update execution time
            if task.duration_minutes:
                agent.metrics.total_execution_time_minutes += task.duration_minutes
            
            self.save_agent(agent)
        
        self.save_task(task)
        return task
    
    def fail_task(self, task_id: str, error_message: str) -> AgentTask:
        """Fail a task with an error message."""
        task = self.load_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        task.fail_task(error_message)
        
        # Update agent metrics
        agent = self.load_agent(task.agent_id)
        if agent:
            agent.metrics.tasks_failed += 1
            agent.metrics.last_activity = datetime.now()
            agent.metrics.update_success_rate()
            agent.unassign_task(task_id)
            
            # Update execution time
            if task.duration_minutes:
                agent.metrics.total_execution_time_minutes += task.duration_minutes
            
            self.save_agent(agent)
        
        self.save_task(task)
        return task
    
    def get_agent_stats(self, agent_id: str) -> Dict[str, Any]:
        """Get comprehensive statistics for an agent."""
        agent = self.load_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        all_tasks = self.list_tasks(agent_id=agent_id)
        
        stats = {
            'agent': agent,
            'total_tasks': len(all_tasks),
            'active_tasks': len([t for t in all_tasks if t.status == AgentTaskStatus.IN_PROGRESS.value]),
            'completed_tasks': len([t for t in all_tasks if t.status == AgentTaskStatus.COMPLETED.value]),
            'failed_tasks': len([t for t in all_tasks if t.status == AgentTaskStatus.FAILED.value]),
            'task_types': {},
            'recent_tasks': sorted(all_tasks, key=lambda t: t.assigned_at, reverse=True)[:10]
        }
        
        # Task type breakdown
        for task in all_tasks:
            task_type = task.task_type
            if task_type not in stats['task_types']:
                stats['task_types'][task_type] = {'total': 0, 'completed': 0, 'failed': 0}
            
            stats['task_types'][task_type]['total'] += 1
            if task.status == AgentTaskStatus.COMPLETED.value:
                stats['task_types'][task_type]['completed'] += 1
            elif task.status == AgentTaskStatus.FAILED.value:
                stats['task_types'][task_type]['failed'] += 1
        
        return stats
    
    def find_best_agent_for_task(self, task_type: str, priority: str = "medium") -> Optional[Agent]:
        """Find the best available agent for a specific task type."""
        available_agents = [
            agent for agent in self.list_agents(status=AgentStatus.ACTIVE.value)
            if agent.is_available() and agent.can_handle_task(task_type)
        ]
        
        if not available_agents:
            return None
        
        # Score agents based on their capabilities and performance
        def score_agent(agent: Agent) -> float:
            score = 0.0
            
            # Base availability score
            load_factor = len(agent.active_tasks) / agent.max_concurrent_tasks
            score += (1.0 - load_factor) * 10  # Lower load = higher score
            
            # Success rate
            score += agent.metrics.success_rate * 20
            
            # Task type match
            if task_type in agent.preferred_task_types:
                score += 15
            
            # Capability confidence
            for capability in agent.capabilities:
                if capability.enabled and task_type.lower() in capability.name.lower():
                    score += capability.confidence_level * 10
            
            return score
        
        # Return agent with highest score
        return max(available_agents, key=score_agent)
    
    def auto_assign_task(
        self,
        ticket_id: str,
        task_type: str,
        description: str,
        **kwargs
    ) -> Optional[AgentTask]:
        """Automatically assign a task to the best available agent."""
        agent = self.find_best_agent_for_task(task_type, kwargs.get('priority', 'medium'))
        
        if not agent:
            return None
        
        return self.assign_task(
            ticket_id=ticket_id,
            agent_id=agent.id,
            task_type=task_type,
            description=description,
            **kwargs
        )