#!/usr/bin/env python3
"""
Async agent operations for repo-tickets.

Provides parallel task assignment and non-blocking monitoring for AI agents.
"""

import asyncio
from typing import List, Dict, Optional, Set, Callable, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from .models import Agent, AgentTask, AgentTaskStatus
from .agents import AgentStorage
from .storage import TicketStorage
from .events import EventType, publish_event
from .logging_utils import get_logger, log_performance


logger = get_logger()


@dataclass
class TaskAssignment:
    """Result of a task assignment operation."""
    
    task_id: str
    agent_id: str
    ticket_id: str
    success: bool
    error: Optional[str] = None
    duration_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'agent_id': self.agent_id,
            'ticket_id': self.ticket_id,
            'success': self.success,
            'error': self.error,
            'duration_ms': self.duration_ms
        }


@dataclass
class ParallelResult:
    """Result of parallel operations."""
    
    success: bool
    total: int
    completed: int
    failed: int
    assignments: List[TaskAssignment] = field(default_factory=list)
    duration_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total == 0:
            return 0.0
        return self.completed / self.total
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'total': self.total,
            'completed': self.completed,
            'failed': self.failed,
            'success_rate': self.success_rate,
            'assignments': [a.to_dict() for a in self.assignments],
            'duration_ms': self.duration_ms
        }


@dataclass
class AgentMonitorResult:
    """Result of agent monitoring."""
    
    agent_id: str
    status: str
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    last_activity: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'active_tasks': self.active_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'metrics': self.metrics
        }


