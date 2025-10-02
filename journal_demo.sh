#!/bin/bash
set -e

echo "📊 Advanced Journaling & PM Tracking Demo"
echo "=========================================="
echo

# Clean up and create demo project
rm -rf journal-demo
mkdir journal-demo
cd journal-demo

echo "1. Setting up demo project with PM tracking..."
git init -q
git config user.name "Project Manager"
git config user.email "pm@company.com"

# Initialize tickets
tickets init -q

echo "2. Creating tickets with effort estimates..."

# Create tickets with estimates
tickets create "User Authentication System" \
  -d "Implement secure JWT-based authentication with role-based access control" \
  -p critical -l security,backend --estimate 24 --points 8

tickets create "Real-time Chat Feature" \
  -d "Add WebSocket-based real-time messaging between users" \
  -p high -l feature,frontend --estimate 32 --points 13

tickets create "Performance Optimization" \
  -d "Optimize database queries and implement Redis caching" \
  -p medium -l performance,backend --estimate 16 --points 5

echo "3. Starting comprehensive PM tracking workflow..."

# Simulate development workflow with time tracking
echo "   🔄 Starting work on authentication system..."
tickets time USER-1 --start --description "Setting up JWT library and basic structure" --type work

echo "   ⏳ Simulating 30 seconds of work..."
sleep 2  # Simulating work time

tickets time USER-1 --stop

# Add some completed time with different types
tickets time USER-1 --add 180 --description "JWT implementation and testing" --type work
tickets time USER-1 --add 45 --description "Security architecture review meeting" --type meeting
tickets time USER-1 --add 60 --description "Researching OAuth2 integration options" --type research

echo "   📊 Adding comprehensive journal entries..."

# Add progress journal entry with metrics
tickets journal USER-1 \
  "Completed core JWT implementation. Token generation and validation working." \
  --type progress \
  --spent 4.5 \
  --completion 40 \
  --milestone "Core Auth Complete"

# Add risk assessment
tickets journal USER-1 \
  "Identified security concerns with token storage in localStorage." \
  --type risk \
  --risks "XSS vulnerability with localStorage,Token lifetime management complexity" \
  --dependencies "SECURITY-AUDIT"

# Add decision entry
tickets journal USER-1 \
  "Decision: Use httpOnly cookies for token storage instead of localStorage." \
  --type decision

# Work on chat feature with different tracking
echo "   💬 Working on chat feature..."
tickets time REAL-1 --add 240 --description "WebSocket server implementation" --type work
tickets time REAL-1 --add 90 --description "Frontend WebSocket client integration" --type work
tickets time REAL-1 --add 30 --description "Daily standup meeting" --type meeting

# Add milestone with dependencies
tickets journal REAL-1 \
  "WebSocket infrastructure complete. Ready for message persistence layer." \
  --type milestone \
  --completion 55 \
  --milestone "WebSocket Infrastructure" \
  --dependencies "PERFORMA-1" \
  --estimate 8

# Add blocked entry
tickets journal REAL-1 \
  "Message persistence blocked pending database optimization completion." \
  --type blocker \
  --dependencies "PERFORMA-1" \
  --risks "Chat feature delivery may be delayed"

# Performance work with multiple sessions
echo "   ⚡ Performance optimization work..."
tickets time PERFORMA-1 --add 120 --description "Database query analysis and indexing" --type work
tickets time PERFORMA-1 --add 90 --description "Redis cache implementation" --type work
tickets time PERFORMA-1 --add 60 --description "Load testing and benchmarking" --type testing

# Progress tracking with completion updates
tickets journal PERFORMA-1 \
  "Database optimization complete. 40% performance improvement achieved." \
  --type progress \
  --completion 70 \
  --spent 4.5

tickets journal PERFORMA-1 \
  "Redis caching implemented for user sessions and frequently accessed data." \
  --type milestone \
  --milestone "Caching Layer Complete" \
  --completion 85

echo "4. Demonstrating advanced PM features..."

# Update ticket statuses based on progress
tickets update USER-1 -s in-progress
tickets update REAL-1 -s blocked
tickets update PERFORMA-1 -s in-progress

# Add some meeting time tracking
echo "   🤝 Sprint planning and reviews..."
tickets time USER-1 --add 90 --description "Sprint planning and backlog refinement" --type meeting
tickets time REAL-1 --add 60 --description "Architecture review with senior dev" --type meeting
tickets time PERFORMA-1 --add 45 --description "Performance metrics review with stakeholders" --type meeting

echo "5. Generating comprehensive PM reports..."

# Show detailed ticket information
echo "   📋 Authentication System Progress:"
tickets show USER-1

echo
echo "   ⏱️ Time Tracking Summaries:"
echo "   Authentication System:"
tickets time USER-1

echo
echo "   Chat Feature:"
tickets time REAL-1

echo
echo "   Performance Optimization:"
tickets time PERFORMA-1

echo
echo "6. Project Management Analytics:"

# Show overall project stats
tickets stats

echo
echo "✨ Advanced Journaling & PM Features Demonstrated:"
echo "================================================="
echo
echo "📊 Performance Metrics:"
echo "   • Effort estimation and tracking"
echo "   • Story points for agile planning" 
echo "   • Completion percentage monitoring"
echo "   • Time spent vs. estimated analysis"
echo
echo "⏱️ Time Tracking:"
echo "   • Start/stop time sessions"
echo "   • Manual time entry for completed work"
echo "   • Work type categorization (work, meeting, research, etc.)"
echo "   • Detailed time logging with descriptions"
echo
echo "📝 Journal Entry Types:"
echo "   • Progress updates with completion tracking"
echo "   • Risk identification and assessment"
echo "   • Decision documentation"
echo "   • Milestone achievement tracking"
echo "   • Blocker identification with dependencies"
echo "   • Meeting notes and outcomes"
echo
echo "🎯 Project Management:"
echo "   • Dependency tracking between tickets"
echo "   • Risk assessment and mitigation"
echo "   • Milestone tracking and reporting"
echo "   • Resource allocation insights"
echo "   • Velocity and capacity planning"
echo
echo "📈 Advanced Analytics:"
echo "   • Time breakdown by work type"
echo "   • Effort variance analysis (estimated vs. actual)"
echo "   • Team productivity metrics"
echo "   • Risk and blocker trend analysis"
echo "   • Milestone completion tracking"
echo
echo "🎨 Professional Benefits:"
echo "   • Executive dashboard-ready metrics"
echo "   • Agile/Scrum process integration"
echo "   • Historical performance analysis"
echo "   • Resource planning and forecasting"
echo "   • Compliance and audit trail"
echo
echo "🚀 Use Cases:"
echo "   • Sprint retrospectives and planning"
echo "   • Performance reviews and evaluations"
echo "   • Project health monitoring"
echo "   • Resource allocation decisions"
echo "   • Client billing and time tracking"
echo "   • Process improvement analysis"

echo
echo "✅ Full PM tracking workflow completed!"
echo "📄 Try: tickets show USER-1 to see comprehensive ticket details"