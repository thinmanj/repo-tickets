#!/usr/bin/env python3
"""
Agent learning system for repo-tickets.

Tracks agent performance by task type and provides ML-based smart selection.
"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import json
from pathlib import Path

from .models import Agent, AgentTask, AgentTaskStatus
from .agents import AgentStorage
from .logging_utils import get_logger


logger = get_logger()


@dataclass
class TaskTypePerformance:
    """Performance metrics for a specific task type."""
    
    task_type: str
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_duration_minutes: float = 0.0
    success_rate: float = 0.0
    avg_duration_minutes: float = 0.0
    
    def update_from_task(self, task: AgentTask) -> None:
        """Update metrics from a completed task."""
        self.total_tasks += 1
        
        if task.status == AgentTaskStatus.COMPLETED.value:
            self.completed_tasks += 1
            if task.duration_minutes:
                self.total_duration_minutes += task.duration_minutes
        elif task.status == AgentTaskStatus.FAILED.value:
            self.failed_tasks += 1
        
        # Recalculate derived metrics
        if self.total_tasks > 0:
            self.success_rate = self.completed_tasks / self.total_tasks
        
        if self.completed_tasks > 0:
            self.avg_duration_minutes = self.total_duration_minutes / self.completed_tasks
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'task_type': self.task_type,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'total_duration_minutes': self.total_duration_minutes,
            'success_rate': self.success_rate,
            'avg_duration_minutes': self.avg_duration_minutes
        }


@dataclass
class AgentPerformanceProfile:
    """Complete performance profile for an agent."""
    
    agent_id: str
    agent_name: str
    task_type_performance: Dict[str, TaskTypePerformance] = field(default_factory=dict)
    overall_success_rate: float = 0.0
    total_tasks: int = 0
    preferred_task_types: List[str] = field(default_factory=list)
    weak_task_types: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def get_or_create_task_type(self, task_type: str) -> TaskTypePerformance:
        """Get or create performance metrics for a task type."""
        if task_type not in self.task_type_performance:
            self.task_type_performance[task_type] = TaskTypePerformance(task_type=task_type)
        return self.task_type_performance[task_type]
    
    def update_overall_metrics(self) -> None:
        """Update overall metrics from task type metrics."""
        total_completed = sum(p.completed_tasks for p in self.task_type_performance.values())
        total_tasks = sum(p.total_tasks for p in self.task_type_performance.values())
        
        self.total_tasks = total_tasks
        if total_tasks > 0:
            self.overall_success_rate = total_completed / total_tasks
        
        # Identify preferred task types (>80% success rate, >3 tasks)
        self.preferred_task_types = [
            task_type for task_type, perf in self.task_type_performance.items()
            if perf.success_rate > 0.8 and perf.total_tasks >= 3
        ]
        
        # Identify weak task types (<50% success rate, >3 tasks)
        self.weak_task_types = [
            task_type for task_type, perf in self.task_type_performance.items()
            if perf.success_rate < 0.5 and perf.total_tasks >= 3
        ]
        
        self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'task_type_performance': {
                k: v.to_dict() for k, v in self.task_type_performance.items()
            },
            'overall_success_rate': self.overall_success_rate,
            'total_tasks': self.total_tasks,
            'preferred_task_types': self.preferred_task_types,
            'weak_task_types': self.weak_task_types,
            'last_updated': self.last_updated.isoformat()
        }


class AgentLearningSystem:
    """
    System for tracking agent performance and learning optimal assignments.
    
    Features:
    - Track performance by task type
    - Identify agent strengths and weaknesses
    - Smart agent selection based on historical performance
    - Learning from past assignments
    """
    
    def __init__(self, agent_storage: Optional[AgentStorage] = None):
        """
        Initialize learning system.
        
        Args:
            agent_storage: AgentStorage instance
        """
        self.agent_storage = agent_storage or AgentStorage()
        self.profiles: Dict[str, AgentPerformanceProfile] = {}
        
        # Load existing profiles
        self._load_profiles()
    
    def _get_profiles_path(self) -> Path:
        """Get path to profiles storage."""
        return self.agent_storage.agents_dir / "learning_profiles.json"
    
    def _load_profiles(self) -> None:
        """Load performance profiles from disk."""
        profiles_path = self._get_profiles_path()
        
        if not profiles_path.exists():
            return
        
        try:
            with open(profiles_path, 'r') as f:
                data = json.load(f)
            
            for agent_id, profile_data in data.items():
                profile = AgentPerformanceProfile(
                    agent_id=profile_data['agent_id'],
                    agent_name=profile_data['agent_name'],
                    overall_success_rate=profile_data['overall_success_rate'],
                    total_tasks=profile_data['total_tasks'],
                    preferred_task_types=profile_data['preferred_task_types'],
                    weak_task_types=profile_data['weak_task_types'],
                    last_updated=datetime.fromisoformat(profile_data['last_updated'])
                )
                
                # Reconstruct task type performance
                for task_type, perf_data in profile_data['task_type_performance'].items():
                    perf = TaskTypePerformance(
                        task_type=perf_data['task_type'],
                        total_tasks=perf_data['total_tasks'],
                        completed_tasks=perf_data['completed_tasks'],
                        failed_tasks=perf_data['failed_tasks'],
                        total_duration_minutes=perf_data['total_duration_minutes'],
                        success_rate=perf_data['success_rate'],
                        avg_duration_minutes=perf_data['avg_duration_minutes']
                    )
                    profile.task_type_performance[task_type] = perf
                
                self.profiles[agent_id] = profile
            
            logger.info("Loaded agent learning profiles", count=len(self.profiles))
            
        except Exception as e:
            logger.error("Failed to load learning profiles", error=str(e))
    
    def _save_profiles(self) -> None:
        """Save performance profiles to disk."""
        profiles_path = self._get_profiles_path()
        
        try:
            data = {
                agent_id: profile.to_dict()
                for agent_id, profile in self.profiles.items()
            }
            
            with open(profiles_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Saved agent learning profiles", count=len(self.profiles))
            
        except Exception as e:
            logger.error("Failed to save learning profiles", error=str(e))
    
    def update_from_task(self, task: AgentTask) -> None:
        """
        Update learning data from a completed task.
        
        Args:
            task: Completed or failed task
        """
        if task.status not in [AgentTaskStatus.COMPLETED.value, AgentTaskStatus.FAILED.value]:
            return
        
        # Get or create profile
        if task.agent_id not in self.profiles:
            agent = self.agent_storage.load_agent(task.agent_id)
            if not agent:
                return
            
            self.profiles[task.agent_id] = AgentPerformanceProfile(
                agent_id=task.agent_id,
                agent_name=agent.name
            )
        
        profile = self.profiles[task.agent_id]
        
        # Update task type performance
        task_type_perf = profile.get_or_create_task_type(task.task_type)
        task_type_perf.update_from_task(task)
        
        # Update overall metrics
        profile.update_overall_metrics()
        
        # Save profiles
        self._save_profiles()
        
        logger.info(
            "Updated agent learning profile",
            agent_id=task.agent_id,
            task_type=task.task_type,
            status=task.status,
            success_rate=task_type_perf.success_rate
        )
    
    def get_agent_profile(self, agent_id: str) -> Optional[AgentPerformanceProfile]:
        """Get performance profile for an agent."""
        return self.profiles.get(agent_id)
    
    def rebuild_all_profiles(self) -> int:
        """
        Rebuild all agent profiles from historical tasks.
        
        Returns:
            Number of profiles rebuilt
        """
        logger.info("Rebuilding agent learning profiles")
        
        self.profiles.clear()
        
        # Get all tasks
        all_tasks = self.agent_storage.list_tasks()
        
        # Group by agent
        tasks_by_agent = defaultdict(list)
        for task in all_tasks:
            if task.status in [AgentTaskStatus.COMPLETED.value, AgentTaskStatus.FAILED.value]:
                tasks_by_agent[task.agent_id].append(task)
        
        # Build profiles
        for agent_id, tasks in tasks_by_agent.items():
            agent = self.agent_storage.load_agent(agent_id)
            if not agent:
                continue
            
            profile = AgentPerformanceProfile(
                agent_id=agent_id,
                agent_name=agent.name
            )
            
            for task in tasks:
                task_type_perf = profile.get_or_create_task_type(task.task_type)
                task_type_perf.update_from_task(task)
            
            profile.update_overall_metrics()
            self.profiles[agent_id] = profile
        
        self._save_profiles()
        
        logger.info("Rebuilt agent learning profiles", count=len(self.profiles))
        
        return len(self.profiles)


class SmartAgentSelector:
    """
    ML-based agent selection using historical performance data.
    
    Selects optimal agent for a task based on:
    - Historical success rate for task type
    - Average completion time
    - Current workload
    - Recent performance trends
    """
    
    def __init__(
        self,
        learning_system: AgentLearningSystem,
        agent_storage: Optional[AgentStorage] = None
    ):
        """
        Initialize smart selector.
        
        Args:
            learning_system: AgentLearningSystem instance
            agent_storage: AgentStorage instance
        """
        self.learning_system = learning_system
        self.agent_storage = agent_storage or AgentStorage()
    
    def select_agent(
        self,
        task_type: str,
        available_agents: Optional[List[Agent]] = None,
        consider_workload: bool = True
    ) -> Optional[Agent]:
        """
        Select best agent for a task using ML-based scoring.
        
        Args:
            task_type: Type of task
            available_agents: List of available agents (active agents if None)
            consider_workload: Factor in current workload
        
        Returns:
            Selected agent or None
        """
        if available_agents is None:
            available_agents = self.agent_storage.list_agents(status='active')
        
        if not available_agents:
            return None
        
        # Score each agent
        scored_agents = []
        
        for agent in available_agents:
            score = self._score_agent(agent, task_type, consider_workload)
            scored_agents.append((agent, score))
            
            logger.debug(
                "Agent scored for task",
                agent_id=agent.id,
                task_type=task_type,
                score=score
            )
        
        # Sort by score (descending)
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        selected = scored_agents[0][0] if scored_agents else None
        
        if selected:
            logger.info(
                "Agent selected by ML",
                agent_id=selected.id,
                task_type=task_type,
                score=scored_agents[0][1]
            )
        
        return selected
    
    def _score_agent(
        self,
        agent: Agent,
        task_type: str,
        consider_workload: bool
    ) -> float:
        """
        Score an agent for a specific task type.
        
        Args:
            agent: Agent to score
            task_type: Task type
            consider_workload: Consider current workload
        
        Returns:
            Score (higher is better)
        """
        score = 0.0
        
        # Get learning profile
        profile = self.learning_system.get_agent_profile(agent.id)
        
        if profile:
            # Historical performance for this task type (weight: 40)
            if task_type in profile.task_type_performance:
                perf = profile.task_type_performance[task_type]
                
                # Success rate (0-20 points)
                score += perf.success_rate * 20.0
                
                # Speed bonus for fast completion (0-10 points)
                if perf.avg_duration_minutes > 0:
                    # Inverse relationship: faster = higher score
                    speed_score = 10.0 / (1.0 + perf.avg_duration_minutes / 60.0)
                    score += speed_score
                
                # Experience bonus (0-10 points)
                experience_score = min(perf.total_tasks / 10.0, 1.0) * 10.0
                score += experience_score
            
            # Overall success rate (weight: 10)
            score += profile.overall_success_rate * 10.0
            
            # Preferred task type bonus (weight: 15)
            if task_type in profile.preferred_task_types:
                score += 15.0
            
            # Weak task type penalty (weight: -10)
            if task_type in profile.weak_task_types:
                score -= 10.0
        
        # Agent capabilities (weight: 15)
        if task_type in agent.preferred_task_types:
            score += 10.0
        
        for cap in agent.capabilities:
            if cap.enabled and task_type.lower() in cap.name.lower():
                score += cap.confidence_level * 5.0
        
        # Current workload (weight: 10)
        if consider_workload:
            active_tasks = self.agent_storage.list_tasks(
                agent_id=agent.id,
                status=AgentTaskStatus.IN_PROGRESS.value
            )
            load_factor = len(active_tasks) / max(agent.max_concurrent_tasks, 1)
            
            # Less loaded agents get higher scores
            workload_score = (1.0 - load_factor) * 10.0
            score += workload_score
        
        return score
    
    def get_recommendations(
        self,
        task_type: str,
        top_n: int = 3
    ) -> List[Tuple[Agent, float, str]]:
        """
        Get top N agent recommendations with explanations.
        
        Args:
            task_type: Task type
            top_n: Number of recommendations
        
        Returns:
            List of (agent, score, explanation) tuples
        """
        agents = self.agent_storage.list_agents(status='active')
        
        scored_agents = []
        for agent in agents:
            score = self._score_agent(agent, task_type, consider_workload=True)
            explanation = self._explain_score(agent, task_type, score)
            scored_agents.append((agent, score, explanation))
        
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        
        return scored_agents[:top_n]
    
    def _explain_score(self, agent: Agent, task_type: str, score: float) -> str:
        """Generate explanation for agent score."""
        profile = self.learning_system.get_agent_profile(agent.id)
        
        reasons = []
        
        if profile and task_type in profile.task_type_performance:
            perf = profile.task_type_performance[task_type]
            reasons.append(f"{perf.success_rate:.0%} success rate on {task_type}")
            reasons.append(f"avg {perf.avg_duration_minutes:.0f}min completion time")
        
        if profile and task_type in profile.preferred_task_types:
            reasons.append(f"preferred task type (>80% success)")
        
        if task_type in agent.preferred_task_types:
            reasons.append(f"matches agent capabilities")
        
        active_tasks = len(self.agent_storage.list_tasks(
            agent_id=agent.id,
            status=AgentTaskStatus.IN_PROGRESS.value
        ))
        reasons.append(f"{active_tasks} active tasks")
        
        return " | ".join(reasons) if reasons else "no historical data"


def get_learning_system(agent_storage: Optional[AgentStorage] = None) -> AgentLearningSystem:
    """
    Get AgentLearningSystem instance.
    
    Args:
        agent_storage: AgentStorage instance
    
    Returns:
        AgentLearningSystem instance
    """
    return AgentLearningSystem(agent_storage)


def get_smart_selector(
    learning_system: Optional[AgentLearningSystem] = None,
    agent_storage: Optional[AgentStorage] = None
) -> SmartAgentSelector:
    """
    Get SmartAgentSelector instance.
    
    Args:
        learning_system: AgentLearningSystem instance
        agent_storage: AgentStorage instance
    
    Returns:
        SmartAgentSelector instance
    """
    if learning_system is None:
        learning_system = get_learning_system(agent_storage)
    
    return SmartAgentSelector(learning_system, agent_storage)
