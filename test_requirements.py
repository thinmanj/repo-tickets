#!/usr/bin/env python3
"""
Test script for requirements management features in repo-tickets.

This script validates all the new requirement tracking functionality including:
- Requirements with acceptance criteria
- User stories with story points
- Expected results with verification
- Gherkin scenarios with Given-When-Then
- Requirements analytics and reporting
"""

import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the repo-tickets package to the path
sys.path.insert(0, str(Path(__file__).parent))

from repo_tickets.models import (
    Ticket, Requirement, UserStory, ExpectedResult, GherkinScenario
)
from repo_tickets.storage import TicketStorage

def test_requirements_model():
    """Test the Requirement model functionality."""
    print("🔍 Testing Requirements model...")
    
    # Create a basic requirement
    req = Requirement(
        id="REQ-001",
        title="User Authentication",
        description="Implement secure user authentication system",
        priority="high",
        acceptance_criteria=["Must use bcrypt", "Session timeout 30 min"],
        author="julio"
    )
    
    assert req.title == "User Authentication"
    assert req.priority == "high"
    assert req.status == "draft"  # Default status
    assert len(req.acceptance_criteria) == 2
    
    print("  ✅ Basic requirement creation works")
    
    # Test status transitions
    req.status = "approved"
    assert req.status == "approved"
    
    req.status = "implemented"
    assert req.status == "implemented"
    
    req.status = "verified"
    assert req.status == "verified"
    
    print("  ✅ Status transitions work")
    
    # Test validation
    try:
        invalid_req = Requirement(
            id="REQ-002",
            title="",  # Empty title should fail
            priority="high"
        )
        assert False, "Should have failed validation"
    except ValueError as e:
        print(f"  ✅ Validation works: {e}")

def test_user_stories_model():
    """Test the UserStory model functionality."""
    print("🔍 Testing User Stories model...")
    
    story = UserStory(
        id="STORY-001",
        persona="developer",
        goal="track time on tickets",
        benefit="I can provide accurate estimates",
        priority="medium",
        story_points=5,
        acceptance_criteria=["Timer can be started/stopped", "Time is recorded accurately"],
        author="julio"
    )
    
    assert story.persona == "developer"
    assert story.goal == "track time on tickets"
    assert story.benefit == "I can provide accurate estimates"
    assert story.story_points == 5
    
    # Test formatted story
    expected_format = "As a developer, I want track time on tickets, so that I can provide accurate estimates."
    assert story.formatted_story == expected_format
    
    print("  ✅ User story creation and formatting works")

def test_expected_results_model():
    """Test the ExpectedResult model functionality."""
    print("🔍 Testing Expected Results model...")
    
    result = ExpectedResult(
        id="RESULT-001",
        description="Login page loads within 2 seconds",
        success_criteria=["Response time < 2000ms", "All elements visible"],
        verification_method="automated"
    )
    
    assert result.description == "Login page loads within 2 seconds"
    assert result.verification_method == "automated"
    assert result.status == "pending"  # Default status
    assert len(result.success_criteria) == 2
    
    # Test verification
    result.mark_verified("test-verifier", "Performance tests passed")
    assert result.status == "verified"
    assert result.verified_by == "test-verifier"
    assert result.notes == "Performance tests passed"
    assert result.verified_at is not None
    
    print("  ✅ Expected results creation and verification works")

