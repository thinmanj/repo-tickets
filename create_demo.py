#!/usr/bin/env python3
"""
Create comprehensive demo tickets with all requirements features.
"""

import sys
from pathlib import Path

# Add the repo-tickets package to the path
sys.path.insert(0, str(Path(__file__).parent))

from repo_tickets.models import Ticket
from repo_tickets.storage import TicketStorage

def create_comprehensive_demo():
    """Create demo tickets with all requirements features."""
    print("🚀 Creating comprehensive demo tickets with requirements...")
    
    # Initialize storage
    storage = TicketStorage()
    
    # Create main authentication ticket
    auth_ticket = Ticket(
        id="AUTH-1",
        title="User Authentication System",
        description="Implement comprehensive user authentication with secure login, password management, and session handling",
        priority="high",
        labels=["security", "authentication", "feature"],
        estimated_hours=20.0,
        reporter="julio",
        reporter_email="thinmanj@gmail.com",
        status="in-progress"
    )
    
    # Add formal requirements
    req1 = auth_ticket.add_requirement(
        title="Password Security",
        description="Implement secure password validation and encryption",
        priority="critical",
        acceptance_criteria=[
            "Minimum 8 characters required",
            "Must contain uppercase, lowercase, and numbers",
            "Must use bcrypt encryption with salt rounds >= 12",
            "Password history of 5 previous passwords maintained"
        ],
        author="julio"
    )
    req1.status = "implemented"  # Mark as implemented
    
    req2 = auth_ticket.add_requirement(
        title="Session Management", 
        description="Secure session handling and timeout management",
        priority="high",
        acceptance_criteria=[
            "Session timeout after 30 minutes of inactivity",
            "Secure session cookies with HttpOnly flag",
            "Session invalidation on logout",
            "Concurrent session limit of 3 per user"
        ],
        author="julio"
    )
    req2.status = "approved"
    
    req3 = auth_ticket.add_requirement(
        title="Multi-Factor Authentication",
        description="Optional 2FA support for enhanced security",
        priority="medium",
        acceptance_criteria=[
            "TOTP support via authenticator apps",
            "SMS backup codes",
            "Recovery codes for account access"
        ],
        author="julio"
    )
    
    # Add user stories
    story1 = auth_ticket.add_user_story(
        persona="end user",
        goal="log into the application securely",
        benefit="I can access my personal data safely",
        priority="high",
        story_points=8,
        acceptance_criteria=[
            "Login form validates credentials",
            "Failed attempts are rate limited",
            "Success redirects to user dashboard"
        ],
        author="julio"
    )
    
    story2 = auth_ticket.add_user_story(
        persona="security administrator",
        goal="monitor authentication attempts",
        benefit="I can detect and prevent security threats",
        priority="medium",
        story_points=5,
        acceptance_criteria=[
            "Failed login attempts are logged",
            "Suspicious activity alerts generated",
            "Account lockout after 5 failed attempts"
        ],
        author="julio"
    )
    
    story3 = auth_ticket.add_user_story(
        persona="developer",
        goal="integrate with external auth providers",
        benefit="Users can use existing accounts (OAuth)",
        priority="low",
        story_points=13,
        acceptance_criteria=[
            "Google OAuth integration",
            "GitHub OAuth integration",
            "Account linking functionality"
        ],
        author="julio"
    )
    
    # Add expected results
    result1 = auth_ticket.add_expected_result(
        description="Login form loads within 2 seconds",
        success_criteria=[
            "Page load time < 2000ms for 95% of requests",
            "All form elements are interactive",
            "No console errors during load"
        ],
        verification_method="automated"
    )
    result1.mark_verified("julio", "Performance tests passed - average 1.2s load time")
    
    result2 = auth_ticket.add_expected_result(
        description="Authentication API responds within 500ms",
        success_criteria=[
            "Login endpoint responds < 500ms",
            "Password validation completes < 200ms",
            "Session creation time < 100ms"
        ],
        verification_method="automated"
    )
    
    result3 = auth_ticket.add_expected_result(
        description="Security audit compliance",
        success_criteria=[
            "OWASP Top 10 vulnerabilities addressed",
            "Penetration testing passed",
            "Security code review completed"
        ],
        verification_method="manual"
    )
    
    # Add Gherkin scenarios
    scenario1 = auth_ticket.add_gherkin_scenario(
        title="Valid user login",
        given=[
            "I am on the login page",
            "I have a valid user account with username 'testuser' and password 'SecurePass123!'"
        ],
        when=[
            "I enter 'testuser' in the username field",
            "I enter 'SecurePass123!' in the password field", 
            "I click the 'Login' button"
        ],
        then=[
            "I should be redirected to the dashboard",
            "I should see a welcome message with my name",
            "I should see the logout option in the navigation"
        ],
        tags=["authentication", "smoke", "happy-path"],
        author="julio"
    )
    scenario1.status = "passing"
    
    scenario2 = auth_ticket.add_gherkin_scenario(
        title="Invalid credentials rejection",
        given=[
            "I am on the login page"
        ],
        when=[
            "I enter 'testuser' in the username field",
            "I enter 'wrongpassword' in the password field",
            "I click the 'Login' button"
        ],
        then=[
            "I should remain on the login page",
            "I should see an error message 'Invalid username or password'",
            "The password field should be cleared",
            "The login attempt should be logged"
        ],
        tags=["authentication", "negative", "security"],
        author="julio"
    )
    scenario2.status = "passing"
    
    scenario3 = auth_ticket.add_gherkin_scenario(
        title="Account lockout after multiple failures",
        given=[
            "I am on the login page",
            "I have already made 4 failed login attempts with username 'testuser'"
        ],
        when=[
            "I enter 'testuser' in the username field",
            "I enter 'wrongpassword' in the password field",
            "I click the 'Login' button"
        ],
        then=[
            "I should see an error message 'Account temporarily locked due to too many failed attempts'",
            "The login form should be disabled for 15 minutes",
            "An admin notification should be sent",
            "The account status should be updated to 'locked'"
        ],
        tags=["authentication", "security", "rate-limiting"],
        author="julio"
    )
    scenario3.status = "ready"
    
    scenario4 = auth_ticket.add_gherkin_scenario(
        title="Session timeout handling",
        given=[
            "I am logged into the application",
            "I have been inactive for 29 minutes"
        ],
        when=[
            "I wait for 1 more minute",
            "I try to access a protected page"
        ],
        then=[
            "I should be redirected to the login page",
            "I should see a message 'Session expired, please log in again'",
            "My session should be invalidated on the server",
            "Any unsaved work should trigger a warning"
        ],
        tags=["authentication", "session", "timeout"],
        author="julio"
    )
    scenario4.status = "failing"  # Currently failing
    
    # Update acceptance criteria status
    auth_ticket.update_acceptance_criteria_status()
    
    # Save the ticket
    storage.save_ticket(auth_ticket)
    print(f"✅ Created comprehensive ticket {auth_ticket.id}")
    
    # Create a second ticket for API development
    api_ticket = Ticket(
        id="API-1",
        title="REST API Development",
        description="Develop RESTful API endpoints for user management",
        priority="medium",
        labels=["api", "backend", "development"],
        estimated_hours=15.0,
        reporter="julio",
        reporter_email="thinmanj@gmail.com",
        status="open"
    )
    
    # Add requirements to API ticket
    api_req = api_ticket.add_requirement(
        title="API Versioning",
        description="Implement proper API versioning strategy",
        priority="high",
        acceptance_criteria=[
            "Version in URL path (/api/v1/)",
            "Backward compatibility for one major version",
            "Deprecation notices for old endpoints"
        ],
        author="julio"
    )
    
    # Add API user story
    api_story = api_ticket.add_user_story(
        persona="mobile app developer",
        goal="access user data via REST API",
        benefit="I can build mobile applications that integrate with the system",
        priority="high",
        story_points=8,
        acceptance_criteria=[
            "RESTful endpoints follow standard conventions",
            "JSON responses with proper status codes",
            "Comprehensive API documentation"
        ],
        author="julio"
    )
    
    # Add API Gherkin scenarios
    api_scenario = api_ticket.add_gherkin_scenario(
        title="Create new user via API",
        given=[
            "I have admin API credentials",
            "The API is running and accessible"
        ],
        when=[
            "I POST to /api/v1/users with valid user data",
            "The request includes proper authentication headers"
        ],
        then=[
            "The response status should be 201 Created",
            "The response should contain the new user ID",
            "The user should exist in the database",
            "The response should include the user's profile URL"
        ],
        tags=["api", "crud", "user-management"],
        author="julio"
    )
    
    storage.save_ticket(api_ticket)
    print(f"✅ Created API ticket {api_ticket.id}")
    
    # Create a bug ticket
    bug_ticket = Ticket(
        id="BUG-1",
        title="Login Form Validation Issues",
        description="Email validation allows invalid formats",
        priority="critical",
        labels=["bug", "urgent", "validation"],
        reporter="julio", 
        reporter_email="thinmanj@gmail.com",
        status="closed"
    )
    
    # Add bug reproduction scenarios
    bug_scenario = bug_ticket.add_gherkin_scenario(
        title="Invalid email format accepted",
        given=[
            "I am on the registration page"
        ],
        when=[
            "I enter 'notanemail' in the email field",
            "I click submit"
        ],
        then=[
            "I should see a validation error",
            "The form should not be submitted",
            "The email field should be highlighted in red"
        ],
        tags=["bug", "validation", "email"],
        author="julio"
    )
    bug_scenario.status = "passing"  # Bug is fixed
    
    storage.save_ticket(bug_ticket)
    print(f"✅ Created bug ticket {bug_ticket.id}")
    
    print("\n🎯 Demo tickets created successfully!")
    print("   • AUTH-1: Comprehensive authentication system with full requirements")
    print("   • API-1: REST API development with user stories")
    print("   • BUG-1: Bug ticket with reproduction scenarios")
    print("\n📊 Summary:")
    
    # Print summary of all features
    all_tickets = storage.list_tickets()
    total_requirements = sum(len(t.requirements) for t in all_tickets)
    total_stories = sum(len(t.user_stories) for t in all_tickets)
    total_results = sum(len(t.expected_results) for t in all_tickets) 
    total_scenarios = sum(len(t.gherkin_scenarios) for t in all_tickets)
    total_points = sum(t.total_story_points for t in all_tickets)
    
    print(f"   • {len(all_tickets)} tickets created")
    print(f"   • {total_requirements} formal requirements")
    print(f"   • {total_stories} user stories ({total_points} story points)")
    print(f"   • {total_results} expected results") 
    print(f"   • {total_scenarios} Gherkin scenarios")
    
    return all_tickets

if __name__ == "__main__":
    create_comprehensive_demo()