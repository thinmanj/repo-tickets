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

### Step 1.1: Create Epic for High-Level Feature

Start with a proper epic that represents a major piece of functionality spanning multiple sprints.

**Example: E-commerce Shopping Cart**

```bash
# Create the epic with comprehensive metadata
tickets epic create "E-commerce Shopping Cart System" \
  --description "Implement complete shopping cart functionality allowing users to add, modify, and purchase items" \
  --priority high \
  --owner "Product Team" \
  --target-version "v2.0" \
  --target-date "2024-12-31" \
  --estimated-points 120 \
  --labels "e-commerce,shopping-cart,revenue"

# This creates: ECOMMERCE-1
```

### Step 1.2: Define Epic Goals and Success Criteria

Add high-level goals and measurable success criteria to the epic:

```bash
# Add epic goals (these define what success looks like)
tickets epic show ECOMMERCE-1  # View current epic details

# Add epic goals and success criteria through update
tickets epic update ECOMMERCE-1 \
  --description "Complete shopping cart functionality with:

Goals:
- Seamless cart persistence across user sessions
- Sub-500ms cart operations for optimal UX
- Multi-provider payment integration
- Mobile-optimized responsive design

Success Criteria:
- Increase conversion rate by 15%
- Reduce cart abandonment to < 30%
- Support 1000+ concurrent users
- 99.9% payment processing uptime"
```

### Step 1.3: Create Product Backlog Items

Break down the epic into prioritized backlog items:

```bash
# Add high-priority backlog items
tickets backlog add "Shopping Cart CRUD Operations" \
  --description "Core cart functionality - add, update, remove items" \
  --type feature \
  --priority high \
  --story-points 8 \
  --business-value 90 \
  --effort-estimate 16 \
  --risk-level medium \
  --epic-id ECOMMERCE-1 \
  --component "Cart Management" \
  --theme "Core Shopping Experience"

tickets backlog add "Cart Session Persistence" \
  --description "Save and restore cart contents across user sessions" \
  --type feature \
  --priority high \
  --story-points 5 \
  --business-value 85 \
  --effort-estimate 12 \
  --risk-level low \
  --epic-id ECOMMERCE-1 \
  --component "Data Management" \
  --theme "User Experience"

tickets backlog add "Payment Integration" \
  --description "Integrate with Stripe, PayPal, and Apple Pay" \
  --type feature \
  --priority critical \
  --story-points 13 \
  --business-value 95 \
  --effort-estimate 24 \
  --risk-level high \
  --epic-id ECOMMERCE-1 \
  --component "Payments" \
  --theme "Revenue Generation"

tickets backlog add "Mobile Cart Interface" \
  --description "Responsive cart UI optimized for mobile devices" \
  --type feature \
  --priority medium \
  --story-points 8 \
  --business-value 70 \
  --effort-estimate 18 \
  --risk-level low \
  --epic-id ECOMMERCE-1 \
  --component "Frontend" \
  --theme "Mobile Experience"
```

### Step 1.4: Review Prioritized Backlog

```bash
# View automatically prioritized backlog
tickets backlog list --epic ECOMMERCE-1

# Items are automatically sorted by priority score:
# Score = (Priority × 100) + Business Value - (Story Points × 2)
# This ensures optimal value/effort balance for sprint planning
```

---

## Phase 2: Sprint Planning & Backlog Grooming

### Step 2.1: Groom Backlog Items for Development

Prepare high-priority backlog items with detailed acceptance criteria:

```bash
# View top-priority items
tickets backlog list --status new

# Groom the highest-priority item by adding acceptance criteria
# (Note: This is conceptual - full backlog item editing in future CLI update)
echo "Acceptance Criteria for SHOPPI-1:
- User can add products to cart from product pages
- Cart icon shows item count in real-time
- Visual confirmation appears when items are added
- Quantity can be updated directly in cart
- Items can be removed with confirmation
- Cart totals update automatically" > cart_criteria.md

# Update item status to groomed
tickets backlog update SHOPPI-1 --status groomed
```

### Step 2.2: Convert Ready Items to Development Tickets

Convert groomed backlog items into full development tickets:

```bash
# Convert the highest-priority groomed item
tickets backlog convert SHOPPI-1 \
  --reporter "Product Manager" \
  --reporter-email "pm@company.com"

# This automatically:
# - Creates ticket SHOPPI-1 -> CART-1
# - Transfers all metadata (priority, story points, epic relationship)
# - Converts acceptance criteria to formal requirements
# - Updates backlog item status to "in-progress"
# - Links backlog item to ticket for traceability

# Convert additional items as sprint capacity allows
tickets backlog convert CART-1  # Session persistence
tickets backlog convert PAYMEN-1  # Payment integration (if capacity allows)

# View epic with newly created tickets
tickets epic show ECOMMERCE-1
```

