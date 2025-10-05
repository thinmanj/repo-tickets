#!/usr/bin/env python3
"""
Bulk Operations Script for repo-tickets

This script demonstrates how AI agents can perform bulk operations
on tickets, epics, and backlog items using both CLI commands and
direct file manipulation.
"""

import json
import subprocess
import argparse
import sys
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import re

class TicketSystemAgent:
    """Agent for interacting with the repo-tickets system."""
    
    def __init__(self, agent_name: str = "python-agent"):
        self.agent_name = agent_name
        self.tickets_dir = Path(".tickets")
        self.log_entries = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] {level}: {message}"
        self.log_entries.append(entry)
        print(entry)
    
    def run_cli_command(self, command: List[str]) -> Dict[str, Any]:
        """Execute a tickets CLI command and return parsed result."""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                try:
                    return json.loads(result.stdout)
                except json.JSONDecodeError:
                    return {"output": result.stdout.strip(), "success": True}
            
            return {"success": True}
            
        except subprocess.CalledProcessError as e:
            self.log(f"CLI command failed: {' '.join(command)}", "ERROR")
            self.log(f"Error: {e.stderr}", "ERROR")
            return {"success": False, "error": e.stderr}
    
    def read_tickets(self) -> List[Dict[str, Any]]:
        """Read all tickets from the JSON file."""
        tickets_file = self.tickets_dir / "tickets.json"
        if tickets_file.exists():
            with open(tickets_file, 'r') as f:
                return json.load(f)
        return []
    
    def read_epics(self) -> List[Dict[str, Any]]:
        """Read all epics from the JSON file."""
        epics_file = self.tickets_dir / "epics.json"
        if epics_file.exists():
            with open(epics_file, 'r') as f:
                return json.load(f)
        return []
    
    def read_backlog(self) -> List[Dict[str, Any]]:
        """Read all backlog items from the JSON file."""
        backlog_file = self.tickets_dir / "backlog.json"
        if backlog_file.exists():
            with open(backlog_file, 'r') as f:
                return json.load(f)
        return []
    
    def bulk_update_tickets(self, filters: Dict[str, str], updates: Dict[str, Any]) -> int:
        """Update multiple tickets matching the filters."""
        self.log(f"Starting bulk update with filters: {filters}")
        
        tickets = self.read_tickets()
        matching_tickets = self.filter_tickets(tickets, filters)
        
        updated_count = 0
        for ticket in matching_tickets:
            ticket_id = ticket['id']
            self.log(f"Updating ticket: {ticket_id}")
            
            # Build CLI command
            command = ["tickets", "update", ticket_id]
            
            for field, value in updates.items():
                if field == "add_comment":
                    command.extend(["--add-comment", f"Agent: {value}"])
                elif field == "add_tag":
                    command.extend(["--add-tag", value])
                elif field == "remove_tag":
                    command.extend(["--remove-tag", value])
                else:
                    command.extend([f"--{field.replace('_', '-')}", str(value)])
            
            command.extend(["--format", "json"])
            
            result = self.run_cli_command(command)
            if result.get("success", False):
                updated_count += 1
            else:
                self.log(f"Failed to update ticket: {ticket_id}", "ERROR")
        
        self.log(f"Updated {updated_count} tickets out of {len(matching_tickets)} matching")
        return updated_count
    
    def filter_tickets(self, tickets: List[Dict], filters: Dict[str, str]) -> List[Dict]:
        """Filter tickets based on criteria."""
        filtered = tickets
        
        for field, value in filters.items():
            if field == "status":
                filtered = [t for t in filtered if t.get("status") == value]
            elif field == "priority":
                filtered = [t for t in filtered if t.get("priority") == value]
            elif field == "assignee":
                filtered = [t for t in filtered if t.get("assignee") == value]
            elif field == "epic_id":
                filtered = [t for t in filtered if t.get("epic_id") == value]
            elif field == "tag":
                filtered = [t for t in filtered if value in t.get("tags", [])]
            elif field == "title_contains":
                filtered = [t for t in filtered if value.lower() in t.get("title", "").lower()]
        
        return filtered
    
    def create_tickets_from_template(self, template: Dict[str, Any], count: int) -> List[str]:
        """Create multiple tickets from a template."""
        created_tickets = []
        
        for i in range(1, count + 1):
            ticket_data = template.copy()
            ticket_data["title"] = f"{ticket_data['title']} #{i}"
            
            if "description" in ticket_data:
                ticket_data["description"] = f"{ticket_data['description']} (Generated #{i})"
            
            # Build CLI command
            command = ["tickets", "create"]
            for field, value in ticket_data.items():
                if field in ["title", "description", "priority", "status", "assignee", "epic_id"]:
                    command.extend([f"--{field.replace('_', '-')}", str(value)])
            
            command.extend(["--format", "json"])
            
            result = self.run_cli_command(command)
            if result.get("success", False) and "id" in result:
                created_tickets.append(result["id"])
                self.log(f"Created ticket: {result['id']}")
            else:
                self.log(f"Failed to create ticket #{i}", "ERROR")
        
        return created_tickets
    
    def auto_assign_tickets(self, assignee_rules: Dict[str, List[str]]) -> int:
        """Automatically assign tickets based on rules."""
        self.log("Starting automatic ticket assignment")
        
        tickets = self.read_tickets()
        unassigned_tickets = [t for t in tickets if not t.get("assignee")]
        
        assigned_count = 0
        
        for ticket in unassigned_tickets:
            assignee = self.determine_assignee(ticket, assignee_rules)
            if assignee:
                result = self.run_cli_command([
                    "tickets", "update", ticket["id"],
                    "--assignee", assignee,
                    "--add-comment", f"Agent: Auto-assigned based on ticket content",
                    "--format", "json"
                ])
                
                if result.get("success", False):
                    assigned_count += 1
                    self.log(f"Assigned {ticket['id']} to {assignee}")
        
        self.log(f"Auto-assigned {assigned_count} tickets")
        return assigned_count
    
    def determine_assignee(self, ticket: Dict[str, Any], rules: Dict[str, List[str]]) -> Optional[str]:
        """Determine assignee based on ticket content and rules."""
        title_lower = ticket.get("title", "").lower()
        description_lower = ticket.get("description", "").lower()
        tags = ticket.get("tags", [])
        
        for assignee, keywords in rules.items():
            for keyword in keywords:
                if (keyword.lower() in title_lower or 
                    keyword.lower() in description_lower or 
                    keyword.lower() in [tag.lower() for tag in tags]):
                    return assignee
        
        return None
    
    def prioritize_backlog_items(self) -> int:
        """Automatically prioritize backlog items based on business value and effort."""
        self.log("Starting backlog prioritization")
        
        backlog_items = self.read_backlog()
        updated_count = 0
        
        for item in backlog_items:
            new_priority = self.calculate_priority_score(item)
            current_priority = item.get("priority_score", 0)
            
            if new_priority != current_priority:
                # Note: This would need a CLI command to update backlog items
                # For now, we'll just log the recommendation
                self.log(f"Backlog item {item['id']}: Priority should be {new_priority} (current: {current_priority})")
                updated_count += 1
        
        return updated_count
    
    def calculate_priority_score(self, item: Dict[str, Any]) -> int:
        """Calculate priority score based on business value and effort."""
        business_value_scores = {"high": 40, "medium": 20, "low": 10}
        effort_scores = {"low": 40, "medium": 20, "high": 10}  # Lower effort = higher score
        
        business_score = business_value_scores.get(item.get("business_value", "medium"), 20)
        effort_score = effort_scores.get(item.get("effort_estimate", "medium"), 20)
        
        # Add bonus for certain tags
        tag_bonus = 0
        tags = item.get("tags", [])
        if "critical" in tags:
            tag_bonus += 20
        elif "important" in tags:
            tag_bonus += 10
        
        return min(100, business_score + effort_score + tag_bonus)
    
    def generate_bulk_report(self) -> Dict[str, Any]:
        """Generate a comprehensive bulk operations report."""
        tickets = self.read_tickets()
        epics = self.read_epics()
        backlog = self.read_backlog()
        
        # Calculate statistics
        ticket_stats = self.calculate_ticket_stats(tickets)
        epic_stats = self.calculate_epic_stats(epics, tickets)
        backlog_stats = self.calculate_backlog_stats(backlog)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_name,
            "summary": {
                "total_tickets": len(tickets),
                "total_epics": len(epics),
                "total_backlog_items": len(backlog)
            },
            "tickets": ticket_stats,
            "epics": epic_stats,
            "backlog": backlog_stats,
            "recommendations": self.generate_recommendations(tickets, epics, backlog)
        }
        
        return report
    
    def calculate_ticket_stats(self, tickets: List[Dict]) -> Dict[str, Any]:
        """Calculate ticket statistics."""
        stats = {
            "by_status": {},
            "by_priority": {},
            "by_assignee": {},
            "unassigned_count": 0,
            "overdue_count": 0,  # Would need due_date field
            "estimated_hours_total": 0,
            "actual_hours_total": 0
        }
        
        for ticket in tickets:
            # Status distribution
            status = ticket.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Priority distribution
            priority = ticket.get("priority", "unknown")
            stats["by_priority"][priority] = stats["by_priority"].get(priority, 0) + 1
            
            # Assignee distribution
            assignee = ticket.get("assignee") or "unassigned"
            stats["by_assignee"][assignee] = stats["by_assignee"].get(assignee, 0) + 1
            
            if not ticket.get("assignee"):
                stats["unassigned_count"] += 1
            
            # Hours tracking
            if ticket.get("estimated_hours"):
                stats["estimated_hours_total"] += ticket["estimated_hours"]
            if ticket.get("actual_hours"):
                stats["actual_hours_total"] += ticket["actual_hours"]
        
        return stats
    
    def calculate_epic_stats(self, epics: List[Dict], tickets: List[Dict]) -> Dict[str, Any]:
        """Calculate epic statistics."""
        stats = {
            "by_status": {},
            "completion_rates": {},
            "ticket_distribution": {}
        }
        
        for epic in epics:
            # Status distribution
            status = epic.get("status", "unknown")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
            
            # Calculate completion rate
            epic_tickets = [t for t in tickets if t.get("epic_id") == epic["id"]]
            done_tickets = [t for t in epic_tickets if t.get("status") == "done"]
            
            if epic_tickets:
                completion_rate = len(done_tickets) / len(epic_tickets) * 100
                stats["completion_rates"][epic["id"]] = {
                    "name": epic.get("name", "Unnamed Epic"),
                    "completion_rate": round(completion_rate, 2),
                    "total_tickets": len(epic_tickets),
                    "done_tickets": len(done_tickets)
                }
            
            stats["ticket_distribution"][epic["id"]] = len(epic_tickets)
        
        return stats
    
    def calculate_backlog_stats(self, backlog: List[Dict]) -> Dict[str, Any]:
        """Calculate backlog statistics."""
        stats = {
            "by_business_value": {},
            "by_effort_estimate": {},
            "priority_distribution": {},
            "high_priority_count": 0,
            "average_priority_score": 0
        }
        
        total_score = 0
        for item in backlog:
            # Business value distribution
            bv = item.get("business_value", "unknown")
            stats["by_business_value"][bv] = stats["by_business_value"].get(bv, 0) + 1
            
            # Effort estimate distribution
            effort = item.get("effort_estimate", "unknown")
            stats["by_effort_estimate"][effort] = stats["by_effort_estimate"].get(effort, 0) + 1
            
            # Priority score analysis
            score = item.get("priority_score", 0)
            total_score += score
            
            if score >= 80:
                stats["high_priority_count"] += 1
            
            # Group by priority ranges
            if score >= 90:
                range_key = "90-100"
            elif score >= 80:
                range_key = "80-89"
            elif score >= 70:
                range_key = "70-79"
            elif score >= 60:
                range_key = "60-69"
            else:
                range_key = "0-59"
            
            stats["priority_distribution"][range_key] = stats["priority_distribution"].get(range_key, 0) + 1
        
        if backlog:
            stats["average_priority_score"] = round(total_score / len(backlog), 2)
        
        return stats
    
    def generate_recommendations(self, tickets: List[Dict], epics: List[Dict], backlog: List[Dict]) -> List[str]:
        """Generate automated recommendations based on data analysis."""
        recommendations = []
        
        # Analyze unassigned tickets
        unassigned = [t for t in tickets if not t.get("assignee")]
        if len(unassigned) > 5:
            recommendations.append(f"Consider assigning {len(unassigned)} unassigned tickets to team members")
        
        # Analyze stale tickets
        in_progress = [t for t in tickets if t.get("status") == "in-progress"]
        if len(in_progress) > 10:
            recommendations.append(f"Review {len(in_progress)} in-progress tickets for potential blockers")
        
        # Analyze high priority backlog
        high_priority_backlog = [b for b in backlog if b.get("priority_score", 0) >= 85]
        if len(high_priority_backlog) > 3:
            recommendations.append(f"Convert {len(high_priority_backlog)} high-priority backlog items to tickets")
        
        # Analyze epic completion
        for epic in epics:
            epic_tickets = [t for t in tickets if t.get("epic_id") == epic["id"]]
            if len(epic_tickets) == 0:
                recommendations.append(f"Epic '{epic.get('name', epic['id'])}' has no assigned tickets")
        
        return recommendations

