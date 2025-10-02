#!/bin/bash
set -e

echo "🎫 Repo-Tickets Demo"
echo "===================="
echo

# Clean up any existing demo directory
rm -rf demo-showcase
mkdir demo-showcase
cd demo-showcase

# Initialize a git repository
echo "1. Creating a git repository..."
git init -q
git config user.name "Demo User"
git config user.email "demo@example.com"
echo "   ✓ Git repository initialized"
echo

# Initialize tickets
echo "2. Initializing ticket system..."
tickets init
echo

# Create some demo tickets
echo "3. Creating demo tickets..."
tickets create "Fix authentication bug" \
  -d "Users cannot login when password contains special characters like @ or #" \
  -p high \
  -l bug,security

tickets create "Add user profile page" \
  -d "Create a user profile page where users can view and edit their information" \
  -p medium \
  -l feature

tickets create "Update documentation" \
  -d "API documentation is outdated and needs to be refreshed with latest changes" \
  -p low \
  -l documentation

tickets create "Performance optimization" \
  -d "Database queries are slow on the reports page" \
  -p critical \
  -l bug,performance
echo

# Show ticket list
echo "4. Listing all tickets..."
tickets list
echo

# Update a ticket
echo "5. Updating ticket status..."
tickets update FIX-1 -s in-progress -a "Demo User"
tickets comment FIX-1 "Started investigating the authentication flow"
echo

# Search tickets
echo "6. Searching for bugs..."
tickets search "bug"
echo

# Show detailed ticket info
echo "7. Showing ticket details..."
tickets show FIX-1
echo

# Show statistics
echo "8. Ticket statistics..."
tickets stats
echo

# Show configuration
echo "9. Current configuration..."
tickets config
echo

echo "✅ Demo completed successfully!"
echo
echo "📁 Tickets are stored in .tickets/ directory:"
find .tickets -type f -name "*.yaml" | head -5

echo
echo "🎉 The ticket system works with:"
echo "   • Git repositories ✓"
echo "   • Mercurial repositories ✓" 
echo "   • Jujutsu repositories ✓"
echo
echo "🚀 Try it yourself with:"
echo "   tickets init"
echo "   tickets create 'My first ticket' -d 'Description here'"