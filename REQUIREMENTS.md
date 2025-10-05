# Requirements Management in Repo-Tickets

This document provides comprehensive guidance on using the powerful requirements management and acceptance testing features in repo-tickets.

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [User Stories](#user-stories)
4. [Expected Results](#expected-results)
5. [Gherkin Acceptance Tests](#gherkin-acceptance-tests)
6. [CLI Commands](#cli-commands)
7. [Examples](#examples)
8. [Best Practices](#best-practices)
9. [Integration with Reports](#integration-with-reports)

## Overview

Repo-tickets provides comprehensive requirements management capabilities that integrate seamlessly with traditional ticket tracking. This system supports:

- **Requirements**: Formal requirements with priorities, statuses, and acceptance criteria
- **User Stories**: Agile user stories with personas, goals, and benefits
- **Expected Results**: Verification-focused outcomes with success criteria
- **Gherkin Scenarios**: BDD-style acceptance tests using Given-When-Then format

All requirements are tracked at the ticket level and provide powerful analytics through reports and status commands.

## Requirements

Requirements are formal specifications that define what needs to be accomplished. Each requirement has:

### Properties
- **ID**: Unique identifier within the ticket
- **Title**: Brief description of the requirement
- **Description**: Detailed explanation (optional)
- **Priority**: critical, high, medium, low
- **Status**: draft, approved, implemented, verified
- **Acceptance Criteria**: List of specific conditions that must be met
- **Author**: Person who created the requirement
- **Timestamps**: Creation and update times

### Workflow
1. **Draft**: Initial requirement creation
2. **Approved**: Requirement reviewed and accepted
3. **Implemented**: Development work completed
4. **Verified**: Testing confirmed requirement is met

## User Stories

User stories follow the standard Agile format and focus on user value:

### Format
```
As a [persona], I want [goal], so that [benefit].
```

### Properties
- **ID**: Unique identifier
- **Persona**: The user type or role
- **Goal**: What the user wants to achieve
- **Benefit**: Why this is valuable
- **Priority**: critical, high, medium, low
- **Story Points**: Estimation points (optional)
- **Acceptance Criteria**: Specific conditions for completion

### Example
```
As a developer, I want to track time spent on tickets, so that I can provide accurate project estimates.
```

## Expected Results

Expected results define specific, verifiable outcomes:

### Properties
- **ID**: Unique identifier
- **Description**: What should happen
- **Success Criteria**: Measurable conditions for success
- **Verification Method**: manual, automated, review
- **Status**: pending, verified, failed, blocked
- **Verifier Information**: Who verified and when

### Verification Methods
- **Manual**: Human testing and validation
- **Automated**: Automated test execution
- **Review**: Code or design review process

## Gherkin Acceptance Tests

Gherkin scenarios use the Behavior-Driven Development (BDD) format:

### Structure
```gherkin
@tag1 @tag2
Scenario: Login with valid credentials
  Given I am on the login page
  And I have valid user credentials
  When I enter my username and password
  And I click the login button
  Then I should be redirected to the dashboard
  And I should see a welcome message
```

### Components
- **Tags**: Categorization and filtering (@smoke, @regression, etc.)
- **Scenario Title**: Descriptive name for the test
- **Background**: Common setup steps (optional)
- **Given**: Pre-conditions and setup
- **When**: Actions performed
- **Then**: Expected outcomes
- **And/But**: Additional steps of the same type

### Status Values
- **draft**: Scenario written but not ready
- **ready**: Scenario ready for implementation
- **passing**: Tests are passing
- **failing**: Tests are failing
- **blocked**: Cannot execute due to dependencies

## CLI Commands

### Adding Requirements

```bash
# Add a basic requirement
tickets requirements add TICKET-1 --title "User authentication" --priority high

# Add requirement with acceptance criteria
tickets requirements add TICKET-1 \
  --title "Password validation" \
  --description "Implement secure password validation" \
  --priority medium \
  --criteria "Minimum 8 characters" \
  --criteria "Must contain uppercase and lowercase" \
  --criteria "Must contain at least one number"
```

### Adding User Stories

```bash
# Add a user story
tickets requirements story TICKET-1 \
  --persona "project manager" \
  --goal "view team velocity metrics" \
  --benefit "I can plan sprints more effectively" \
  --priority high \
  --points 5

# With acceptance criteria
tickets requirements story TICKET-1 \
  --persona "developer" \
  --goal "track time on tickets" \
  --benefit "I can provide accurate estimates" \
  --criteria "Timer can be started and stopped" \
  --criteria "Time is recorded in minutes" \
  --criteria "Historical time logs are viewable"
```

### Adding Expected Results

```bash
# Add expected result
tickets requirements result TICKET-1 \
  --description "Login page loads within 2 seconds" \
  --method automated \
  --criteria "Response time < 2000ms" \
  --criteria "All page elements visible"
```

### Adding Gherkin Scenarios

```bash
# Add from command line
tickets requirements gherkin TICKET-1 \
  --title "Successful login" \
  --given "I am on the login page" \
  --given "I have valid credentials" \
  --when "I enter username and password" \
  --when "I click login button" \
  --then "I should see the dashboard" \
  --tags smoke --tags authentication

# Load from file
tickets requirements gherkin TICKET-1 --file scenarios/login.feature
```

### Viewing Requirements

```bash
# Summary view
tickets requirements list TICKET-1

# Detailed view
tickets requirements list TICKET-1 --format detailed

# Gherkin scenarios only
tickets requirements list TICKET-1 --format gherkin
```

### Verification

```bash
# Mark expected result as verified
tickets requirements verify TICKET-1 RESULT-123 \
  --notes "Confirmed via performance testing"
```

## Examples

### Complete Feature Development

```bash
# Create ticket
tickets create "User login system" \
  --description "Implement secure user authentication" \
  --priority high

# Add user stories
tickets requirements story LOGIN-1 \
  --persona "end user" \
  --goal "log into the application securely" \
  --benefit "I can access my personal data" \
  --points 8

tickets requirements story LOGIN-1 \
  --persona "administrator" \
  --goal "manage user access permissions" \
  --benefit "I can control system security" \
  --points 5

# Add requirements
tickets requirements add LOGIN-1 \
  --title "Password encryption" \
  --description "All passwords must be encrypted using bcrypt" \
  --priority critical \
  --criteria "Bcrypt with salt rounds >= 12" \
  --criteria "Plain text passwords never stored"

tickets requirements add LOGIN-1 \
  --title "Session management" \
  --priority high \
  --criteria "Session timeout after 30 minutes" \
  --criteria "Secure session cookies only"

# Add expected results
tickets requirements result LOGIN-1 \
  --description "Login form validates input" \
  --method manual \
  --criteria "Empty fields show error messages" \
  --criteria "Invalid email format rejected"

tickets requirements result LOGIN-1 \
  --description "Authentication API performance" \
  --method automated \
  --criteria "Login endpoint responds < 500ms" \
  --criteria "Rate limiting prevents brute force"

# Add Gherkin scenarios
tickets requirements gherkin LOGIN-1 \
  --title "Valid login credentials" \
  --given "I am on the login page" \
  --given "I have a valid user account" \
  --when "I enter correct email and password" \
  --when "I click the login button" \
  --then "I should be logged in" \
  --then "I should see the dashboard" \
  --tags authentication --tags smoke

tickets requirements gherkin LOGIN-1 \
  --title "Invalid login credentials" \
  --given "I am on the login page" \
  --when "I enter invalid credentials" \
  --when "I click the login button" \
  --then "I should see an error message" \
  --then "I should remain on the login page" \
  --tags authentication --tags negative
```

### API Feature Example

```gherkin
@api @integration
Scenario: Create new user via API
  Given the API is running
  And I have admin authentication
  When I POST to /api/users with valid user data
  Then the response status should be 201
  And the response should contain the user ID
  And the user should exist in the database

@api @validation
Scenario: API rejects invalid user data
  Given the API is running
  And I have admin authentication
  When I POST to /api/users with invalid email format
  Then the response status should be 400
  And the response should contain validation errors
```

## Best Practices

### Requirements Writing

1. **Be Specific**: Use measurable, testable language
2. **Single Responsibility**: One requirement per ID
3. **Traceability**: Link to business objectives
4. **Prioritization**: Use priority levels consistently

```bash
# Good: Specific and measurable
tickets requirements add TICKET-1 \
  --title "API response time performance" \
  --criteria "95% of requests complete within 200ms"

# Avoid: Vague and unmeasurable
tickets requirements add TICKET-1 \
  --title "API should be fast"
```

### User Stories

1. **User-Centered**: Focus on user value
2. **Independent**: Stories can be developed separately  
3. **Negotiable**: Details can be discussed
4. **Valuable**: Provides business value
5. **Estimable**: Can be estimated for effort
6. **Small**: Fits in a sprint
7. **Testable**: Clear acceptance criteria

### Gherkin Scenarios

1. **Descriptive Titles**: Clear scenario purpose
2. **Consistent Language**: Use domain terminology
3. **Independent**: Scenarios don't depend on each other
4. **Data-Driven**: Use examples for multiple cases
5. **Maintainable**: Keep scenarios focused and simple

```gherkin
# Good: Clear and focused
Scenario: User searches for products by category
  Given I am on the product catalog page
  When I select the "Electronics" category
  Then I should see only electronic products
  And the product count should be displayed

# Avoid: Too complex or multiple concerns
Scenario: Complete user workflow from registration to purchase
  # ... too many steps covering multiple features
```

### Tagging Strategy

Use consistent tags for organization:

```bash
# Functional areas
--tags authentication --tags payment --tags search

# Test types  
--tags smoke --tags regression --tags performance

# Priority/Risk
--tags critical --tags high-risk --tags edge-case

# Environment
--tags api --tags ui --tags mobile --tags integration
```

## Integration with Reports

Requirements are automatically included in:

### HTML Reports
- Requirements dashboard card showing coverage metrics
- Individual ticket sections with full requirement details
- Color-coded badges indicating status and coverage

### Status Command
```bash
# View requirements in status summary
tickets status

# Detailed status including requirements breakdown
tickets status --format detailed

# JSON output for automation
tickets status --format json
```

### README Integration
```bash
# Update README with requirements metrics
tickets status --update-readme
```

This adds a section like:
```markdown
**📋 Requirements & Testing:**
- Requirements: 15 (87.5% coverage)
- User Stories: 8 (34 story points)
- Test Scenarios: 23 (91.3% passing)
- Acceptance Rate: 75.0% (6/8 tickets)
```

## Analytics and Metrics

The system tracks comprehensive metrics:

- **Requirements Coverage**: % of requirements implemented/verified
- **Test Pass Rate**: % of Gherkin scenarios passing
- **Acceptance Rate**: % of tickets meeting acceptance criteria
- **Story Point Velocity**: Completed points over time
- **Verification Methods**: Distribution of manual vs automated testing

These metrics help teams:
- Track progress toward release goals
- Identify testing gaps
- Measure delivery quality
- Plan sprint capacity
- Assess risk levels

## Advanced Usage

### Custom Gherkin Templates

Create reusable scenario templates:

```bash
# Save common scenarios to files
cat > templates/api_crud.feature << EOF
@api @crud
Scenario: Create resource via API
  Given the API is authenticated
  When I POST to {endpoint} with valid data
  Then the response status should be 201
  And the resource should be created
EOF

# Load template and customize
tickets requirements gherkin TICKET-1 --file templates/api_crud.feature
```

### Batch Operations

Process multiple requirements:

```bash
# Load requirements from spreadsheet/CSV
while IFS=, read -r title description priority; do
  tickets requirements add TICKET-1 \
    --title "$title" \
    --description "$description" \
    --priority "$priority"
done < requirements.csv
```

### Integration with CI/CD

```yaml
# .github/workflows/requirements.yml
name: Requirements Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install repo-tickets
        run: pip install repo-tickets
      - name: Validate Gherkin scenarios
        run: tickets requirements list --format gherkin | cucumber --dry-run
      - name: Check coverage
        run: |
          coverage=$(tickets status --format json | jq -r '.requirements_stats.requirements_coverage')
          if (( $(echo "$coverage < 80" | bc -l) )); then
            echo "Requirements coverage ($coverage%) below threshold"
            exit 1
          fi
```

This comprehensive requirements management system transforms repo-tickets from simple issue tracking into a complete project management and quality assurance platform.