def main():
    """Main function to run bulk operations."""
    parser = argparse.ArgumentParser(description="Bulk operations for repo-tickets")
    parser.add_argument("--operation", choices=[
        "bulk-update", "create-from-template", "auto-assign", 
        "prioritize-backlog", "generate-report"
    ], required=True, help="Operation to perform")
    
    parser.add_argument("--agent-name", default="python-agent", help="Agent name for operations")
    parser.add_argument("--filters", help="JSON string of filters for bulk operations")
    parser.add_argument("--updates", help="JSON string of updates to apply")
    parser.add_argument("--template", help="JSON string of ticket template")
    parser.add_argument("--count", type=int, default=1, help="Number of tickets to create")
    parser.add_argument("--output-file", help="File to save report output")
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = TicketSystemAgent(args.agent_name)
    
    if args.operation == "bulk-update":
        if not args.filters or not args.updates:
            print("Error: --filters and --updates are required for bulk-update")
            sys.exit(1)
        
        filters = json.loads(args.filters)
        updates = json.loads(args.updates)
        
        count = agent.bulk_update_tickets(filters, updates)
        print(f"Successfully updated {count} tickets")
    
    elif args.operation == "create-from-template":
        if not args.template:
            print("Error: --template is required for create-from-template")
            sys.exit(1)
        
        template = json.loads(args.template)
        created_tickets = agent.create_tickets_from_template(template, args.count)
        print(f"Created {len(created_tickets)} tickets: {', '.join(created_tickets)}")
    
    elif args.operation == "auto-assign":
        # Default assignee rules
        assignee_rules = {
            "frontend-team": ["ui", "frontend", "react", "vue", "angular"],
            "backend-team": ["api", "backend", "server", "database", "python", "java"],
            "devops-team": ["deploy", "devops", "infrastructure", "docker", "kubernetes"],
            "qa-team": ["test", "testing", "qa", "quality", "bug"]
        }
        
        count = agent.auto_assign_tickets(assignee_rules)
        print(f"Auto-assigned {count} tickets")
    
    elif args.operation == "prioritize-backlog":
        count = agent.prioritize_backlog_items()
        print(f"Analyzed {count} backlog items for prioritization")
    
    elif args.operation == "generate-report":
        report = agent.generate_bulk_report()
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"Report saved to {args.output_file}")
        else:
            print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()