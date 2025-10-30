#!/usr/bin/env python3
"""
Example automation using the event bus.

Shows how agents can use events for reactive automation without polling.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from repo_tickets.events import EventType, get_event_bus, Event
from repo_tickets.storage import TicketStorage


def example_auto_assign_critical():
    """Auto-assign critical tickets to an agent."""
    
    def on_ticket_created(event: Event):
        """Handler for ticket creation events."""
        if event.data.get('priority') == 'critical':
            ticket_id = event.data.get('ticket_id')
            print(f"🚨 CRITICAL ticket created: {ticket_id}")
            print(f"   Auto-assigning to emergency response team...")
            # In real implementation:
            # agent_storage.auto_assign_task(ticket_id, 'urgent_fix', ...)
    
    event_bus = get_event_bus()
    event_bus.subscribe(EventType.TICKET_CREATED, on_ticket_created)
    print("✓ Subscribed to ticket.created events")
    print("  Critical tickets will be auto-assigned")


def example_test_on_code_complete():
    """Automatically start testing when code is complete."""
    
    def on_task_completed(event: Event):
        """Handler for agent task completion."""
        if event.data.get('task_type') == 'code':
            ticket_id = event.data.get('ticket_id')
            print(f"✅ Code completed for: {ticket_id}")
            print(f"   Automatically starting test phase...")
            # In real implementation:
            # agent_storage.auto_assign_task(ticket_id, 'test', ...)
    
    event_bus = get_event_bus()
    event_bus.subscribe(EventType.AGENT_TASK_COMPLETED, on_task_completed)
    print("✓ Subscribed to agent.task.completed events")
    print("  Tests will auto-start after code completion")


def example_milestone_tracking():
    """Track milestones and notify team."""
    
    closed_count = {'count': 0}
    
    def on_ticket_closed(event: Event):
        """Handler for ticket closing."""
        closed_count['count'] += 1
        
        # Check for milestone
        if closed_count['count'] % 10 == 0:
            print(f"🎉 MILESTONE: {closed_count['count']} tickets closed!")
            print(f"   Publishing milestone event...")
            
            event_bus = get_event_bus()
            event_bus.publish(
                EventType.MILESTONE_REACHED,
                {'milestone': f'{closed_count["count"]}_tickets_closed'},
                source='automation'
            )
    
    event_bus = get_event_bus()
    event_bus.subscribe(EventType.TICKET_CLOSED, on_ticket_closed)
    print("✓ Subscribed to ticket.closed events")
    print("  Milestones will be tracked")


def example_audit_logger():
    """Log all events for audit trail."""
    
    log_file = Path.cwd() / "event_audit.log"
    
    def log_all_events(event: Event):
        """Handler that logs all events."""
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{event.timestamp}] {event.type.value}: {event.data}\\n")
    
    event_bus = get_event_bus()
    event_bus.subscribe_all(log_all_events)
    print(f"✓ Subscribed to ALL events")
    print(f"  Audit log: {log_file}")


def example_agent_coordination():
    """Coordinate multiple agents through events."""
    
    workflow_state = {
        'design_complete': False,
        'code_complete': False,
        'test_complete': False,
    }
    
    def on_agent_task_completed(event: Event):
        """Coordinate workflow steps."""
        task_type = event.data.get('task_type')
        ticket_id = event.data.get('ticket_id')
        
        if task_type == 'design':
            workflow_state['design_complete'] = True
            print(f"✅ Design complete for {ticket_id}")
            print(f"   Starting code phase...")
            # Start code task
            
        elif task_type == 'code':
            if workflow_state['design_complete']:
                workflow_state['code_complete'] = True
                print(f"✅ Code complete for {ticket_id}")
                print(f"   Starting test phase...")
                # Start test task
            
        elif task_type == 'test':
            if workflow_state['code_complete']:
                workflow_state['test_complete'] = True
                print(f"✅ Test complete for {ticket_id}")
                print(f"   Feature fully implemented!")
                # Close ticket or move to review
    
    event_bus = get_event_bus()
    event_bus.subscribe(EventType.AGENT_TASK_COMPLETED, on_agent_task_completed)
    print("✓ Subscribed to agent task completion")
    print("  Workflow coordination active")


def example_notification_system():
    """Send notifications on important events."""
    
    def send_notification(event: Event):
        """Send notification for critical events."""
        event_str = event.type.value
        
        if event_str.startswith('ticket.') and event.data.get('priority') == 'critical':
            print(f"📧 NOTIFICATION: Critical {event_str}")
            print(f"   Ticket: {event.data.get('ticket_id')}")
            # In real implementation:
            # send_email(...) or send_slack_message(...)
        
        elif event_str == 'agent.task.failed':
            print(f"⚠️  ALERT: Agent task failed!")
            print(f"   Agent: {event.data.get('agent_id')}")
            print(f"   Error: {event.data.get('error')}")
            # Alert on-call engineer
    
    event_bus = get_event_bus()
    event_bus.subscribe_all(send_notification)
    print("✓ Notification system active")
    print("  Alerts configured for critical events")


def main():
    """Run example automation setups."""
    print("=" * 60)
    print("Event Bus Automation Examples")
    print("=" * 60)
    print()
    
    print("Setting up automation handlers...")
    print()
    
    # Set up various automations
    example_auto_assign_critical()
    print()
    
    example_test_on_code_complete()
    print()
    
    example_milestone_tracking()
    print()
    
    example_audit_logger()
    print()
    
    example_agent_coordination()
    print()
    
    example_notification_system()
    print()
    
    print("=" * 60)
    print("All automation handlers registered!")
    print("=" * 60)
    print()
    
    # Show current stats
    event_bus = get_event_bus()
    stats = event_bus.get_stats()
    print(f"Event Bus Status:")
    print(f"  Total Subscribers: {stats['total_subscribers']}")
    print(f"  Events Published: {stats['total_events']}")
    print()
    
    print("Now any ticket operations will trigger these handlers...")
    print("Try: tickets create \"Test\" --priority critical")
    print()


if __name__ == "__main__":
    main()
