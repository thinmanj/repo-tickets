#!/usr/bin/env python3
"""
Demo script for the repo-tickets TUI interface.

This demonstrates the TUI capabilities and usage patterns.
"""

import os
import sys
from pathlib import Path

def main():
    """Run TUI demo."""
    print("🎫 Repo Tickets TUI Demo")
    print("=" * 50)
    
    # Add the repo_tickets module to path
    repo_root = Path(__file__).parent
    sys.path.insert(0, str(repo_root))
    
    try:
        from repo_tickets.tui import run_tui
        from repo_tickets.storage import TicketStorage
        
        # Check if tickets are initialized
        storage = TicketStorage()
        if not storage.is_initialized():
            print("❌ Tickets not initialized in this repository!")
            print("Run 'tickets init' first to initialize the ticket system.")
            return
        
        # Show current tickets
        tickets = storage.list_tickets()
        print(f"\nFound {len(tickets)} tickets in the repository:")
        for ticket in tickets:
            status_icon = {
                'open': '🔵',
                'in-progress': '🟡', 
                'blocked': '🔴',
                'closed': '✅'
            }.get(ticket.status, '⚪')
            
            priority_icon = {
                'critical': '🔥',
                'high': '🟠',
                'medium': '🟢',
                'low': '🔵'
            }.get(ticket.priority, '⚪')
            
            print(f"  {status_icon} {ticket.id}: {ticket.title} ({priority_icon} {ticket.priority})")
        
        print("🚀 Features of the TUI interface:")
        print("  • Interactive ticket browsing with filtering")
        print("  • Real-time search across titles, descriptions, and IDs")
        print("  • Detailed ticket views with collapsible sections")
        print("  • Modal forms for creating tickets and adding journal entries")
        print("  • Time tracking with start/stop/add capabilities")
        print("  • Live project metrics (completion rates, time tracking, risk assessment)")
        print("  • ✨ Comprehensive keyboard shortcuts for power users")
        print("  • Modern terminal styling with emojis and colors")
        print("  • HTML report generation with browser integration")
        
        print("\n📋 Key TUI Commands:")
        print("  • Filter tickets by status: All, Open, In Progress, Blocked, Closed")
        print("  • Filter by priority: Critical, High")
        print("  • Click any ticket row to view detailed information")
        print("  • Use 'New Ticket' button to create new tickets")
        print("  • 'Refresh' button to reload data")
        print("  • 'Generate Report' to create HTML reports")
        
        print("\n⌨️  Keyboard Shortcuts (Power User Mode):")
        print("  • Press ? for full help screen")
        print("  • n = New ticket, r = Refresh, g = Generate report")
        print("  • / = Focus search, q = Quit")
        print("  • 1-7 = Quick filters (All, Open, Progress, Blocked, Closed, Critical, High)")
        print("  • In ticket details: j = Journal, t = Time tracking")
        print("  • Ctrl+L = Clear search, Esc = Back/Clear")
        
        print("\n⌨️  Ready to launch TUI!")
        print("Press Enter to start the interactive TUI, or Ctrl+C to exit...")
        
        try:
            input()
            print("🎨 Launching TUI interface...")
            
            # Launch the TUI
            run_tui()
            
        except KeyboardInterrupt:
            print("\n👋 Demo cancelled by user.")
            
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Install with: pip install textual rich")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()