def test_gherkin_scenarios_model():
    """Test the GherkinScenario model functionality."""
    print("🔍 Testing Gherkin Scenarios model...")
    
    scenario = GherkinScenario(
        id="SCENARIO-001",
        title="Successful user login",
        given=["I am on the login page", "I have valid credentials"],
        when=["I enter username and password", "I click login button"],
        then=["I should be logged in", "I should see the dashboard"],
        tags=["authentication", "smoke"],
        author="julio"
    )
    
    assert scenario.title == "Successful user login"
    assert len(scenario.given) == 2
    assert len(scenario.when) == 2
    assert len(scenario.then) == 2
    assert "authentication" in scenario.tags
    
    # Test Gherkin text generation
    gherkin_text = scenario.to_gherkin_text()
    assert "Scenario: Successful user login" in gherkin_text
    assert "Given I am on the login page" in gherkin_text
    assert "And I have valid credentials" in gherkin_text
    assert "When I enter username and password" in gherkin_text
    assert "Then I should be logged in" in gherkin_text
    assert "@authentication @smoke" in gherkin_text
    
    print("  ✅ Gherkin scenario creation and text generation works")
    
    # Test parsing from text
    gherkin_input = """@api @integration
Scenario: Create new user via API
  Given the API is running
  And I have admin authentication  
  When I POST to /api/users with valid data
  Then the response status should be 201
  And the user should exist in the database"""
    
    parsed_scenario = GherkinScenario.from_gherkin_text(gherkin_input, author="parser-test")
    assert parsed_scenario.title == "Create new user via API"
    assert "api" in parsed_scenario.tags
    assert "integration" in parsed_scenario.tags
    assert len(parsed_scenario.given) == 2
    assert len(parsed_scenario.when) == 1
    assert len(parsed_scenario.then) == 2
    
    print("  ✅ Gherkin text parsing works")

def test_ticket_requirements_integration():
    """Test requirements integration with tickets."""
    print("🔍 Testing Ticket-Requirements integration...")
    
    # Create a ticket
    ticket = Ticket(
        id="TEST-001",
        title="User Authentication Feature",
        description="Implement comprehensive user authentication",
        reporter="julio",
        reporter_email="thinmanj@gmail.com"
    )
    
    # Add requirements
    req1 = ticket.add_requirement(
        title="Password Security",
        description="Implement secure password handling",
        priority="critical",
        acceptance_criteria=["Bcrypt encryption", "Minimum 8 characters"],
        author="julio"
    )
    
    req2 = ticket.add_requirement(
        title="Session Management", 
        priority="high",
        author="julio"
    )
    
    assert len(ticket.requirements) == 2
    assert ticket.requirements_count == 2
    
    print("  ✅ Adding requirements to tickets works")
    
    # Add user stories
    story1 = ticket.add_user_story(
        persona="end user",
        goal="log in securely",
        benefit="I can access my account safely",
        priority="high",
        story_points=8,
        author="julio"
    )
    
    story2 = ticket.add_user_story(
        persona="admin",
        goal="manage user sessions",
        benefit="I can maintain security",
        story_points=3,
        author="julio"
    )
    
    assert len(ticket.user_stories) == 2
    assert ticket.total_story_points == 11
    
    print("  ✅ Adding user stories to tickets works")
    
    # Add expected results
    result1 = ticket.add_expected_result(
        description="Login form validates input",
        success_criteria=["Empty fields show errors", "Invalid email rejected"],
        verification_method="manual"
    )
    
    result2 = ticket.add_expected_result(
        description="Authentication API performance",
        success_criteria=["Response time < 500ms"],
        verification_method="automated"
    )
    
    assert len(ticket.expected_results) == 2
    
    print("  ✅ Adding expected results to tickets works")
    
    # Add Gherkin scenarios
    scenario1 = ticket.add_gherkin_scenario(
        title="Valid login attempt",
        given=["I am on login page"],
        when=["I enter valid credentials"],
        then=["I should be logged in"],
        tags=["authentication", "happy-path"],
        author="julio"
    )
    
    gherkin_text = """@authentication @negative
Scenario: Invalid login attempt
  Given I am on the login page
  When I enter invalid credentials
  Then I should see an error message"""
    
    scenario2 = ticket.add_gherkin_from_text(gherkin_text, author="julio")
    
    assert len(ticket.gherkin_scenarios) == 2
    assert ticket.gherkin_scenarios_count == 2
    
    print("  ✅ Adding Gherkin scenarios to tickets works")
    
    # Test requirements summary
    summary = ticket.get_requirements_summary()
    assert summary['requirements_count'] == 2
    assert summary['user_stories_count'] == 2
    assert summary['total_story_points'] == 11
    assert summary['expected_results_count'] == 2
    assert summary['gherkin_scenarios_count'] == 2
    
    print("  ✅ Requirements summary generation works")
    
    # Test coverage calculation (no requirements are implemented/verified yet)
    assert summary['requirements_coverage'] == 0.0  # No requirements verified yet
    assert summary['test_pass_rate'] == 0.0  # No tests passing yet
    
    # Mark some requirements as implemented/verified
    ticket.requirements[0].status = "implemented"
    ticket.requirements[1].status = "verified"
    
    # Mark some scenarios as passing
    ticket.gherkin_scenarios[0].status = "passing"
    
    # Verify an expected result
    ticket.expected_results[0].mark_verified("test-verifier")
    
    # Update acceptance criteria status
    ticket.update_acceptance_criteria_status()
    
    # Check updated metrics
    updated_summary = ticket.get_requirements_summary()
    assert updated_summary['requirements_coverage'] == 100.0  # Both requirements now covered
    assert updated_summary['test_pass_rate'] == 50.0  # 1 of 2 scenarios passing
    assert updated_summary['verification_rate'] == 50.0  # 1 of 2 results verified
    
    print("  ✅ Requirements metrics calculation works")

