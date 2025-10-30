#!/usr/bin/env python3
"""
Workflow engine for repo-tickets.

Orchestrates multi-step workflows with task dependencies and automatic progression.
"""

from typing import List, Dict, Optional, Set, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import time

from .models import Ticket, Agent
from .agents import AgentStorage
from .storage import TicketStorage
from .async_agents import get_async_agent_operations
from .events import EventType, publish_event, subscribe_event
from .logging_utils import get_logger, log_performance


logger = get_logger()


class StepStatus(Enum):
    """Status of a workflow step."""
    PENDING = "pending"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStatus(Enum):
    """Status of entire workflow."""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""
    
    id: str
    name: str
    description: str
    task_type: str
    agent_id: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    status: str = StepStatus.PENDING.value
    task_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    # Conditional execution
    condition: Optional[Callable[[Dict[str, Any]], bool]] = None
    retry_count: int = 0
    max_retries: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'task_type': self.task_type,
            'agent_id': self.agent_id,
            'depends_on': self.depends_on,
            'status': self.status,
            'task_id': self.task_id,
            'result': self.result,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class Workflow:
    """Represents a complete workflow."""
    
    id: str
    name: str
    description: str
    ticket_id: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: str = WorkflowStatus.CREATED.value
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ticket_id': self.ticket_id,
            'steps': [step.to_dict() for step in self.steps],
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'context': self.context
        }
    
    @property
    def progress_percentage(self) -> float:
        """Calculate workflow progress percentage."""
        if not self.steps:
            return 0.0
        completed = len([s for s in self.steps if s.status == StepStatus.COMPLETED.value])
        return (completed / len(self.steps)) * 100
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Calculate total duration."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class WorkflowEngine:
    """
    Engine for executing multi-step workflows.
    
    Features:
    - Task dependencies and ordering
    - Automatic step progression
    - Conditional branching
    - Parallel step execution
    - Retry logic
    - Event-driven coordination
    """
    
    def __init__(
        self,
        agent_storage: Optional[AgentStorage] = None,
        ticket_storage: Optional[TicketStorage] = None
    ):
        """
        Initialize workflow engine.
        
        Args:
            agent_storage: AgentStorage instance
            ticket_storage: TicketStorage instance
        """
        self.agent_storage = agent_storage or AgentStorage()
        self.ticket_storage = ticket_storage or TicketStorage()
        self.async_ops = get_async_agent_operations(self.agent_storage)
        
        self.active_workflows: Dict[str, Workflow] = {}
        
        # Subscribe to task completion events
        subscribe_event(EventType.AGENT_TASK_COMPLETED, self._on_task_completed)
        subscribe_event(EventType.AGENT_TASK_FAILED, self._on_task_failed)
    
    def create_workflow(
        self,
        name: str,
        description: str,
        ticket_id: str,
        steps: List[Dict[str, Any]]
    ) -> Workflow:
        """
        Create a new workflow.
        
        Args:
            name: Workflow name
            description: Workflow description
            ticket_id: Associated ticket ID
            steps: List of step specifications
        
        Returns:
            Created Workflow
        """
        workflow_id = f"WF-{uuid.uuid4().hex[:8].upper()}"
        
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description,
            ticket_id=ticket_id
        )
        
        # Create steps
        for step_spec in steps:
            step = WorkflowStep(
                id=f"{workflow_id}-{step_spec['name'].replace(' ', '-')}",
                name=step_spec['name'],
                description=step_spec.get('description', ''),
                task_type=step_spec['task_type'],
                agent_id=step_spec.get('agent_id'),
                depends_on=step_spec.get('depends_on', []),
                max_retries=step_spec.get('max_retries', 0)
            )
            workflow.steps.append(step)
        
        self.active_workflows[workflow_id] = workflow
        
        logger.info(
            "Workflow created",
            workflow_id=workflow_id,
            ticket_id=ticket_id,
            steps=len(workflow.steps)
        )
        
        publish_event(EventType.SYSTEM_CACHE_CLEARED, {
            'workflow_id': workflow_id,
            'name': name,
            'ticket_id': ticket_id,
            'steps': len(workflow.steps)
        })
        
        return workflow
    
    def start_workflow(self, workflow_id: str) -> None:
        """
        Start executing a workflow.
        
        Args:
            workflow_id: Workflow ID
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow.status = WorkflowStatus.RUNNING.value
        workflow.started_at = datetime.now()
        
        logger.info(
            "Workflow started",
            workflow_id=workflow_id,
            ticket_id=workflow.ticket_id
        )
        
        # Execute ready steps
        self._execute_ready_steps(workflow)
    
    def _execute_ready_steps(self, workflow: Workflow) -> None:
        """
        Execute all steps that are ready.
        
        Args:
            workflow: Workflow to process
        """
        ready_steps = self._get_ready_steps(workflow)
        
        if not ready_steps:
            # Check if workflow is complete
            if self._is_workflow_complete(workflow):
                self._complete_workflow(workflow)
            return
        
        # Prepare task specs for parallel execution
        task_specs = []
        for step in ready_steps:
            step.status = StepStatus.IN_PROGRESS.value
            step.started_at = datetime.now()
            
            # Auto-assign agent if not specified
            if not step.agent_id:
                agent = self._select_agent_for_step(step)
                if agent:
                    step.agent_id = agent.id
                else:
                    logger.warning(
                        "No suitable agent found for step",
                        workflow_id=workflow.id,
                        step_id=step.id
                    )
                    step.status = StepStatus.FAILED.value
                    step.error = "No suitable agent available"
                    continue
            
            task_specs.append({
                'ticket_id': workflow.ticket_id,
                'agent_id': step.agent_id,
                'task_type': step.task_type,
                'description': f"{workflow.name}: {step.description}",
                'priority': 'high',
                'instructions': f"Workflow: {workflow.id}, Step: {step.id}"
            })
        
        # Execute tasks in parallel
        if task_specs:
            result = self.async_ops.assign_tasks_parallel(task_specs)
            
            # Map task IDs back to steps
            for i, assignment in enumerate(result.assignments):
                if assignment.success and i < len(ready_steps):
                    ready_steps[i].task_id = assignment.task_id
                    
                    logger.log_agent_operation(
                        "workflow_step_started",
                        assignment.agent_id,
                        workflow_id=workflow.id,
                        step_id=ready_steps[i].id,
                        task_id=assignment.task_id
                    )
    
    def _get_ready_steps(self, workflow: Workflow) -> List[WorkflowStep]:
        """
        Get all steps that are ready to execute.
        
        Args:
            workflow: Workflow to check
        
        Returns:
            List of ready steps
        """
        ready_steps = []
        
        for step in workflow.steps:
            if step.status != StepStatus.PENDING.value:
                continue
            
            # Check if dependencies are satisfied
            dependencies_met = True
            for dep_id in step.depends_on:
                dep_step = self._find_step(workflow, dep_id)
                if not dep_step or dep_step.status != StepStatus.COMPLETED.value:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                # Check condition if present
                if step.condition:
                    try:
                        if not step.condition(workflow.context):
                            step.status = StepStatus.SKIPPED.value
                            continue
                    except Exception as e:
                        logger.error(
                            "Step condition evaluation failed",
                            workflow_id=workflow.id,
                            step_id=step.id,
                            error=str(e)
                        )
                        continue
                
                ready_steps.append(step)
        
        return ready_steps
    
    def _find_step(self, workflow: Workflow, step_id: str) -> Optional[WorkflowStep]:
        """Find step by ID."""
        for step in workflow.steps:
            if step.id == step_id or step.name == step_id:
                return step
        return None
    
    def _is_workflow_complete(self, workflow: Workflow) -> bool:
        """Check if workflow is complete."""
        for step in workflow.steps:
            if step.status in [StepStatus.PENDING.value, StepStatus.IN_PROGRESS.value, StepStatus.READY.value]:
                return False
        return True
    
    def _complete_workflow(self, workflow: Workflow) -> None:
        """Mark workflow as complete."""
        workflow.status = WorkflowStatus.COMPLETED.value
        workflow.completed_at = datetime.now()
        
        logger.info(
            "Workflow completed",
            workflow_id=workflow.id,
            ticket_id=workflow.ticket_id,
            duration_seconds=workflow.duration_seconds,
            progress=workflow.progress_percentage
        )
        
        publish_event(EventType.SYSTEM_INDEX_REBUILT, {
            'workflow_id': workflow.id,
            'ticket_id': workflow.ticket_id,
            'status': workflow.status,
            'duration_seconds': workflow.duration_seconds
        })
    
    def _select_agent_for_step(self, step: WorkflowStep) -> Optional[Agent]:
        """
        Select best agent for a step.
        
        Args:
            step: Workflow step
        
        Returns:
            Selected agent or None
        """
        agents = self.agent_storage.list_agents(status='active')
        if not agents:
            return None
        
        # Score agents
        scored_agents = []
        for agent in agents:
            score = 0.0
            
            # Capability match
            if step.task_type in agent.preferred_task_types:
                score += 10.0
            
            for cap in agent.capabilities:
                if cap.enabled and step.task_type in cap.name.lower():
                    score += cap.confidence_level * 5.0
            
            # Success rate
            if agent.metrics:
                score += agent.metrics.success_rate * 3.0
            
            scored_agents.append((agent, score))
        
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0] if scored_agents else None
    
    def _on_task_completed(self, event: Any) -> None:
        """Handle task completion event."""
        task_id = event.data.get('task_id')
        if not task_id:
            return
        
        # Find workflow and step for this task
        for workflow in self.active_workflows.values():
            for step in workflow.steps:
                if step.task_id == task_id:
                    step.status = StepStatus.COMPLETED.value
                    step.completed_at = datetime.now()
                    step.result = event.data.get('result')
                    
                    logger.info(
                        "Workflow step completed",
                        workflow_id=workflow.id,
                        step_id=step.id,
                        duration_seconds=step.duration_seconds
                    )
                    
                    # Update workflow context with step result
                    if step.result:
                        workflow.context[step.id] = step.result
                    
                    # Execute next ready steps
                    self._execute_ready_steps(workflow)
                    return
    
    def _on_task_failed(self, event: Any) -> None:
        """Handle task failure event."""
        task_id = event.data.get('task_id')
        if not task_id:
            return
        
        # Find workflow and step for this task
        for workflow in self.active_workflows.values():
            for step in workflow.steps:
                if step.task_id == task_id:
                    # Retry logic
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        step.status = StepStatus.PENDING.value
                        step.task_id = None
                        
                        logger.warning(
                            "Retrying failed step",
                            workflow_id=workflow.id,
                            step_id=step.id,
                            retry=step.retry_count,
                            max_retries=step.max_retries
                        )
                        
                        # Retry
                        self._execute_ready_steps(workflow)
                    else:
                        step.status = StepStatus.FAILED.value
                        step.error = event.data.get('error', 'Unknown error')
                        step.completed_at = datetime.now()
                        
                        logger.error(
                            "Workflow step failed",
                            workflow_id=workflow.id,
                            step_id=step.id,
                            error=step.error
                        )
                        
                        # Mark workflow as failed
                        workflow.status = WorkflowStatus.FAILED.value
                    return
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow status.
        
        Args:
            workflow_id: Workflow ID
        
        Returns:
            Workflow status dict
        """
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        return workflow.to_dict()
    
    def pause_workflow(self, workflow_id: str) -> None:
        """Pause a running workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.PAUSED.value
            logger.info("Workflow paused", workflow_id=workflow_id)
    
    def resume_workflow(self, workflow_id: str) -> None:
        """Resume a paused workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if workflow and workflow.status == WorkflowStatus.PAUSED.value:
            workflow.status = WorkflowStatus.RUNNING.value
            logger.info("Workflow resumed", workflow_id=workflow_id)
            self._execute_ready_steps(workflow)
    
    def cancel_workflow(self, workflow_id: str) -> None:
        """Cancel a workflow."""
        workflow = self.active_workflows.get(workflow_id)
        if workflow:
            workflow.status = WorkflowStatus.CANCELLED.value
            workflow.completed_at = datetime.now()
            logger.info("Workflow cancelled", workflow_id=workflow_id)


