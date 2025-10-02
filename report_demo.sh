#!/bin/bash
set -e

echo "🎯 Advanced HTML Reporting Demo"
echo "==============================="
echo

# Clean up any existing demo directory
rm -rf report-demo
mkdir report-demo
cd report-demo

# Initialize a git repository
echo "1. Setting up demo project..."
git init -q
git config user.name "Report Demo User"
git config user.email "demo@example.com"

# Initialize tickets
tickets init -q

echo "2. Creating comprehensive project tickets..."

# Create a variety of tickets to showcase analytics
tickets create "User Authentication System" \
  -d "Implement JWT-based authentication with role-based access control" \
  -p critical -l security,backend

tickets create "Mobile App Development" \
  -d "Build native iOS and Android applications" \
  -p high -l mobile,frontend

tickets create "Payment Integration" \
  -d "Integrate with Stripe and PayPal payment processors" \
  -p high -l backend,integration

tickets create "Performance Optimization" \
  -d "Optimize database queries and implement caching" \
  -p medium -l performance,backend

tickets create "API Documentation" \
  -d "Create comprehensive API documentation using OpenAPI/Swagger" \
  -p low -l documentation

tickets create "Dark Mode Implementation" \
  -d "Add dark theme support to web and mobile interfaces" \
  -p medium -l frontend,enhancement

tickets create "Security Audit" \
  -d "Conduct comprehensive security assessment and penetration testing" \
  -p critical -l security,testing

tickets create "Data Migration Tool" \
  -d "Build tool to migrate data from legacy system" \
  -p high -l backend,migration

tickets create "Unit Test Coverage" \
  -d "Increase unit test coverage to 90%+ across all components" \
  -p medium -l testing,quality

tickets create "CI/CD Pipeline Setup" \
  -d "Implement automated testing and deployment pipeline" \
  -p medium -l devops,infrastructure

echo "3. Simulating development progress..."

# Assign tickets to team members
tickets update USER-1 -s in-progress -a "Alice Johnson (Security Lead)"
tickets update MOBILE-1 -s in-progress -a "Bob Smith (Mobile Dev)"
tickets update PAYMENT-1 -a "Carol Williams (Backend Dev)"
tickets update PERFORMA-1 -a "Dave Brown (DevOps Engineer)"
tickets update SECURITY-1 -s blocked -a "Alice Johnson (Security Lead)"
tickets update DATA-1 -s in-progress -a "Eve Davis (Data Engineer)"

# Add realistic progress comments
tickets comment USER-1 "JWT implementation completed. Working on role-based permissions."
tickets comment USER-1 "Added password strength requirements and MFA support."

tickets comment MOBILE-1 "iOS app foundation completed. Starting Android development."
tickets comment MOBILE-1 "Implementing biometric authentication for mobile login."

tickets comment SECURITY-1 "Blocked pending completion of authentication system (USER-1)."

tickets comment DATA-1 "Analyzed legacy database schema. Creating migration scripts."

# Close some tickets to show completion
tickets close API-1  # This will be marked as closed
tickets comment UNIT-1 "Test coverage increased from 45% to 78%. Continuing work."

echo "4. Creating critical bug tickets..."

tickets create "Login fails on mobile Safari" \
  -d "Users cannot login on iPhone Safari browser due to session cookie issues" \
  -p critical -l bug,mobile,urgent

tickets create "Payment processing timeout" \
  -d "Credit card payments randomly timeout during checkout process" \
  -p critical -l bug,payment,urgent

tickets create "Database connection leak" \
  -d "Connection pool exhaustion causing application crashes" \
  -p high -l bug,database

# Assign critical bugs
tickets update LOGIN-1 -s in-progress -a "Bob Smith (Mobile Dev)"
tickets update PAYMENT-2 -s blocked -a "Carol Williams (Backend Dev)"
tickets update DATABASE-1 -a "Dave Brown (DevOps Engineer)"

# Add investigation comments
tickets comment LOGIN-1 "Reproduced issue. Investigating Safari cookie handling."
tickets comment PAYMENT-2 "Identified race condition in payment processing. Blocked on vendor fix."

echo "5. Adding feature requests..."

tickets create "Real-time Notifications" \
  -d "Implement WebSocket-based real-time notifications for users" \
  -p medium -l feature,frontend,backend

tickets create "Advanced Analytics Dashboard" \
  -d "Create comprehensive analytics dashboard for business metrics" \
  -p low -l feature,analytics,frontend

tickets create "Multi-language Support" \
  -d "Add internationalization (i18n) support for Spanish and French" \
  -p low -l feature,frontend

echo "6. Generating comprehensive HTML report..."

# Generate the report
tickets report --output project_report.html

echo
echo "✨ Professional HTML Report Features:"
echo "====================================="
echo
echo "🎨 Modern Design:"
echo "   • Glass-morphism cards with blur effects"
echo "   • Gradient backgrounds and smooth animations"
echo "   • Responsive layout for mobile and desktop"
echo "   • Professional typography and color schemes"
echo
echo "📊 Interactive Analytics:"
echo "   • Status distribution (doughnut chart)"
echo "   • Priority distribution (bar chart)" 
echo "   • Team workload analysis (horizontal bar chart)"
echo "   • Project progress tracking with completion percentage"
echo
echo "⚠️  Risk Assessment:"
echo "   • Automated risk scoring (0-100 scale)"
echo "   • Blocked ticket identification"
echo "   • Stale ticket detection (30+ days)"
echo "   • Critical open issues tracking"
echo
echo "🚀 Velocity Metrics:"
echo "   • Weekly/monthly closure rates"
echo "   • Average resolution time"
echo "   • Projected annual velocity"
echo
echo "🔍 Smart Filtering:"
echo "   • Filter tickets by status, priority, labels"
echo "   • Real-time JavaScript filtering"
echo "   • Visual indicators for risk levels"
echo
echo "📅 Activity Timeline:"
echo "   • Recent ticket creation and comments"
echo "   • Color-coded activity types"
echo "   • Chronological event tracking"
echo
echo "✅ Report successfully generated and opened in browser!"
echo "📄 File location: $(pwd)/project_report.html"
echo

# Show final stats
echo "📈 Project Summary:"
tickets stats

echo
echo "🎯 Use Cases for HTML Reports:"
echo "• Executive stakeholder presentations"
echo "• Sprint retrospectives and planning"
echo "• Project health monitoring" 
echo "• Team performance analysis"
echo "• Risk assessment and mitigation"
echo "• Historical project documentation"