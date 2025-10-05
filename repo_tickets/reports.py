#!/usr/bin/env python3
"""
HTML report generation for repo-tickets.

Creates professional, interactive HTML reports with charts, analytics, and modern design.
"""

import os
import json
import subprocess
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

from .models import Ticket
from .storage import TicketStorage
from .vcs import detect_vcs


class TicketReportGenerator:
    """Generates professional HTML reports for tickets."""
    
    def __init__(self, storage: TicketStorage):
        self.storage = storage
        self.vcs = detect_vcs()
        
    def generate_html_report(self, output_path: Optional[Path] = None) -> Path:
        """Generate a comprehensive HTML report."""
        if output_path is None:
            output_path = Path.cwd() / "ticket_report.html"
        
        # Gather all data
        tickets = self.storage.list_tickets()
        stats = self.storage.get_stats()
        analytics = self._generate_analytics(tickets)
        
        # Generate HTML content
        html_content = self._generate_html(tickets, stats, analytics)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def _generate_analytics(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Generate comprehensive analytics from tickets."""
        now = datetime.now()
        
        analytics = {
            'total_tickets': len(tickets),
            'open_tickets': len([t for t in tickets if t.is_open]),
            'closed_tickets': len([t for t in tickets if not t.is_open]),
            'status_distribution': self._get_status_distribution(tickets),
            'priority_distribution': self._get_priority_distribution(tickets),
            'label_distribution': self._get_label_distribution(tickets),
            'assignee_workload': self._get_assignee_workload(tickets),
            'age_distribution': self._get_age_distribution(tickets),
            'activity_timeline': self._get_activity_timeline(tickets),
            'progress_metrics': self._get_progress_metrics(tickets),
            'risk_indicators': self._get_risk_indicators(tickets),
            'velocity_metrics': self._get_velocity_metrics(tickets),
            'requirements_metrics': self._get_requirements_metrics(tickets),
        }
        
        return analytics
    
    def _get_status_distribution(self, tickets: List[Ticket]) -> Dict[str, int]:
        """Get distribution of tickets by status."""
        return dict(Counter(ticket.status for ticket in tickets))
    
    def _get_priority_distribution(self, tickets: List[Ticket]) -> Dict[str, int]:
        """Get distribution of tickets by priority."""
        return dict(Counter(ticket.priority for ticket in tickets))
    
    def _get_label_distribution(self, tickets: List[Ticket]) -> Dict[str, int]:
        """Get distribution of labels across all tickets."""
        label_counts = Counter()
        for ticket in tickets:
            for label in ticket.labels:
                label_counts[label] += 1
        return dict(label_counts.most_common(10))  # Top 10 labels
    
    def _get_assignee_workload(self, tickets: List[Ticket]) -> Dict[str, Dict[str, int]]:
        """Get workload distribution by assignee."""
        workload = defaultdict(lambda: {'total': 0, 'open': 0, 'in_progress': 0})
        
        for ticket in tickets:
            assignee = ticket.assignee or 'Unassigned'
            workload[assignee]['total'] += 1
            if ticket.status == 'open':
                workload[assignee]['open'] += 1
            elif ticket.status == 'in-progress':
                workload[assignee]['in_progress'] += 1
        
        return dict(workload)
    
    def _get_age_distribution(self, tickets: List[Ticket]) -> Dict[str, int]:
        """Get distribution of tickets by age."""
        age_buckets = {
            'New (0-2 days)': 0,
            'Recent (3-7 days)': 0,
            'Moderate (1-4 weeks)': 0,
            'Old (1-3 months)': 0,
            'Ancient (3+ months)': 0,
        }
        
        for ticket in tickets:
            age = ticket.age_days
            if age <= 2:
                age_buckets['New (0-2 days)'] += 1
            elif age <= 7:
                age_buckets['Recent (3-7 days)'] += 1
            elif age <= 28:
                age_buckets['Moderate (1-4 weeks)'] += 1
            elif age <= 90:
                age_buckets['Old (1-3 months)'] += 1
            else:
                age_buckets['Ancient (3+ months)'] += 1
        
        return age_buckets
    
    def _get_activity_timeline(self, tickets: List[Ticket]) -> List[Dict[str, Any]]:
        """Get timeline of ticket activity."""
        events = []
        
        for ticket in tickets:
            # Creation event
            events.append({
                'date': ticket.created_at.strftime('%Y-%m-%d'),
                'type': 'created',
                'ticket_id': ticket.id,
                'title': ticket.title,
                'priority': ticket.priority,
                'status': ticket.status,
            })
            
            # Comment events
            for comment in ticket.comments:
                events.append({
                    'date': comment.created_at.strftime('%Y-%m-%d'),
                    'type': 'commented',
                    'ticket_id': ticket.id,
                    'title': ticket.title,
                    'author': comment.author,
                })
        
        # Sort by date and limit to recent events
        events.sort(key=lambda x: x['date'], reverse=True)
        return events[:20]  # Last 20 events
    
    def _get_progress_metrics(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Calculate project progress metrics."""
        total = len(tickets)
        if total == 0:
            return {'completion_rate': 0, 'work_in_progress': 0, 'backlog_size': 0}
        
        closed = len([t for t in tickets if t.status == 'closed'])
        in_progress = len([t for t in tickets if t.status == 'in-progress'])
        open_tickets = len([t for t in tickets if t.status == 'open'])
        
        return {
            'completion_rate': round((closed / total) * 100, 1),
            'work_in_progress': in_progress,
            'backlog_size': open_tickets,
            'total_effort': total,
        }
    
    def _get_risk_indicators(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Identify potential risks in the project."""
        risks = {
            'blocked_tickets': len([t for t in tickets if t.status == 'blocked']),
            'critical_open': len([t for t in tickets if t.priority == 'critical' and t.is_open]),
            'old_open_tickets': len([t for t in tickets if t.is_open and t.age_days > 30]),
            'unassigned_tickets': len([t for t in tickets if not t.assignee and t.is_open]),
            'high_priority_stalled': len([t for t in tickets if t.priority in ['critical', 'high'] and t.age_days > 7 and t.is_open]),
        }
        
        # Calculate risk score (0-100)
        risk_score = min(100, (
            risks['blocked_tickets'] * 20 +
            risks['critical_open'] * 15 +
            risks['old_open_tickets'] * 5 +
            risks['unassigned_tickets'] * 3 +
            risks['high_priority_stalled'] * 10
        ))
        
        risks['overall_risk_score'] = risk_score
        return risks
    
    def _get_velocity_metrics(self, tickets: List[Ticket]) -> Dict[str, float]:
        """Calculate team velocity metrics."""
        now = datetime.now()
        
        # Tickets closed in last 7 days
        week_ago = now - timedelta(days=7)
        weekly_closed = len([t for t in tickets if not t.is_open and t.updated_at >= week_ago])
        
        # Tickets closed in last 30 days
        month_ago = now - timedelta(days=30)
        monthly_closed = len([t for t in tickets if not t.is_open and t.updated_at >= month_ago])
        
        return {
            'weekly_velocity': weekly_closed,
            'monthly_velocity': monthly_closed,
            'average_resolution_time': self._calculate_avg_resolution_time(tickets),
        }
    
    def _calculate_avg_resolution_time(self, tickets: List[Ticket]) -> float:
        """Calculate average time to resolve tickets."""
        closed_tickets = [t for t in tickets if not t.is_open]
        if not closed_tickets:
            return 0.0
        
        total_time = sum((t.updated_at - t.created_at).days for t in closed_tickets)
        return round(total_time / len(closed_tickets), 1)
    
    def _get_requirements_metrics(self, tickets: List[Ticket]) -> Dict[str, Any]:
        """Calculate requirements and acceptance criteria metrics."""
        tickets_with_requirements = [t for t in tickets if t.requirements or t.user_stories or t.expected_results or t.gherkin_scenarios]
        
        if not tickets_with_requirements:
            return {
                'tickets_with_requirements': 0,
                'total_requirements': 0,
                'total_user_stories': 0,
                'total_story_points': 0,
                'total_expected_results': 0,
                'total_scenarios': 0,
                'requirements_coverage': 0.0,
                'acceptance_rate': 0.0,
                'test_pass_rate': 0.0,
                'requirements_status_distribution': {},
                'scenario_status_distribution': {},
                'verification_method_distribution': {},
            }
        
        # Basic counts
        total_requirements = sum(len(t.requirements) for t in tickets)
        total_user_stories = sum(len(t.user_stories) for t in tickets)
        total_expected_results = sum(len(t.expected_results) for t in tickets)
        total_scenarios = sum(len(t.gherkin_scenarios) for t in tickets)
        total_story_points = sum(t.total_story_points for t in tickets)
        
        # Requirements coverage
        requirements_coverage = 0.0
        if tickets:
            covered_requirements = 0
            total_req_count = 0
            
            for ticket in tickets:
                if ticket.requirements:
                    total_req_count += len(ticket.requirements)
                    covered_requirements += len([r for r in ticket.requirements if r.status in ['implemented', 'verified']])
            
            if total_req_count > 0:
                requirements_coverage = (covered_requirements / total_req_count) * 100
        
        # Acceptance criteria met rate
        acceptance_rate = 0.0
        if tickets_with_requirements:
            tickets_with_met_criteria = len([t for t in tickets_with_requirements if t.acceptance_criteria_met])
            acceptance_rate = (tickets_with_met_criteria / len(tickets_with_requirements)) * 100
        
        # Test pass rate
        test_pass_rate = 0.0
        if total_scenarios > 0:
            passing_scenarios = 0
            for ticket in tickets:
                passing_scenarios += len([s for s in ticket.gherkin_scenarios if s.status == 'passing'])
            test_pass_rate = (passing_scenarios / total_scenarios) * 100
        
        # Status distributions
        requirements_status_distribution = Counter()
        scenario_status_distribution = Counter()
        verification_method_distribution = Counter()
        
        for ticket in tickets:
            for req in ticket.requirements:
                requirements_status_distribution[req.status] += 1
            
            for scenario in ticket.gherkin_scenarios:
                scenario_status_distribution[scenario.status] += 1
            
            for result in ticket.expected_results:
                verification_method_distribution[result.verification_method] += 1
        
        return {
            'tickets_with_requirements': len(tickets_with_requirements),
            'total_requirements': total_requirements,
            'total_user_stories': total_user_stories,
            'total_story_points': total_story_points,
            'total_expected_results': total_expected_results,
            'total_scenarios': total_scenarios,
            'requirements_coverage': round(requirements_coverage, 1),
            'acceptance_rate': round(acceptance_rate, 1),
            'test_pass_rate': round(test_pass_rate, 1),
            'requirements_status_distribution': dict(requirements_status_distribution),
            'scenario_status_distribution': dict(scenario_status_distribution),
            'verification_method_distribution': dict(verification_method_distribution),
        }
    
    def _generate_html(self, tickets: List[Ticket], stats: Dict[str, int], analytics: Dict[str, Any]) -> str:
        """Generate the complete HTML report."""
        # Get project info
        project_name = self.storage.repo_root.name if self.storage.repo_root else "Project"
        vcs_type = type(self.vcs).__name__.replace('VCS', '') if self.vcs else 'Unknown'
        generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ticket Report - {project_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/date-fns@2.29.3/index.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            color: #666;
            font-size: 1rem;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
        }}
        
        .card h3 {{
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: #4a5568;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: #f7fafc;
            border-radius: 10px;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #2d3748;
        }}
        
        .stat-label {{
            color: #718096;
            font-size: 0.9rem;
            margin-top: 5px;
        }}
        
        .chart-container {{
            height: 300px;
            margin-top: 20px;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e2e8f0;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.5s ease;
        }}
        
        .ticket-list {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .ticket-filters {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: 1px solid #e2e8f0;
            border-radius: 20px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }}
        
        .filter-btn.active,
        .filter-btn:hover {{
            background: #667eea;
            color: white;
            border-color: #667eea;
        }}
        
        .ticket-item {{
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
        }}
        
        .ticket-item:hover {{
            border-color: #667eea;
            transform: translateX(5px);
        }}
        
        .ticket-header {{
            display: flex;
            justify-content: between;
            align-items: flex-start;
            margin-bottom: 10px;
            gap: 15px;
        }}
        
        .ticket-id {{
            font-weight: 700;
            color: #667eea;
            text-decoration: none;
            font-size: 0.9rem;
            white-space: nowrap;
        }}
        
        .ticket-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3748;
            flex: 1;
        }}
        
        .ticket-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
            margin-top: 10px;
        }}
        
        .badge {{
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .badge.status-open {{ background: #c6f6d5; color: #22543d; }}
        .badge.status-in-progress {{ background: #fed7d7; color: #c53030; }}
        .badge.status-blocked {{ background: #feb2b2; color: #9b2c2c; }}
        .badge.status-closed {{ background: #bee3f8; color: #2a69ac; }}
        
        .badge.priority-critical { background: #fed7d7; color: #c53030; }
        .badge.priority-high { background: #feebc8; color: #c05621; }
        .badge.priority-medium { background: #e6fffa; color: #234e52; }
        .badge.priority-low { background: #f0fff4; color: #22543d; }
        
        .badge.success { background: #22543d; color: white; }
        .badge.warning { background: #c05621; color: white; }
        .badge.danger { background: #c53030; color: white; }
        .badge.info { background: #2a69ac; color: white; }
        
        .risk-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 5px 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 500;
        }}
        
        .risk-low {{ background: #c6f6d5; color: #22543d; }}
        .risk-medium {{ background: #feebc8; color: #c05621; }}
        .risk-high {{ background: #fed7d7; color: #c53030; }}
        
        .timeline {{
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .timeline-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 10px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        
        .timeline-item:last-child {{
            border-bottom: none;
        }}
        
        .timeline-icon {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #667eea;
            flex-shrink: 0;
        }}
        
        .timeline-content {{
            flex: 1;
            font-size: 0.9rem;
        }}
        
        .timeline-date {{
            color: #718096;
            font-size: 0.8rem;
        }}
        
        @media (max-width: 768px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
            
            .stat-grid {{
                grid-template-columns: 1fr;
            }}
            
            .ticket-header {{
                flex-direction: column;
                align-items: flex-start;
            }}
            
            .ticket-filters {{
                flex-direction: column;
            }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header fade-in">
            <h1>📊 Project Dashboard</h1>
            <div class="meta">
                <strong>{project_name}</strong> • {vcs_type} Repository<br>
                Generated on {generation_time}
            </div>
        </div>
        
        <div class="dashboard">
            {self._generate_overview_card(stats, analytics)}
            {self._generate_progress_card(analytics)}
            {self._generate_risk_card(analytics)}
            {self._generate_velocity_card(analytics)}
            {self._generate_requirements_card(analytics)}
        </div>
        
        <div class="dashboard">
            {self._generate_status_chart_card(analytics)}
            {self._generate_priority_chart_card(analytics)}
            {self._generate_assignee_chart_card(analytics)}
            {self._generate_timeline_card(analytics)}
        </div>
        
        <div class="ticket-list fade-in">
            <h3>🎫 All Tickets</h3>
            <div class="ticket-filters">
                <button class="filter-btn active" data-filter="all">All</button>
                <button class="filter-btn" data-filter="open">Open</button>
                <button class="filter-btn" data-filter="in-progress">In Progress</button>
                <button class="filter-btn" data-filter="blocked">Blocked</button>
                <button class="filter-btn" data-filter="closed">Closed</button>
                <button class="filter-btn" data-filter="critical">Critical</button>
                <button class="filter-btn" data-filter="high">High Priority</button>
            </div>
            {self._generate_ticket_list(tickets)}
        </div>
    </div>
    
    <script>
        // Initialize charts and interactions
        document.addEventListener('DOMContentLoaded', function() {{
            {self._generate_chart_scripts(analytics)}
            {self._generate_filter_scripts()}
            
            // Add fade-in animation to cards
            setTimeout(() => {{
                document.querySelectorAll('.card').forEach((card, index) => {{
                    setTimeout(() => {{
                        card.classList.add('fade-in');
                    }}, index * 100);
                }});
            }}, 200);
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_overview_card(self, stats: Dict[str, int], analytics: Dict[str, Any]) -> str:
        """Generate the project overview card."""
        return f"""
        <div class="card">
            <h3>📈 Project Overview</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{analytics['total_tickets']}</div>
                    <div class="stat-label">Total Tickets</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{analytics['open_tickets']}</div>
                    <div class="stat-label">Open</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{analytics['closed_tickets']}</div>
                    <div class="stat-label">Closed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{len(analytics['assignee_workload'])}</div>
                    <div class="stat-label">Team Members</div>
                </div>
            </div>
        </div>"""
    
    def _generate_progress_card(self, analytics: Dict[str, Any]) -> str:
        """Generate the progress tracking card."""
        progress = analytics['progress_metrics']
        completion_rate = progress['completion_rate']
        
        return f"""
        <div class="card">
            <h3>🎯 Progress Tracking</h3>
            <div style="text-align: center; margin: 20px 0;">
                <div class="stat-value">{completion_rate}%</div>
                <div class="stat-label">Completion Rate</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {completion_rate}%"></div>
                </div>
            </div>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{progress['work_in_progress']}</div>
                    <div class="stat-label">In Progress</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{progress['backlog_size']}</div>
                    <div class="stat-label">Backlog</div>
                </div>
            </div>
        </div>"""
    
    def _generate_risk_card(self, analytics: Dict[str, Any]) -> str:
        """Generate the risk assessment card."""
        risks = analytics['risk_indicators']
        risk_score = risks['overall_risk_score']
        
        if risk_score < 20:
            risk_level = "low"
            risk_text = "Low Risk"
            risk_color = "#22543d"
        elif risk_score < 50:
            risk_level = "medium"
            risk_text = "Medium Risk"
            risk_color = "#c05621"
        else:
            risk_level = "high"
            risk_text = "High Risk"
            risk_color = "#c53030"
        
        return f"""
        <div class="card">
            <h3>⚠️ Risk Assessment</h3>
            <div style="text-align: center; margin: 20px 0;">
                <div class="risk-indicator risk-{risk_level}">
                    {risk_text} ({risk_score}/100)
                </div>
            </div>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value" style="color: {risk_color};">{risks['blocked_tickets']}</div>
                    <div class="stat-label">Blocked</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: {risk_color};">{risks['critical_open']}</div>
                    <div class="stat-label">Critical Open</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: {risk_color};">{risks['old_open_tickets']}</div>
                    <div class="stat-label">Stale (30+ days)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: {risk_color};">{risks['unassigned_tickets']}</div>
                    <div class="stat-label">Unassigned</div>
                </div>
            </div>
        </div>"""
    
    def _generate_velocity_card(self, analytics: Dict[str, Any]) -> str:
        """Generate the team velocity card."""
        velocity = analytics['velocity_metrics']
        
        return f"""
        <div class="card">
            <h3>🚀 Team Velocity</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{velocity['weekly_velocity']}</div>
                    <div class="stat-label">Closed This Week</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{velocity['monthly_velocity']}</div>
                    <div class="stat-label">Closed This Month</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{velocity['average_resolution_time']}</div>
                    <div class="stat-label">Avg Resolution (days)</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{velocity['monthly_velocity'] * 12}</div>
                    <div class="stat-label">Projected Annual</div>
                </div>
            </div>
        </div>"""
    
    def _generate_requirements_card(self, analytics: Dict[str, Any]) -> str:
        """Generate the requirements and acceptance criteria card."""
        req_metrics = analytics['requirements_metrics']
        
        if req_metrics['tickets_with_requirements'] == 0:
            return f"""
            <div class="card">
                <h3>📋 Requirements</h3>
                <div style="text-align: center; padding: 40px; color: #666;">
                    <div style="font-size: 3rem; margin-bottom: 10px;">📄</div>
                    <div>No requirements defined yet</div>
                    <div style="font-size: 0.9rem; margin-top: 10px;">Use 'tickets requirements add' to get started</div>
                </div>
            </div>"""
        
        coverage_color = "#22543d" if req_metrics['requirements_coverage'] > 80 else "#c05621" if req_metrics['requirements_coverage'] > 50 else "#c53030"
        test_color = "#22543d" if req_metrics['test_pass_rate'] > 80 else "#c05621" if req_metrics['test_pass_rate'] > 50 else "#c53030"
        
        return f"""
        <div class="card">
            <h3>📋 Requirements & Testing</h3>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="stat-value">{req_metrics['total_requirements']}</div>
                    <div class="stat-label">Requirements</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{req_metrics['total_user_stories']}</div>
                    <div class="stat-label">User Stories</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: {coverage_color};">{req_metrics['requirements_coverage']}%</div>
                    <div class="stat-label">Coverage</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: {test_color};">{req_metrics['test_pass_rate']}%</div>
                    <div class="stat-label">Tests Passing</div>
                </div>
            </div>
            <div style="margin-top: 15px; padding: 10px; background: #f7fafc; border-radius: 8px; font-size: 0.9rem;">
                🏆 Story Points: {req_metrics['total_story_points']} • 
                🎯 Tests: {req_metrics['total_scenarios']} • 
                ✅ Acceptance: {req_metrics['acceptance_rate']}%
            </div>
        </div>"""
    
    def _generate_status_chart_card(self, analytics: Dict[str, Any]) -> str:
        """Generate status distribution chart."""
        return f"""
        <div class="card">
            <h3>📊 Status Distribution</h3>
            <div class="chart-container">
                <canvas id="statusChart"></canvas>
            </div>
        </div>"""
    
    def _generate_priority_chart_card(self, analytics: Dict[str, Any]) -> str:
        """Generate priority distribution chart."""
        return f"""
        <div class="card">
            <h3>🎯 Priority Distribution</h3>
            <div class="chart-container">
                <canvas id="priorityChart"></canvas>
            </div>
        </div>"""
    
    def _generate_assignee_chart_card(self, analytics: Dict[str, Any]) -> str:
        """Generate assignee workload chart."""
        return f"""
        <div class="card">
            <h3>👥 Team Workload</h3>
            <div class="chart-container">
                <canvas id="assigneeChart"></canvas>
            </div>
        </div>"""
    
    def _generate_timeline_card(self, analytics: Dict[str, Any]) -> str:
        """Generate activity timeline."""
        timeline_html = ""
        for event in analytics['activity_timeline']:
            icon_color = "#667eea"
            if event['type'] == 'created':
                icon_color = "#22543d"
            elif event['type'] == 'commented':
                icon_color = "#c05621"
            
            timeline_html += f"""
            <div class="timeline-item">
                <div class="timeline-icon" style="background: {icon_color};"></div>
                <div class="timeline-content">
                    <strong>{event['ticket_id']}</strong> {event['type']}
                    {f"by {event.get('author', '')}" if event.get('author') else ""}
                    <div class="timeline-date">{event['date']}</div>
                </div>
            </div>"""
        
        return f"""
        <div class="card">
            <h3>⏰ Recent Activity</h3>
            <div class="timeline">
                {timeline_html}
            </div>
        </div>"""
    
    def _generate_ticket_list(self, tickets: List[Ticket]) -> str:
        """Generate the detailed ticket list."""
        ticket_html = ""
        
        for ticket in sorted(tickets, key=lambda t: (t.status != 'open', t.priority != 'critical', t.created_at), reverse=True):
            labels_html = " ".join([f'<span class="badge">{label}</span>' for label in ticket.labels])
            assignee_html = f'<span class="badge">👤 {ticket.assignee}</span>' if ticket.assignee else '<span class="badge">Unassigned</span>'
            
            # Add risk indicators
            risk_html = ""
            if ticket.status == 'blocked':
                risk_html += '<span class="risk-indicator risk-high">🚫 Blocked</span>'
            if ticket.priority == 'critical' and ticket.is_open:
                risk_html += '<span class="risk-indicator risk-high">🔥 Critical</span>'
            if ticket.age_days > 30 and ticket.is_open:
                risk_html += '<span class="risk-indicator risk-medium">⏰ Stale</span>'
            
            # Add requirements indicators
            req_html = ""
            if ticket.requirements or ticket.user_stories or ticket.expected_results or ticket.gherkin_scenarios:
                summary = ticket.get_requirements_summary()
                
                # Requirements badge
                if summary['requirements_count'] > 0:
                    req_color = "success" if summary['requirements_coverage'] > 80 else "warning" if summary['requirements_coverage'] > 50 else "danger"
                    req_html += f'<span class="badge {req_color}">📋 {summary["requirements_count"]} req</span>'
                
                # User stories badge  
                if summary['user_stories_count'] > 0:
                    req_html += f'<span class="badge info">📖 {summary["user_stories_count"]} stories ({summary["total_story_points"]}pts)</span>'
                
                # Tests badge
                if summary['gherkin_scenarios_count'] > 0:
                    test_color = "success" if summary['test_pass_rate'] > 80 else "warning" if summary['test_pass_rate'] > 50 else "danger"
                    req_html += f'<span class="badge {test_color}">🧪 {summary["gherkin_scenarios_count"]} tests</span>'
                
                # Acceptance criteria status
                if ticket.acceptance_criteria_met:
                    req_html += '<span class="badge success">✅ Accepted</span>'
                elif summary['requirements_count'] > 0 or summary['expected_results_count'] > 0:
                    req_html += '<span class="badge warning">⏳ Pending</span>'
            
            ticket_html += f"""
            <div class="ticket-item" data-status="{ticket.status}" data-priority="{ticket.priority}">
                <div class="ticket-header">
                    <a href="#{ticket.id}" class="ticket-id">{ticket.id}</a>
                    <div class="ticket-title">{ticket.title}</div>
                </div>
                <div class="ticket-meta">
                    <span class="badge status-{ticket.status.replace('-', '_')}">{ticket.status.title()}</span>
                    <span class="badge priority-{ticket.priority}">{ticket.priority.title()}</span>
                    {assignee_html}
                    <span class="badge">📅 {ticket.age_days}d old</span>
                    {labels_html}
                    {req_html}
                    {risk_html}
                </div>
            </div>"""
        
        return ticket_html
    
    def _generate_chart_scripts(self, analytics: Dict[str, Any]) -> str:
        """Generate JavaScript for charts."""
        status_data = analytics['status_distribution']
        priority_data = analytics['priority_distribution']
        assignee_data = analytics['assignee_workload']
        
        return f"""
        // Status Chart
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {{
            type: 'doughnut',
            data: {{
                labels: {list(status_data.keys())},
                datasets: [{{
                    data: {list(status_data.values())},
                    backgroundColor: ['#22543d', '#c05621', '#c53030', '#2a69ac', '#9b2c2c'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom' }}
                }}
            }}
        }});
        
        // Priority Chart
        const priorityCtx = document.getElementById('priorityChart').getContext('2d');
        new Chart(priorityCtx, {{
            type: 'bar',
            data: {{
                labels: {list(priority_data.keys())},
                datasets: [{{
                    data: {list(priority_data.values())},
                    backgroundColor: ['#c53030', '#c05621', '#234e52', '#22543d'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ beginAtZero: true }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});
        
        // Assignee Chart
        const assigneeCtx = document.getElementById('assigneeChart').getContext('2d');
        const assigneeNames = {list(assignee_data.keys())};
        const assigneeTotals = {[data['total'] for data in assignee_data.values()]};
        
        new Chart(assigneeCtx, {{
            type: 'bar',
            data: {{
                labels: assigneeNames,
                datasets: [{{
                    label: 'Total Tickets',
                    data: assigneeTotals,
                    backgroundColor: '#667eea',
                    borderWidth: 0
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{ beginAtZero: true }}
                }},
                plugins: {{
                    legend: {{ display: false }}
                }}
            }}
        }});"""
    
    def _generate_filter_scripts(self) -> str:
        """Generate JavaScript for ticket filtering."""
        return """
        // Ticket filtering
        const filterBtns = document.querySelectorAll('.filter-btn');
        const ticketItems = document.querySelectorAll('.ticket-item');
        
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active button
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                const filter = btn.dataset.filter;
                
                // Filter tickets
                ticketItems.forEach(ticket => {
                    const status = ticket.dataset.status;
                    const priority = ticket.dataset.priority;
                    
                    let show = false;
                    
                    if (filter === 'all') {
                        show = true;
                    } else if (filter === 'critical') {
                        show = priority === 'critical';
                    } else if (filter === 'high') {
                        show = priority === 'high';
                    } else {
                        show = status === filter;
                    }
                    
                    ticket.style.display = show ? 'block' : 'none';
                });
            });
        });"""


def open_in_browser(file_path: Path) -> bool:
    """Open HTML file in the default browser."""
    try:
        # Convert to file:// URL for better compatibility
        file_url = f"file://{file_path.resolve()}"
        webbrowser.open(file_url)
        return True
    except Exception:
        return False