def get_workflow_engine(
    agent_storage: Optional[AgentStorage] = None,
    ticket_storage: Optional[TicketStorage] = None
) -> WorkflowEngine:
    """
    Get WorkflowEngine instance.
    
    Args:
        agent_storage: AgentStorage instance
        ticket_storage: TicketStorage instance
    
    Returns:
        WorkflowEngine instance
    """
    return WorkflowEngine(agent_storage, ticket_storage)


# Workflow Templates

def create_feature_development_workflow(
    ticket_id: str,
    engine: WorkflowEngine
) -> Workflow:
    """Create a feature development workflow."""
    steps = [
        {
            'name': 'requirements',
            'description': 'Analyze requirements and create specifications',
            'task_type': 'analysis',
            'depends_on': []
        },
        {
            'name': 'design',
            'description': 'Design technical architecture',
            'task_type': 'design',
            'depends_on': ['requirements']
        },
        {
            'name': 'implementation',
            'description': 'Implement feature code',
            'task_type': 'code',
            'depends_on': ['design']
        },
        {
            'name': 'testing',
            'description': 'Write and execute tests',
            'task_type': 'test',
            'depends_on': ['implementation']
        },
        {
            'name': 'review',
            'description': 'Code review',
            'task_type': 'review',
            'depends_on': ['testing']
        }
    ]
    
    return engine.create_workflow(
        name="Feature Development",
        description="Complete feature development workflow",
        ticket_id=ticket_id,
        steps=steps
    )


def create_bug_fix_workflow(
    ticket_id: str,
    engine: WorkflowEngine
) -> Workflow:
    """Create a bug fix workflow."""
    steps = [
        {
            'name': 'reproduce',
            'description': 'Reproduce the bug',
            'task_type': 'test',
            'depends_on': []
        },
        {
            'name': 'diagnose',
            'description': 'Diagnose root cause',
            'task_type': 'analysis',
            'depends_on': ['reproduce']
        },
        {
            'name': 'fix',
            'description': 'Implement fix',
            'task_type': 'code',
            'depends_on': ['diagnose']
        },
        {
            'name': 'verify',
            'description': 'Verify fix resolves issue',
            'task_type': 'test',
            'depends_on': ['fix']
        }
    ]
    
    return engine.create_workflow(
        name="Bug Fix",
        description="Bug fix and verification workflow",
        ticket_id=ticket_id,
        steps=steps
    )