def test_ticket_serialization_with_requirements():
    """Test that tickets with requirements serialize/deserialize correctly."""
    print("🔍 Testing Requirements serialization...")
    
    # Create ticket with all requirement types
    original_ticket = Ticket(
        id="SERIAL-001",
        title="Serialization Test",
        reporter="julio",
        reporter_email="thinmanj@gmail.com"
    )
    
    # Add various requirements
    original_ticket.add_requirement(
        title="Test Requirement",
        priority="medium",
        author="julio"
    )
    
    original_ticket.add_user_story(
        persona="tester",
        goal="validate serialization",
        benefit="data persists correctly",
        story_points=2,
        author="julio"
    )
    
    original_ticket.add_expected_result(
        description="Data should serialize correctly",
        verification_method="automated"
    )
    
    original_ticket.add_gherkin_scenario(
        title="Serialize ticket data",
        given=["A ticket with requirements exists"],
        when=["The ticket is serialized"],
        then=["All requirement data is preserved"],
        author="julio"
    )
    
    # Serialize to dictionary
    ticket_dict = original_ticket.to_dict()
    
    # Verify all requirement data is in the dictionary
    assert 'requirements' in ticket_dict
    assert 'user_stories' in ticket_dict
    assert 'expected_results' in ticket_dict
    assert 'gherkin_scenarios' in ticket_dict
    assert ticket_dict['requirements_status'] == 'draft'
    
    print("  ✅ Ticket serialization includes requirements")
    
    # Deserialize from dictionary
    restored_ticket = Ticket.from_dict(ticket_dict)
    
    # Verify all data is restored correctly
    assert len(restored_ticket.requirements) == 1
    assert len(restored_ticket.user_stories) == 1
    assert len(restored_ticket.expected_results) == 1
    assert len(restored_ticket.gherkin_scenarios) == 1
    
    assert restored_ticket.requirements[0].title == "Test Requirement"
    assert restored_ticket.user_stories[0].persona == "tester"
    assert restored_ticket.user_stories[0].story_points == 2
    assert restored_ticket.expected_results[0].description == "Data should serialize correctly"
    assert restored_ticket.gherkin_scenarios[0].title == "Serialize ticket data"
    
    print("  ✅ Ticket deserialization restores requirements correctly")

