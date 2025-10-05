# Epics and Backlog Management

Repo-tickets provides comprehensive support for epic-level planning and product backlog management, enabling professional Agile/Scrum workflows with full traceability from high-level business goals to individual development tasks.

## Table of Contents

1. [Overview](#overview)
2. [Epic Management](#epic-management)
3. [Backlog Management](#backlog-management)
4. [Epic-Ticket Relationships](#epic-ticket-relationships)
5. [Sprint Planning](#sprint-planning)
6. [Prioritization and Scoring](#prioritization-and-scoring)
7. [CLI Commands Reference](#cli-commands-reference)
8. [Best Practices](#best-practices)
9. [Integration Examples](#integration-examples)

## Overview

### What are Epics?

Epics are large bodies of work that can be broken down into smaller, manageable pieces (tickets/user stories). They represent significant features, initiatives, or business goals that typically span multiple sprints.

**Epic Lifecycle:**
- **Draft** → **Active** → **Completed** / **Cancelled**

### What is the Backlog?

The product backlog is a prioritized list of features, enhancements, bug fixes, and technical work. Items in the backlog are estimated, prioritized, and can be assigned to sprints for development.

**Backlog Item Lifecycle:**
- **New** → **Groomed** → **Ready** → **In Progress** → **Done** / **Cancelled**

## Epic Management

### Creating Epics

Create an epic to represent a major feature or initiative:

```bash
# Basic epic creation
tickets epic create "User Authentication System" \
  --description "Complete user management with registration, login, and profiles" \
  --priority high \
  --target-version "v1.0" \
  --estimated-points 50

# Epic with full metadata
tickets epic create "E-commerce Platform" \
  --description "Build complete online shopping experience" \
  --priority critical \
  --owner "Product Team" \
  --owner-email "product@company.com" \
  --labels "e-commerce,revenue" \
  --target-version "v2.0" \
  --target-date "2024-12-31" \
  --estimated-points 200
```

### Managing Epics

```bash
# List all epics
tickets epic list

# List only active epics
tickets epic list --status active

# Show detailed epic information
tickets epic show USER-1

# Update epic details
tickets epic update USER-1 \
  --status active \
  --target-date "2024-06-30" \
  --priority critical

# Add tickets to epic
tickets epic add-ticket USER-1 AUTH-1
tickets epic add-ticket USER-1 PROFILE-1

# Remove tickets from epic
tickets epic remove-ticket USER-1 OLD-TICKET-1
```

### Epic Properties

Epics support comprehensive metadata:

- **Basic Info:** Title, description, status, priority
- **Ownership:** Owner, owner email, labels
- **Planning:** Target version, start date, target date
- **Estimation:** Estimated story points
- **Goals:** High-level objectives
- **Success Criteria:** Measurable outcomes
- **Tickets:** Associated development tasks

## Backlog Management

### Adding Items to Backlog

```bash
# Add a user story to backlog
tickets backlog add "User Registration Feature" \
  --description "Allow users to create accounts with email verification" \
  --type feature \
  --priority high \
  --story-points 8 \
  --business-value 90 \
  --epic-id USER-1

# Add a bug fix
tickets backlog add "Fix login timeout issue" \
  --type bug \
  --priority critical \
  --story-points 3 \
  --business-value 95 \
  --effort-estimate 6 \
  --risk-level low

# Add a technical task
tickets backlog add "Database migration for user profiles" \
  --type task \
  --priority medium \
  --story-points 5 \
  --business-value 40 \
  --effort-estimate 12 \
  --risk-level medium \
  --component "Database" \
  --theme "Technical Debt"
```

### Managing Backlog Items

```bash
# List all backlog items (prioritized)
tickets backlog list

# Filter by status
tickets backlog list --status ready

# Filter by epic
tickets backlog list --epic USER-1

# Filter by sprint
tickets backlog list --sprint SPRINT-1
```

### Backlog Item Properties

Backlog items include extensive sprint planning metadata:

- **Basic:** Title, description, type, priority, status
- **Estimation:** Story points, business value, effort estimate
- **Planning:** Risk level, component, theme, labels
- **Ownership:** Product owner, assigned developer
- **Sprint:** Sprint ID, sprint name
- **Quality:** Acceptance criteria, definition of done
- **Relationships:** Epic association, dependencies

## Epic-Ticket Relationships

### Automatic Relationship Management

When you add a ticket to an epic, repo-tickets maintains bidirectional relationships:

```bash
# Add ticket to epic
tickets epic add-ticket ECOM-1 CART-1
# This updates both:
# - Epic ECOM-1 includes CART-1 in its ticket_ids
# - Ticket CART-1 sets epic_id to ECOM-1

# Remove ticket from epic
tickets epic remove-ticket ECOM-1 CART-1
# This clears both sides of the relationship
```

### Viewing Relationships

```bash
# View epic with all associated tickets
tickets epic show ECOM-1

# View ticket with epic information
tickets show CART-1
```

### Hierarchical Tickets

Tickets can also have parent-child relationships:

```bash
# Create parent ticket
tickets create "User Authentication Epic" --description "Parent epic ticket"

# Create child tickets and link them
tickets create "Login Form" --description "Login UI components"
tickets create "Password Validation" --description "Password strength validation"

# The relationship is maintained in ticket.parent_ticket_id and ticket.child_ticket_ids
```

## Sprint Planning

### Backlog Grooming

Prepare backlog items for sprint planning:

```bash
# Add acceptance criteria to backlog item
tickets backlog show LOGIN-1
# Edit the item to add acceptance criteria and definition of done

# Update item status to groomed
tickets backlog update LOGIN-1 --status groomed

# Check if item is ready for sprint
# Items are sprint-ready when they have:
# - Status: groomed or ready
# - Story points assigned
# - Acceptance criteria defined
```

### Sprint Assignment

```bash
# Assign items to sprint (conceptually - full sprint management in future release)
tickets backlog update LOGIN-1 \
  --status in-progress \
  --sprint-id SPRINT-2024-1 \
  --sprint-name "Q1 Authentication Sprint"
```

### Converting Backlog Items to Tickets

When ready for development, convert backlog items to full tickets:

```bash
# This creates a ticket and links it to the backlog item
# Acceptance criteria become requirements
# Backlog item status updates to "in-progress"
tickets backlog convert LOGIN-1 \
  --reporter "Product Manager" \
  --reporter-email "pm@company.com"
```

## Prioritization and Scoring

### Automatic Priority Scoring

Backlog items are automatically prioritized using a scoring algorithm:

**Priority Score = (Base Priority × 100) + Business Value - (Story Points × 2)**

Where:
- **Base Priority:** critical=4, high=3, medium=2, low=1
- **Business Value:** 1-100 scale
- **Story Points:** Fibonacci-style effort estimate

### Examples

```bash
# High business value, low effort = High priority score
tickets backlog add "Quick Analytics Fix" \
  --priority high \
  --business-value 90 \
  --story-points 2
# Score: (3 × 100) + 90 - (2 × 2) = 386

# Medium business value, high effort = Lower priority score  
tickets backlog add "Complex Reporting System" \
  --priority medium \
  --business-value 70 \
  --story-points 13
# Score: (2 × 100) + 70 - (13 × 2) = 244
```

### Custom Prioritization

You can override automatic prioritization by manually setting priority and adjusting business value scores based on:

- **Strategic importance**
- **Customer impact**
- **Technical dependencies**
- **Risk mitigation**
- **Deadline constraints**

## CLI Commands Reference

### Epic Commands

```bash
tickets epic create TITLE [OPTIONS]       # Create new epic
tickets epic list [OPTIONS]               # List epics
tickets epic show EPIC_ID                 # Show epic details  
tickets epic update EPIC_ID [OPTIONS]     # Update epic
tickets epic add-ticket EPIC_ID TICKET_ID # Add ticket to epic
tickets epic remove-ticket EPIC_ID TICKET_ID # Remove ticket from epic
```

### Backlog Commands

```bash
tickets backlog add TITLE [OPTIONS]       # Add item to backlog
tickets backlog list [OPTIONS]            # List backlog items
tickets backlog show ITEM_ID              # Show item details
tickets backlog update ITEM_ID [OPTIONS]  # Update item
tickets backlog convert ITEM_ID [OPTIONS] # Convert to ticket
```

### Options Reference

**Epic Creation Options:**
- `--description, -d` - Epic description
- `--priority` - Priority (critical, high, medium, low)
- `--owner` - Epic owner name
- `--owner-email` - Epic owner email
- `--labels, -l` - Epic labels (multiple)
- `--target-version` - Target version
- `--target-date` - Target date (YYYY-MM-DD)
- `--estimated-points` - Estimated story points

**Backlog Item Options:**
- `--description, -d` - Item description
- `--type` - Item type (story, feature, bug, epic, task, spike)
- `--priority` - Priority (critical, high, medium, low)
- `--story-points` - Story points estimate
- `--business-value` - Business value (1-100)
- `--effort-estimate` - Effort in hours
- `--risk-level` - Risk level (low, medium, high)
- `--epic-id` - Associate with epic
- `--component` - System component
- `--theme` - Business theme
- `--labels, -l` - Labels (multiple)

## Best Practices

### Epic Management

1. **Keep Epics Focused**
   - One business goal per epic
   - 3-6 month timeframe maximum
   - Clear success criteria

2. **Regular Epic Grooming**
   - Review progress weekly
   - Update target dates as needed
   - Break down into smaller epics if too large

3. **Epic Documentation**
   - Include business context and user value
   - Define success criteria measurably
   - List key assumptions and dependencies

### Backlog Management

1. **INVEST Principle for Items**
   - **I**ndependent - Can be developed independently
   - **N**egotiable - Details can be refined
   - **V**aluable - Delivers user/business value
   - **E**stimable - Can be estimated reasonably
   - **S**mall - Completable in one sprint
   - **T**estable - Clear acceptance criteria

2. **Continuous Grooming**
   - Refine top 2-3 sprints worth of items
   - Keep acceptance criteria current
   - Re-estimate as understanding improves

3. **Balanced Prioritization**
   - Mix of features, bugs, and technical debt
   - Consider dependencies and risks
   - Balance short-term wins with long-term goals

### Sprint Planning

1. **Definition of Ready**
   - Story points assigned
   - Acceptance criteria defined
   - Dependencies identified
   - Design/architecture approved

2. **Definition of Done**
   - Code complete and tested
   - Acceptance criteria met
   - Documentation updated
   - Peer reviewed

## Integration Examples

### Complete Feature Development Flow

```bash
# 1. Create epic for major feature
tickets epic create "Mobile App Authentication" \
  --description "Complete mobile authentication system" \
  --priority high \
  --target-version "v1.2" \
  --estimated-points 40

# 2. Add detailed backlog items
tickets backlog add "Mobile Login Screen" \
  --type feature \
  --priority high \
  --story-points 5 \
  --business-value 85 \
  --epic-id MOBILE-1

tickets backlog add "Biometric Authentication" \
  --type feature \
  --priority medium \
  --story-points 8 \
  --business-value 75 \
  --epic-id MOBILE-1

tickets backlog add "Session Management" \
  --type feature \
  --priority high \
  --story-points 3 \
  --business-value 90 \
  --epic-id MOBILE-1

# 3. Groom and prioritize backlog
tickets backlog list --epic MOBILE-1

# 4. Convert ready items to tickets
tickets backlog convert LOGIN-1 \
  --reporter "Product Manager" \
  --reporter-email "pm@company.com"

# 5. Track progress
tickets epic show MOBILE-1
tickets show LOGIN-1
```

### Release Planning

```bash
# List all epics for release planning
tickets epic list --format table

# Show epic progress
tickets epic show MOBILE-1

# Check backlog health
tickets backlog list --status ready

# Generate comprehensive report
tickets report
```

### Team Coordination

```bash
# Product Owner: Manage backlog
tickets backlog add "User Profile Pictures" \
  --business-value 60 \
  --story-points 5 \
  --epic-id USER-1

# Scrum Master: Review sprint readiness  
tickets backlog list --status groomed

# Developer: Convert and work on items
tickets backlog convert PROFILE-1
tickets update PROFILE-1 --status in-progress --assignee "developer"

# Team: Track epic progress
tickets epic show USER-1
```

This comprehensive epic and backlog management system transforms repo-tickets into a professional project management platform suitable for teams of any size, from small startups to enterprise development organizations.