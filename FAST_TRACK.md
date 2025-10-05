# Fast Track Guide: Complete Software Engineering Workflow with Repo-Tickets

This guide walks you through the complete software engineering lifecycle using repo-tickets - from initial user cases to fully tested features. Perfect for teams wanting to implement professional project management and quality assurance practices.

## Table of Contents

1. [Quick Setup](#quick-setup)
2. [Phase 1: Discovery & Requirements](#phase-1-discovery--requirements)
3. [Phase 2: Epic & Feature Planning](#phase-2-epic--feature-planning)
4. [Phase 3: User Stories & Acceptance Criteria](#phase-3-user-stories--acceptance-criteria)
5. [Phase 4: Development Tickets & Dependencies](#phase-4-development-tickets--dependencies)
6. [Phase 5: BDD Testing & Scenarios](#phase-5-bdd-testing--scenarios)
7. [Phase 6: Implementation & Tracking](#phase-6-implementation--tracking)
8. [Phase 7: Verification & Closure](#phase-7-verification--closure)
9. [Continuous Workflow](#continuous-workflow)
10. [Team Best Practices](#team-best-practices)

---

## Quick Setup

### Prerequisites
```bash
# Install repo-tickets
pip install -e .

# Initialize in your project
cd your-project
tickets init

# Verify installation
tickets --help
```

### Essential Configuration
```bash
# Set up your identity (if not already done)
git config user.name "Your Name"
git config user.email "your.email@company.com"

# Optional: Configure ticket preferences
tickets config
```

---

## Phase 1: Discovery & Requirements

### Step 1.1: Create Epic Ticket for High-Level Feature

Start with a high-level feature epic that represents a major piece of functionality.

**Example: E-commerce Shopping Cart**

```bash
# Create the epic ticket
tickets create "E-commerce Shopping Cart System" \
  --description "Implement complete shopping cart functionality allowing users to add, modify, and purchase items" \
  --priority high \
  --labels "epic,e-commerce,shopping-cart" \
  --estimate 120

# This creates: SHOPPING-1
```

### Step 1.2: Add Business Requirements

Define formal business requirements with clear acceptance criteria:

```bash
# Add core business requirement
tickets requirements add SHOPPING-1 \
  --title "Shopping Cart Persistence" \
  --description "Cart contents must persist across user sessions" \
  --priority critical \
  --criteria "Cart items saved to database on add/remove" \
  --criteria "Cart restored when user logs back in" \
  --criteria "Guest carts persist for 7 days" \
  --criteria "Registered user carts persist indefinitely"

# Add performance requirement
tickets requirements add SHOPPING-1 \
  --title "Cart Performance" \
  --description "Cart operations must be fast and responsive" \
  --priority high \
  --criteria "Add to cart completes in < 500ms" \
  --criteria "Cart page loads in < 2 seconds" \
  --criteria "Checkout process completes in < 10 seconds" \
  --criteria "Supports concurrent access by 1000+ users"

# Add integration requirement
tickets requirements add SHOPPING-1 \
  --title "Payment Integration" \
  --description "Integrate with multiple payment providers" \
  --priority high \
  --criteria "Stripe payment processing" \
  --criteria "PayPal payment option" \
  --criteria "Apple Pay for mobile" \
  --criteria "Secure tokenization of payment data"
```

### Step 1.3: Define Expected Business Outcomes

```bash
# Add measurable business results
tickets requirements result SHOPPING-1 \
  --description "Increase conversion rate by 15%" \
  --method automated \
  --criteria "A/B test shows 15% improvement" \
  --criteria "Statistical significance > 95%" \
  --criteria "Minimum 1000 users in test"

tickets requirements result SHOPPING-1 \
  --description "Reduce cart abandonment to < 30%" \
  --method automated \
  --criteria "Analytics show abandonment < 30%" \
  --criteria "Measured over 30-day period" \
  --criteria "Excludes known bot traffic"
```

---

## Phase 2: Epic & Feature Planning

### Step 2.1: Break Down into Feature Tickets

Create specific feature tickets for each major component:

```bash
# Feature 1: Cart Management
tickets create "Shopping Cart CRUD Operations" \
  --description "Core cart functionality - add, update, remove items" \
  --priority high \
  --labels "feature,cart,crud" \
  --estimate 24

# Feature 2: Cart Persistence  
tickets create "Shopping Cart Session Persistence" \
  --description "Save and restore cart contents across sessions" \
  --priority high \
  --labels "feature,cart,persistence" \
  --estimate 16

# Feature 3: Checkout Process
tickets create "Shopping Cart Checkout Flow" \
  --description "Complete checkout process with payment integration" \
  --priority high \
  --labels "feature,checkout,payment" \
  --estimate 32

# Feature 4: Cart UI/UX
tickets create "Shopping Cart User Interface" \
  --description "Responsive cart UI with modern design" \
  --priority medium \
  --labels "feature,ui,frontend" \
  --estimate 20
```

### Step 2.2: Establish Dependencies

```bash
# Update tickets to show dependencies
tickets update CART-2 --blocked_by CART-1  # Persistence needs CRUD first
tickets update CART-3 --blocked_by CART-1,CART-2  # Checkout needs both
tickets update CART-4 --related_to CART-1,CART-3  # UI works with CRUD and checkout
```

---

## Phase 3: User Stories & Acceptance Criteria

### Step 3.1: Define User Stories for Each Feature

**For CART-1 (CRUD Operations):**

```bash
# Primary user story
tickets requirements story CART-1 \
  --persona "online shopper" \
  --goal "add products to my cart easily" \
  --benefit "I can collect items before making a purchase decision" \
  --priority high \
  --points 8 \
  --criteria "Add to cart button visible on product pages" \
  --criteria "Cart icon updates with item count" \
  --criteria "Visual confirmation when item added"

# Secondary user story
tickets requirements story CART-1 \
  --persona "online shopper" \
  --goal "modify quantities and remove items from my cart" \
  --benefit "I can adjust my order before checkout" \
  --priority high \
  --points 5 \
  --criteria "Quantity controls on cart page" \
  --criteria "Remove item button for each cart item" \
  --criteria "Total price updates automatically"

# Edge case story
tickets requirements story CART-1 \
  --persona "mobile user" \
  --goal "manage my cart on small screens" \
  --benefit "I can shop effectively on my phone" \
  --priority medium \
  --points 3 \
  --criteria "Touch-friendly cart controls" \
  --criteria "Swipe to remove items" \
  --criteria "Responsive design for mobile"
```

**For CART-2 (Persistence):**

```bash
# Guest user story
tickets requirements story CART-2 \
  --persona "guest shopper" \
  --goal "keep my cart items when I close the browser" \
  --benefit "I don't lose my selection if I need to continue later" \
  --priority high \
  --points 5 \
  --criteria "Cart saved to localStorage" \
  --criteria "Cart restored on page reload" \
  --criteria "Cart persists for 7 days"

# Registered user story
tickets requirements story CART-2 \
  --persona "registered user" \
  --goal "access my cart from any device" \
  --benefit "I can start shopping on mobile and finish on desktop" \
  --priority high \
  --points 8 \
  --criteria "Cart synced to user account" \
  --criteria "Cart available across devices" \
  --criteria "Cart merges when logging in"
```

---

## Phase 4: Development Tickets & Dependencies

### Step 4.1: Create Technical Implementation Tickets

Break each feature into implementable development tasks:

**Backend Development Tickets:**

```bash
# Database schema
tickets create "Cart Database Schema Design" \
  --description "Design and implement database tables for cart functionality" \
  --priority high \
  --labels "backend,database,schema" \
  --estimate 4

# API endpoints
tickets create "Cart REST API Endpoints" \
  --description "Implement RESTful API for cart operations" \
  --priority high \
  --labels "backend,api,rest" \
  --estimate 8

# Business logic
tickets create "Cart Business Logic Implementation" \
  --description "Implement cart validation, pricing, and business rules" \
  --priority high \
  --labels "backend,logic,validation" \
  --estimate 6
```

**Frontend Development Tickets:**

```bash
# React components
tickets create "Cart React Components" \
  --description "Build reusable cart components (CartItem, CartSummary, etc.)" \
  --priority high \
  --labels "frontend,react,components" \
  --estimate 12

# State management
tickets create "Cart State Management" \
  --description "Implement Redux/Context for cart state management" \
  --priority high \
  --labels "frontend,state,redux" \
  --estimate 6

# Integration
tickets create "Cart Frontend-Backend Integration" \
  --description "Connect frontend cart with backend APIs" \
  --priority high \
  --labels "integration,api,frontend" \
  --estimate 4
```

### Step 4.2: Add Technical Requirements

Add technical specifications to development tickets:

```bash
# API requirements
tickets requirements add API-1 \
  --title "RESTful API Design" \
  --description "Follow REST principles for cart endpoints" \
  --priority high \
  --criteria "GET /api/cart returns current cart" \
  --criteria "POST /api/cart/items adds item to cart" \
  --criteria "PUT /api/cart/items/:id updates quantity" \
  --criteria "DELETE /api/cart/items/:id removes item"

# Performance requirements
tickets requirements add API-1 \
  --title "API Performance" \
  --description "API must be fast and efficient" \
  --priority medium \
  --criteria "Response time < 200ms for 95% of requests" \
  --criteria "Supports 100 concurrent users" \
  --criteria "Proper HTTP caching headers" \
  --criteria "Database queries optimized"
```

---

## Phase 5: BDD Testing & Scenarios

### Step 5.1: Create Comprehensive Gherkin Scenarios

**Happy Path Scenarios:**

```bash
# Basic cart operations
tickets requirements gherkin CART-1 \
  --title "Add item to empty cart" \
  --given "I am on the product page for 'iPhone 14'" \
  --given "My cart is empty" \
  --when "I click the 'Add to Cart' button" \
  --then "The item should be added to my cart" \
  --then "The cart icon should show '1' item" \
  --then "I should see a success notification" \
  --tags "cart,add-item,happy-path"

# Cart modification
tickets requirements gherkin CART-1 \
  --title "Update item quantity in cart" \
  --given "I have 1 iPhone 14 in my cart" \
  --given "I am on the cart page" \
  --when "I change the quantity to 2" \
  --when "I click outside the quantity input" \
  --then "The cart should show 2 iPhone 14s" \
  --then "The total price should update automatically" \
  --then "The cart icon should show '2' items" \
  --tags "cart,quantity,update"
```

**Edge Cases and Error Scenarios:**

```bash
# Out of stock handling
tickets requirements gherkin CART-1 \
  --title "Handle out of stock items" \
  --given "I have an iPhone 14 in my cart" \
  --given "The iPhone 14 goes out of stock" \
  --when "I view my cart" \
  --then "I should see an 'out of stock' notice for the iPhone" \
  --then "The checkout button should be disabled" \
  --then "I should have option to remove or save for later" \
  --tags "cart,out-of-stock,error-handling"

# Cart persistence testing
tickets requirements gherkin CART-2 \
  --title "Cart persists across browser sessions" \
  --given "I am a guest user" \
  --given "I have added 3 items to my cart" \
  --when "I close my browser" \
  --when "I reopen the browser and visit the site" \
  --then "My cart should still contain the 3 items" \
  --then "The cart total should be unchanged" \
  --tags "persistence,guest-user,browser-session"
```

**Integration Testing Scenarios:**

```bash
# End-to-end checkout
tickets requirements gherkin CART-3 \
  --title "Complete checkout process" \
  --given "I have items in my cart worth $150" \
  --given "I am a registered user" \
  --when "I proceed to checkout" \
  --when "I enter my shipping information" \
  --when "I select credit card payment" \
  --when "I enter valid payment details" \
  --when "I click 'Place Order'" \
  --then "My order should be created" \
  --then "I should receive an order confirmation" \
  --then "My cart should be empty" \
  --then "I should receive a confirmation email" \
  --tags "checkout,end-to-end,payment,integration"
```

**Performance Testing Scenarios:**

```bash
# Load testing scenario
tickets requirements gherkin CART-1 \
  --title "Cart performance under load" \
  --given "The system has 1000 concurrent users" \
  --given "Each user has items in their cart" \
  --when "Users simultaneously add items to cart" \
  --then "95% of add-to-cart requests complete within 500ms" \
  --then "No cart data is lost or corrupted" \
  --then "Cart totals remain accurate" \
  --tags "performance,load-testing,concurrency"
```

---

## Phase 6: Implementation & Tracking

### Step 6.1: Start Development with Time Tracking

```bash
# Begin work on first ticket
tickets update SCHEMA-1 --status in-progress --assignee "julio"

# Start time tracking
tickets time SCHEMA-1 --start --description "Designing cart database schema"

# Log progress with journal entries
tickets journal SCHEMA-1 "Completed initial database design" \
  --type progress \
  --completion 30 \
  --spent 2.5 \
  --milestone "Schema Design"
```

### Step 6.2: Update Requirements as You Learn

```bash
# Update requirement status as work progresses
# (Programmatically, you'd load and modify the ticket)

# Example: Mark a requirement as implemented
tickets show CART-1  # Review current requirements
# Then manually update requirement status through the models
```

### Step 6.3: Continuous Testing Updates

```bash
# Update test scenarios as development progresses
tickets requirements gherkin CART-1 \
  --title "API error handling for invalid requests" \
  --given "I am using the cart API" \
  --when "I send a POST request with invalid product ID" \
  --then "I should receive a 400 Bad Request response" \
  --then "The error message should be descriptive" \
  --then "My cart should remain unchanged" \
  --tags "api,error-handling,validation"
```

---

## Phase 7: Verification & Closure

### Step 7.1: Verify Expected Results

```bash
# Mark expected results as verified
tickets requirements verify CART-1 RESULT-123 \
  --notes "Performance tests show average 150ms response time, well under 500ms requirement"

# Add verification for business outcomes
tickets requirements verify SHOPPING-1 RESULT-456 \
  --notes "A/B test completed: 18% conversion improvement, exceeding 15% target"
```

### Step 7.2: Update Test Scenarios Status

```bash
# Update Gherkin scenarios as tests pass/fail
# (This would typically be done programmatically via test automation)
python -c "
from repo_tickets.storage import TicketStorage
storage = TicketStorage()
ticket = storage.load_ticket('CART-1')
scenario = ticket.get_gherkin_scenario('SCENARIO-123')
scenario.status = 'passing'
storage.save_ticket(ticket)
print('Updated scenario status to passing')
"
```

### Step 7.3: Generate Reports and Close Tickets

```bash
# Generate comprehensive project report
tickets report

# Check overall project status
tickets status --format detailed

# Close completed tickets
tickets close SCHEMA-1 --comment "Database schema implemented and tested"
tickets close API-1 --comment "All cart API endpoints implemented with full test coverage"
```

---

## Continuous Workflow

### Daily Workflow

```bash
# Morning: Check status and plan day
tickets status
tickets list --assignee julio --status open

# Start working on highest priority ticket
tickets update NEXT-TICKET --status in-progress
tickets time NEXT-TICKET --start --description "Working on user authentication"

# End of day: Log progress and stop tracking
tickets journal NEXT-TICKET "Implemented login validation logic" \
  --type progress \
  --completion 60 \
  --spent 6
tickets time NEXT-TICKET --stop
```

### Sprint/Weekly Workflow

```bash
# Sprint planning: Review backlog
tickets list --status open --priority high
tickets report  # Generate comprehensive report

# Sprint review: Check velocity and completion
tickets status --generate-report --update-readme
```

### Release Workflow

```bash
# Pre-release: Verify all requirements met
tickets list --status open --priority critical  # Should be empty
python -c "
from repo_tickets.storage import TicketStorage
storage = TicketStorage()
tickets = storage.list_tickets()
for t in tickets:
    if t.status == 'closed':
        summary = t.get_requirements_summary()
        print(f'{t.id}: {summary[\"verification_rate\"]}% verified')
"

# Release notes: Generate from tickets
tickets search "milestone:v1.0" --format json > release_tickets.json
```

---

## Team Best Practices

### 1. Requirement Definition Standards

```bash
# Always include measurable acceptance criteria
tickets requirements add TICKET-1 \
  --title "Clear, Specific Requirement" \
  --criteria "Specific numeric target (e.g., < 2 seconds)" \
  --criteria "Observable behavior (e.g., user sees confirmation)" \
  --criteria "Boundary conditions (e.g., handles 1000+ items)"
```

### 2. User Story Best Practices

```bash
# Follow INVEST principles: Independent, Negotiable, Valuable, Estimable, Small, Testable
tickets requirements story TICKET-1 \
  --persona "specific user type (not just 'user')" \
  --goal "specific action they want to take" \
  --benefit "clear value they get from the action" \
  --points 3  # Small enough to complete in 1-2 days
```

### 3. Gherkin Scenario Guidelines

```bash
# Use consistent language and avoid technical implementation details
tickets requirements gherkin TICKET-1 \
  --title "Focus on user behavior, not system internals" \
  --given "Business context, not technical state" \
  --when "User action in business terms" \
  --then "Observable outcome from user perspective" \
  --tags "feature-area,test-type,risk-level"
```

### 4. Dependency Management

```bash
# Keep dependencies explicit and minimal
tickets update TICKET-A --blocks TICKET-B  # A must finish before B
tickets update TICKET-C --related_to TICKET-A  # C and A are related but not dependent
```

### 5. Estimation and Planning

```bash
# Use relative sizing for story points
# 1 point = simple change (few hours)
# 3 points = moderate feature (1-2 days)  
# 5 points = complex feature (3-4 days)
# 8 points = large feature (1 week)
# 13+ points = epic, needs breaking down
```

### 6. Continuous Integration

```bash
# Automate scenario status updates in CI/CD
cat > .github/workflows/update-tickets.yml << 'EOF'
name: Update Ticket Status
on: [push, pull_request]
jobs:
  update-scenarios:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests and update scenarios
        run: |
          # Run your tests
          npm test -- --json > test-results.json
          # Update scenario status based on results
          python scripts/update_scenarios.py test-results.json
EOF
```

---

## Complete Example Walkthrough

Here's a condensed example showing the complete flow:

```bash
# 1. Create epic
tickets create "User Authentication System" --priority high --estimate 40

# 2. Add business requirements  
tickets requirements add AUTH-1 --title "Secure Login" --priority critical
tickets requirements story AUTH-1 --persona "user" --goal "log in securely" --benefit "access my account"

# 3. Break into development tasks
tickets create "Login API Endpoints" --priority high --estimate 8
tickets create "Password Hashing" --priority high --estimate 4  
tickets create "Session Management" --priority high --estimate 6

# 4. Add comprehensive testing
tickets requirements gherkin LOGIN-1 --title "Valid login attempt" \
  --given "I have a valid account" \
  --when "I enter correct credentials" \
  --then "I should be logged in"

# 5. Implement with tracking
tickets update LOGIN-1 --status in-progress
tickets time LOGIN-1 --start
# ... do the work ...
tickets time LOGIN-1 --stop

# 6. Verify and close
tickets requirements verify AUTH-1 RESULT-123 --notes "Security audit passed"
tickets close LOGIN-1
```

This creates a complete audit trail from business need to verified implementation, with full traceability and professional project management throughout the software engineering lifecycle.

---

## Quick Reference Commands

```bash
# Essential daily commands
tickets status                              # Project overview
tickets list --assignee me --status open    # My open tickets
tickets show TICKET-1                       # Full ticket details
tickets requirements list TICKET-1          # All requirements for ticket
tickets time TICKET-1 --start              # Start time tracking
tickets journal TICKET-1 "Progress update" # Log progress
tickets report                              # Generate HTML report

# Requirement management
tickets requirements add TICKET-1 --title "..." --criteria "..." 
tickets requirements story TICKET-1 --persona "..." --goal "..." --benefit "..."
tickets requirements result TICKET-1 --description "..." --method automated
tickets requirements gherkin TICKET-1 --title "..." --given "..." --when "..." --then "..."
tickets requirements verify TICKET-1 RESULT-ID --notes "..."

# Project tracking
tickets status --update-readme             # Update README with metrics
tickets status --generate-report           # Generate STATUS.md
tickets report                             # Interactive HTML dashboard
```

This fast-track guide provides everything needed to implement professional software engineering practices with comprehensive requirement tracking, from initial user cases through tested, verified implementations.