---

## Phase 3: Enhanced Requirements & User Stories

### Step 3.1: Review Auto-Generated Requirements

View the requirements automatically created from backlog item conversion:

```bash
# View requirements created from backlog conversion
tickets requirements list CART-1

# The backlog conversion automatically created:
# - Requirements from acceptance criteria
# - User story placeholders
# - Expected results framework

# View detailed requirements breakdown
tickets show CART-1
```

### Step 3.2: Enhance with Additional User Stories

Add detailed user stories to supplement the auto-generated requirements:

```bash
# Add edge case user story for mobile users
tickets requirements story CART-1 \
  --persona "mobile user" \
  --goal "manage my cart on small screens" \
  --benefit "I can shop effectively on my phone" \
  --priority medium \
  --points 3 \
  --criteria "Touch-friendly cart controls" \
  --criteria "Swipe to remove items" \
  --criteria "Responsive design for mobile"

# Add accessibility user story
tickets requirements story CART-1 \
  --persona "user with disabilities" \
  --goal "use cart functionality with assistive technology" \
  --benefit "I can shop independently" \
  --priority high \
  --points 2 \
  --criteria "Screen reader compatible" \
  --criteria "Keyboard navigation support" \
  --criteria "High contrast mode support"
```

### Step 3.3: Add Expected Results for Verification

Define measurable outcomes for the converted tickets:

```bash
# Add performance expectations
tickets requirements result CART-1 \
  --description "Cart operations complete within performance targets" \
  --method automated \
  --criteria "Add to cart: < 300ms response time" \
  --criteria "Cart page load: < 2s" \
  --criteria "95% success rate under normal load"

# Add user experience expectations  
tickets requirements result CART-1 \
  --description "Users can successfully manage cart items" \
  --method manual \
  --criteria "100% of test users can add items" \
  --criteria "100% of test users can modify quantities" \
  --criteria "95% find the interface intuitive"
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

### Step 7.2: Review Test Scenarios Status

```bash
# Review current Gherkin scenarios and their status
tickets requirements list CART-1 --format gherkin

# View detailed requirements including test scenarios
tickets show CART-1

# Note: Gherkin scenario status updates are currently managed through:
# 1. CI/CD integration that updates scenario status based on automated test results
# 2. Manual status tracking in your test automation framework
# 3. Journal entries to document test progress
tickets journal CART-1 "All Gherkin scenarios now passing in CI" --type testing

# Document test results in journal for audit trail
tickets journal CART-1 "Performance scenarios: 95% passing, 2 edge cases still failing" \
  --type progress --completion 85
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

# Check overall project health and requirements coverage
tickets status --format detailed

# Generate comprehensive report for release review
tickets report  # Creates HTML report with full requirements analysis

# Review all completed tickets for release notes
tickets list --status closed --format detailed

# Generate release documentation
tickets status --generate-report  # Creates STATUS.md with metrics

# Export ticket data for release notes (if search command exists)
# tickets search "milestone:v1.0" --format json > release_tickets.json
# Otherwise, use:
tickets list --labels "milestone:v1.0" --format json > release_tickets.json
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
# Integrate with CI/CD for automated progress tracking
cat > .github/workflows/update-tickets.yml << 'EOF'
name: Update Ticket Progress
on: [push, pull_request]
jobs:
  update-progress:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install repo-tickets
        run: pip install -e .
      - name: Update ticket progress based on test results
        run: |
          # Run your tests
          npm test -- --json > test-results.json || true
          
          # Extract ticket IDs from commit messages or branch names
          TICKET_ID=$(git log -1 --pretty=%B | grep -o '[A-Z]\+-[0-9]\+' | head -1)
          
          if [ ! -z "$TICKET_ID" ]; then
            # Log CI results in ticket journal
            if grep -q '"failures": 0' test-results.json; then
              tickets journal $TICKET_ID "CI: All tests passing" --type testing
            else
              tickets journal $TICKET_ID "CI: Some tests failing, check results" --type testing
            fi
          fi
EOF

# Alternative: Manual progress updates after CI runs
# Check test results and update tickets manually:
tickets journal CART-1 "CI build #123: All integration tests passing" --type testing
tickets journal CART-1 "Performance tests: 95% scenarios passing" --type progress
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