def test_storage_with_requirements():
    """Test that storage operations work with requirements."""
    print("🔍 Testing Storage with requirements...")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Initialize a git repository (required for TicketStorage)
        os.system("git init .")
        os.system("git config user.email 'thinmanj@gmail.com'")
        os.system("git config user.name 'Test User'")
        
        # Initialize storage
        storage = TicketStorage()
        storage.initialize()
        
        # Create ticket with requirements
        ticket = Ticket(
            id="STORAGE-001",
            title="Storage Test Ticket",
            reporter="julio",
            reporter_email="thinmanj@gmail.com"
        )
        
        # Add comprehensive requirements
        ticket.add_requirement(
            title="Storage Requirement",
            description="Data must persist correctly",
            priority="high",
            acceptance_criteria=["Data saved to disk", "Data loads correctly"],
            author="julio"
        )
        
        ticket.add_user_story(
            persona="user",
            goal="save my work",
            benefit="I don't lose data",
            story_points=3,
            author="julio"
        )
        
        ticket.add_expected_result(
            description="Ticket persists between sessions",
            success_criteria=["File created on disk", "Data readable after restart"],
            verification_method="manual"
        )
        
        gherkin_text = """@storage @persistence
Scenario: Save and load ticket
  Given I have a ticket with requirements
  When I save the ticket
  And I restart the application
  Then the ticket should still exist
  And all requirements should be intact"""
        
        ticket.add_gherkin_from_text(gherkin_text, author="julio")
        
        # Save ticket
        storage.save_ticket(ticket)
        print("  ✅ Ticket with requirements saved successfully")
        
        # Load ticket back
        loaded_ticket = storage.load_ticket("STORAGE-001")
        assert loaded_ticket is not None
        
        # Verify all requirements are loaded correctly
        assert len(loaded_ticket.requirements) == 1
        assert len(loaded_ticket.user_stories) == 1
        assert len(loaded_ticket.expected_results) == 1
        assert len(loaded_ticket.gherkin_scenarios) == 1
        
        assert loaded_ticket.requirements[0].title == "Storage Requirement"
        assert loaded_ticket.requirements[0].priority == "high"
        assert len(loaded_ticket.requirements[0].acceptance_criteria) == 2
        
        assert loaded_ticket.user_stories[0].persona == "user"
        assert loaded_ticket.user_stories[0].story_points == 3
        
        assert loaded_ticket.expected_results[0].verification_method == "manual"
        assert len(loaded_ticket.expected_results[0].success_criteria) == 2
        
        assert "storage" in loaded_ticket.gherkin_scenarios[0].tags
        assert "persistence" in loaded_ticket.gherkin_scenarios[0].tags
        
        print("  ✅ Ticket with requirements loaded successfully")
        
        # Test listing tickets still works
        all_tickets = storage.list_tickets()
        assert len(all_tickets) == 1
        assert all_tickets[0].id == "STORAGE-001"
        
        print("  ✅ Ticket listing works with requirements")

def run_all_tests():
    """Run all requirement feature tests."""
    print("🚀 Starting Requirements Feature Tests")
    print("=" * 50)
    
    try:
        test_requirements_model()
        print()
        
        test_user_stories_model()
        print()
        
        test_expected_results_model()
        print()
        
        test_gherkin_scenarios_model()
        print()
        
        test_ticket_requirements_integration()
        print()
        
        test_ticket_serialization_with_requirements()
        print()
        
        test_storage_with_requirements()
        print()
        
        print("=" * 50)
        print("🎉 All Requirements Feature Tests PASSED!")
        print()
        print("✨ Requirements management features are working correctly:")
        print("   • Requirements with acceptance criteria ✅")
        print("   • User stories with story points ✅")
        print("   • Expected results with verification ✅")
        print("   • Gherkin scenarios with BDD format ✅")
        print("   • Ticket integration and metrics ✅")
        print("   • Data persistence and serialization ✅")
        print()
        print("🎯 Ready for production use!")
        
        return True
        
    except Exception as e:
        print("=" * 50)
        print(f"❌ Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)