class AsyncAgentOperations:
    """
    Async operations for AI agents.
    
    Provides parallel task assignment and non-blocking monitoring.
    """
    
    def __init__(self, agent_storage: Optional[AgentStorage] = None, max_workers: int = 10):
        """
        Initialize async agent operations.
        
        Args:
            agent_storage: AgentStorage instance
            max_workers: Maximum parallel workers
        """
        self.agent_storage = agent_storage or AgentStorage()
        self.ticket_storage = self.agent_storage.ticket_storage
        self.max_workers = max_workers
    
    def assign_tasks_parallel(
        self,
        task_specs: List[Dict[str, Any]],
        max_concurrent: Optional[int] = None
    ) -> ParallelResult:
        """
        Assign multiple tasks to agents in parallel.
        
        Args:
            task_specs: List of task specifications
                Each spec: {'ticket_id': str, 'agent_id': str, 'task_type': str, 'description': str}
            max_concurrent: Maximum concurrent assignments (uses max_workers if None)
        
        Returns:
            ParallelResult with assignment details
        """
        with log_performance("assign_tasks_parallel", count=len(task_specs)):
            start_time = time.time()
            max_concurrent = max_concurrent or self.max_workers
            
            result = ParallelResult(
                success=True,
                total=len(task_specs),
                completed=0,
                failed=0
            )
            
            # Use ThreadPoolExecutor for parallel I/O operations
            with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
                # Submit all tasks
                futures = {
                    executor.submit(self._assign_single_task, spec): spec
                    for spec in task_specs
                }
                
                # Collect results as they complete
                for future in as_completed(futures):
                    spec = futures[future]
                    try:
                        assignment = future.result()
                        result.assignments.append(assignment)
                        
                        if assignment.success:
                            result.completed += 1
                            logger.log_agent_operation(
                                "task_assigned_parallel",
                                assignment.agent_id,
                                task_id=assignment.task_id,
                                ticket_id=assignment.ticket_id,
                                duration_ms=assignment.duration_ms
                            )
                        else:
                            result.failed += 1
                            logger.error(
                                "Parallel task assignment failed",
                                agent_id=spec.get('agent_id'),
                                ticket_id=spec.get('ticket_id'),
                                error=assignment.error
                            )
                    except Exception as e:
                        result.failed += 1
                        logger.error(
                            "Parallel task assignment exception",
                            spec=spec,
                            error=str(e)
                        )
            
            result.duration_ms = (time.time() - start_time) * 1000
            result.success = result.failed == 0
            
            # Publish batch event
            if result.completed > 0:
                publish_event(
                    EventType.AGENT_TASK_ASSIGNED,
                    {
                        'count': result.completed,
                        'failed': result.failed,
                        'duration_ms': result.duration_ms,
                        'parallel': True
                    }
                )
            
            return result
    
    def _assign_single_task(self, spec: Dict[str, Any]) -> TaskAssignment:
        """
        Assign a single task (thread-safe).
        
        Args:
            spec: Task specification
        
        Returns:
            TaskAssignment result
        """
        start_time = time.time()
        
        try:
            task = self.agent_storage.assign_task(
                ticket_id=spec['ticket_id'],
                agent_id=spec['agent_id'],
                task_type=spec['task_type'],
                description=spec['description'],
                priority=spec.get('priority', 'medium'),
                instructions=spec.get('instructions', '')
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            return TaskAssignment(
                task_id=task.id,
                agent_id=task.agent_id,
                ticket_id=task.ticket_id,
                success=True,
                duration_ms=duration_ms
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            return TaskAssignment(
                task_id='',
                agent_id=spec.get('agent_id', ''),
                ticket_id=spec.get('ticket_id', ''),
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )
    
    def monitor_agents_parallel(
        self,
        agent_ids: Optional[List[str]] = None
    ) -> Dict[str, AgentMonitorResult]:
        """
        Monitor multiple agents in parallel.
        
        Args:
            agent_ids: List of agent IDs to monitor (all if None)
        
        Returns:
            Dict mapping agent_id to AgentMonitorResult
        """
        with log_performance("monitor_agents_parallel"):
            # Get agent IDs to monitor
            if agent_ids is None:
                agents = self.agent_storage.list_agents()
                agent_ids = [a.id for a in agents]
            
            results = {}
            
            # Use ThreadPoolExecutor for parallel monitoring
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._monitor_single_agent, agent_id): agent_id
                    for agent_id in agent_ids
                }
                
                for future in as_completed(futures):
                    agent_id = futures[future]
                    try:
                        result = future.result()
                        results[agent_id] = result
                    except Exception as e:
                        logger.error(
                            "Failed to monitor agent",
                            agent_id=agent_id,
                            error=str(e)
                        )
            
            return results
    
    def _monitor_single_agent(self, agent_id: str) -> AgentMonitorResult:
        """
        Monitor a single agent (thread-safe).
        
        Args:
            agent_id: Agent ID
        
        Returns:
            AgentMonitorResult
        """
        agent = self.agent_storage.load_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Get task statistics
        all_tasks = self.agent_storage.list_tasks(agent_id=agent_id)
        active_tasks = [t for t in all_tasks if t.status == AgentTaskStatus.IN_PROGRESS.value]
        completed_tasks = [t for t in all_tasks if t.status == AgentTaskStatus.COMPLETED.value]
        failed_tasks = [t for t in all_tasks if t.status == AgentTaskStatus.FAILED.value]
        
        # Get last activity
        last_activity = agent.last_seen
        if all_tasks:
            task_times = [t.assigned_at for t in all_tasks] + \
                        [t.completed_at for t in all_tasks if t.completed_at]
            if task_times:
                last_activity = max(task_times)
        
        # Build metrics
        metrics = {
            'total_tasks': len(all_tasks),
            'success_rate': agent.metrics.success_rate if agent.metrics else 0.0,
            'avg_completion_time': agent.metrics.average_completion_time_minutes if agent.metrics else 0.0
        }
        
        return AgentMonitorResult(
            agent_id=agent_id,
            status=agent.status,
            active_tasks=len(active_tasks),
            completed_tasks=len(completed_tasks),
            failed_tasks=len(failed_tasks),
            last_activity=last_activity,
            metrics=metrics
        )
    
    def collect_results_parallel(
        self,
        task_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Collect results from multiple tasks in parallel.
        
        Args:
            task_ids: List of task IDs
        
        Returns:
            Dict mapping task_id to task data
        """
        with log_performance("collect_results_parallel", count=len(task_ids)):
            results = {}
            
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {
                    executor.submit(self._collect_single_result, task_id): task_id
                    for task_id in task_ids
                }
                
                for future in as_completed(futures):
                    task_id = futures[future]
                    try:
                        result = future.result()
                        results[task_id] = result
                    except Exception as e:
                        logger.error(
                            "Failed to collect task result",
                            task_id=task_id,
                            error=str(e)
                        )
                        results[task_id] = {'error': str(e)}
            
            return results
    
    def _collect_single_result(self, task_id: str) -> Dict[str, Any]:
        """
        Collect result from single task (thread-safe).
        
        Args:
            task_id: Task ID
        
        Returns:
            Task data dict
        """
        task = self.agent_storage.load_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        return {
            'task_id': task.id,
            'agent_id': task.agent_id,
            'ticket_id': task.ticket_id,
            'status': task.status,
            'task_type': task.task_type,
            'description': task.description,
            'result': task.result,
            'assigned_at': task.assigned_at.isoformat() if task.assigned_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'duration_minutes': task.duration_minutes
        }
    
    def auto_distribute_tasks(
        self,
        task_specs: List[Dict[str, Any]],
        consider_load: bool = True,
        consider_capabilities: bool = True
    ) -> ParallelResult:
        """
        Automatically distribute tasks to best available agents.
        
        Args:
            task_specs: List of task specs (without agent_id)
            consider_load: Balance based on current agent load
            consider_capabilities: Match based on agent capabilities
        
        Returns:
            ParallelResult with assignments
        """
        with log_performance("auto_distribute_tasks", count=len(task_specs)):
            # Get available agents
            agents = self.agent_storage.list_agents(status='active')
            if not agents:
                raise ValueError("No active agents available")
            
            # Assign agents to tasks
            enhanced_specs = []
            for spec in task_specs:
                agent = self._select_best_agent(
                    agents,
                    spec.get('task_type'),
                    consider_load=consider_load,
                    consider_capabilities=consider_capabilities
                )
                
                if agent:
                    spec_with_agent = spec.copy()
                    spec_with_agent['agent_id'] = agent.id
                    enhanced_specs.append(spec_with_agent)
                else:
                    logger.warning(
                        "No suitable agent found for task",
                        task_type=spec.get('task_type'),
                        ticket_id=spec.get('ticket_id')
                    )
            
            # Assign tasks in parallel
            return self.assign_tasks_parallel(enhanced_specs)
    
    def _select_best_agent(
        self,
        agents: List[Agent],
        task_type: Optional[str],
        consider_load: bool,
        consider_capabilities: bool
    ) -> Optional[Agent]:
        """
        Select best agent for a task.
        
        Args:
            agents: Available agents
            task_type: Task type
            consider_load: Balance based on load
            consider_capabilities: Match capabilities
        
        Returns:
            Best agent or None
        """
        if not agents:
            return None
        
        # Score each agent
        scored_agents = []
        for agent in agents:
            score = 0.0
            
            # Capability score
            if consider_capabilities and task_type:
                if task_type in agent.preferred_task_types:
                    score += 10.0
                
                # Check capabilities
                for cap in agent.capabilities:
                    if cap.enabled and task_type in cap.name.lower():
                        score += cap.confidence_level * 5.0
            
            # Load balancing score
            if consider_load:
                active_tasks = self.agent_storage.list_tasks(
                    agent_id=agent.id,
                    status=AgentTaskStatus.IN_PROGRESS.value
                )
                load_factor = len(active_tasks) / max(agent.max_concurrent_tasks, 1)
                score += (1.0 - load_factor) * 3.0
            
            # Success rate score
            if agent.metrics:
                score += agent.metrics.success_rate * 2.0
            
            scored_agents.append((agent, score))
        
        # Return agent with highest score
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0] if scored_agents else None


def get_async_agent_operations(
    agent_storage: Optional[AgentStorage] = None,
    max_workers: int = 10
) -> AsyncAgentOperations:
    """
    Get AsyncAgentOperations instance.
    
    Args:
        agent_storage: AgentStorage instance
        max_workers: Maximum parallel workers
    
    Returns:
        AsyncAgentOperations instance
    """
    return AsyncAgentOperations(agent_storage, max_workers)
