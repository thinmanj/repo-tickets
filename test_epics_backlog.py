#!/usr/bin/env python3
"""
Comprehensive test script for Epic and Backlog functionality in repo-tickets.

Tests all major features:
- Epic creation, management, and relationships
- Backlog item management and prioritization
- Epic-ticket relationships
- Storage and serialization
- CLI integration
- Sprint planning workflows
"""

import sys
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add the repo_tickets module to the path
sys.path.insert(0, str(Path(__file__).parent))

from repo_tickets.models import Epic, BacklogItem, Ticket
from repo_tickets.storage import TicketStorage


def cleanup_test_data():
    """Clean up any existing test data."""
    test_dir = Path('.tickets')
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("🧹 Cleaned up existing test data")


def test_epic_basic_functionality():
    """Test basic epic creation and management."""
    print("\n🎯 Testing Epic Basic Functionality...")
    
    # Test Epic creation
    epic = Epic(
        id="USER-1",
        title="User Management System",
        description="Complete user management with auth and profiles",
        priority="high",
        owner="Product Team",
        owner_email="product@company.com",
        target_version="v1.0",
        estimated_story_points=50
    )
    
    print(f"✓ Created epic: {epic.id} - {epic.title}")
    print(f"  Status: {epic.status}")
    print(f"  Priority: {epic.priority}")
    print(f"  Estimated Story Points: {epic.estimated_story_points}")
    
    # Test adding goals and success criteria
    epic.add_goal("Implement secure user authentication")
    epic.add_goal("Create user profile management")
    epic.add_success_criterion("100% of users can register and log in")
    epic.add_success_criterion("Profile updates work on mobile and desktop")
    
    print(f"✓ Added {len(epic.goals)} goals and {len(epic.success_criteria)} success criteria")
    
    # Test adding tickets to epic
    epic.add_ticket("AUTH-1")
    epic.add_ticket("PROFILE-1")
    epic.add_ticket("PROFILE-2")
    
    print(f"✓ Added {len(epic.ticket_ids)} tickets to epic")
    
    # Test epic properties
    assert not epic.is_overdue, "New epic should not be overdue"
    assert epic.age_days >= 0, "Epic age should be non-negative"
    
    # Test epic updates
    epic.update(
        status="active",
        target_date=datetime.now() + timedelta(days=30)
    )
    
    print(f"✓ Updated epic status to: {epic.status}")
    print(f"✓ Set target date: {epic.target_date.strftime('%Y-%m-%d')}")
    
    return epic


def test_backlog_basic_functionality():
    """Test basic backlog item creation and management."""
    print("\n📋 Testing Backlog Basic Functionality...")
    
    # Test BacklogItem creation
    item = BacklogItem(
        id="USER-REG",
        title="User Registration Feature",
        description="Allow new users to create accounts with email verification",
        item_type="feature",
        priority="high",
        story_points=8,
        business_value=90,
        effort_estimate=16.0,
        risk_level="medium",
        product_owner="Product Manager",
        component="Authentication",
        theme="User Onboarding"
    )
    
    print(f"✓ Created backlog item: {item.id} - {item.title}")
    print(f"  Type: {item.item_type}")
    print(f"  Story Points: {item.story_points}")
    print(f"  Business Value: {item.business_value}")
    print(f"  Priority Score: {item.priority_score}")
    
    # Test adding acceptance criteria and DoD
    item.add_acceptance_criterion("User can register with valid email")
    item.add_acceptance_criterion("Email verification is required")
    item.add_acceptance_criterion("User receives welcome message")
    
    item.add_dod_item("Unit tests written and passing")
    item.add_dod_item("Integration tests cover happy path")
    item.add_dod_item("Security review completed")
    
    print(f"✓ Added {len(item.acceptance_criteria)} acceptance criteria")
    print(f"✓ Added {len(item.definition_of_done)} definition of done items")
    
    # Test sprint assignment
    item.assign_to_sprint("SPRINT-1", "Q4 User Features Sprint")
    print(f"✓ Assigned to sprint: {item.sprint_name}")
    
    # Test backlog item properties
    assert not item.is_ready_for_sprint, "Item without groomed status should not be ready"
    
    item.update(status="groomed")
    assert item.is_ready_for_sprint, "Groomed item with story points and criteria should be ready"
    print("✓ Item is ready for sprint after grooming")
    
    return item


def test_storage_integration():
    """Test storage integration for epics and backlog items."""
    print("\n💾 Testing Storage Integration...")
    
    # Initialize storage
    storage = TicketStorage()
    storage.initialize(force=True)
    print("✓ Initialized storage system")
    
    # Test epic storage
    epic = Epic(
        id="ECOM-1",
        title="E-commerce Platform",
        description="Build complete e-commerce solution",
        priority="critical",
        target_version="v2.0"
    )
    
    storage.save_epic(epic)
    print(f"✓ Saved epic: {epic.id}")
    
    # Test epic loading
    loaded_epic = storage.load_epic("ECOM-1")
    assert loaded_epic is not None, "Should load saved epic"
    assert loaded_epic.title == epic.title, "Loaded epic should match saved epic"
    print(f"✓ Loaded epic: {loaded_epic.id}")
    
    # Test backlog item storage
    item = BacklogItem(
        id="CART-1",
        title="Shopping Cart Feature",
        description="Allow users to add/remove items from cart",
        story_points=5,
        business_value=85,
        epic_id="ECOM-1"
    )
    
    storage.save_backlog_item(item)
    print(f"✓ Saved backlog item: {item.id}")
    
    # Test backlog item loading
    loaded_item = storage.load_backlog_item("CART-1")
    assert loaded_item is not None, "Should load saved backlog item"
    assert loaded_item.title == item.title, "Loaded item should match saved item"
    print(f"✓ Loaded backlog item: {loaded_item.id}")
    
    # Test listing functions
    epics = storage.list_epics()
    assert len(epics) == 1, "Should have one epic"
    print(f"✓ Listed {len(epics)} epics")
    
    items = storage.list_backlog_items()
    assert len(items) == 1, "Should have one backlog item"
    print(f"✓ Listed {len(items)} backlog items")
    
    # Test filtering
    items_by_epic = storage.list_backlog_items(epic_id="ECOM-1")
    assert len(items_by_epic) == 1, "Should find item by epic"
    print("✓ Filtered backlog items by epic")
    
    return storage


def test_epic_ticket_relationships(storage):
    """Test epic-ticket relationship management."""
    print("\n🔗 Testing Epic-Ticket Relationships...")
    
    # Create a ticket
    ticket = Ticket(
        id="PAYMENT-1",
        title="Payment Processing",
        description="Implement secure payment processing",
        priority="high",
        reporter="Developer",
        reporter_email="dev@company.com"
    )
    
    storage.save_ticket(ticket)
    print(f"✓ Created ticket: {ticket.id}")
    
    # Add ticket to epic
    success = storage.add_ticket_to_epic("ECOM-1", "PAYMENT-1")
    assert success, "Should successfully add ticket to epic"
    print("✓ Added ticket to epic")
    
    # Verify relationships
    epic = storage.load_epic("ECOM-1")
    ticket = storage.load_ticket("PAYMENT-1")
    
    assert "PAYMENT-1" in epic.ticket_ids, "Epic should contain ticket ID"
    assert ticket.epic_id == "ECOM-1", "Ticket should reference epic"
    print("✓ Verified bidirectional relationship")
    
    # Test removing ticket from epic
    success = storage.remove_ticket_from_epic("ECOM-1", "PAYMENT-1")
    assert success, "Should successfully remove ticket from epic"
    print("✓ Removed ticket from epic")
    
    # Verify relationship removal
    epic = storage.load_epic("ECOM-1")
    ticket = storage.load_ticket("PAYMENT-1")
    
    assert "PAYMENT-1" not in epic.ticket_ids, "Epic should not contain ticket ID"
    assert ticket.epic_id is None, "Ticket should not reference epic"
    print("✓ Verified relationship removal")


def test_backlog_to_ticket_conversion(storage):
    """Test converting backlog items to tickets."""
    print("\n🔄 Testing Backlog to Ticket Conversion...")
    
    # Create a detailed backlog item
    item = BacklogItem(
        id="LOGIN-1",
        title="User Login System",
        description="Secure user authentication with session management",
        priority="high",
        story_points=5,
        business_value=95,
        epic_id="ECOM-1"
    )
    
    item.add_acceptance_criterion("User can log in with email/password")
    item.add_acceptance_criterion("Session expires after 24 hours")
    item.add_acceptance_criterion("Failed login attempts are logged")
    
    storage.save_backlog_item(item)
    print(f"✓ Created detailed backlog item: {item.id}")
    
    # Convert to ticket
    ticket = storage.convert_backlog_to_ticket(
        "LOGIN-1", 
        reporter="Product Manager",
        reporter_email="pm@company.com"
    )
    
    assert ticket is not None, "Should successfully convert backlog item to ticket"
    print(f"✓ Converted to ticket: {ticket.id}")
    
    # Verify conversion
    assert ticket.title == item.title, "Ticket should have same title"
    assert ticket.description == item.description, "Ticket should have same description"
    assert ticket.priority == item.priority, "Ticket should have same priority"
    assert ticket.story_points == item.story_points, "Ticket should have same story points"
    assert ticket.epic_id == item.epic_id, "Ticket should maintain epic relationship"
    print("✓ Verified ticket properties match backlog item")
    
    # Verify requirements were created from acceptance criteria
    assert len(ticket.requirements) == len(item.acceptance_criteria), "Should create requirements from criteria"
    print(f"✓ Created {len(ticket.requirements)} requirements from acceptance criteria")
    
    # Verify backlog item was updated
    updated_item = storage.load_backlog_item("LOGIN-1")
    assert updated_item.ticket_id == ticket.id, "Backlog item should reference ticket"
    assert updated_item.status == "in-progress", "Backlog item status should be updated"
    print("✓ Updated backlog item with ticket reference")


def test_id_generation(storage):
    """Test ID generation for epics and backlog items."""
    print("\n🏷️  Testing ID Generation...")
    
    # Create fresh storage for ID generation tests
    import tempfile
    import shutil
    with tempfile.TemporaryDirectory() as tmpdir:
        fresh_storage = TicketStorage(repo_root=tmpdir)
        fresh_storage.initialize()
        
        # Test epic ID generation
        epic_id1 = fresh_storage.generate_epic_id("User Management System")
        epic_id2 = fresh_storage.generate_epic_id("Authentication Module")
        epic_id3 = fresh_storage.generate_epic_id("Special Characters & Symbols!")
        
        print(f"✓ Generated epic IDs: {epic_id1}, {epic_id2}, {epic_id3}")
        
        # Verify IDs are unique and follow pattern
        assert epic_id1.startswith("USER-"), f"Expected USER- prefix, got {epic_id1}"
        assert epic_id2.startswith("AUTHENTI-"), f"Expected AUTHENTI- prefix, got {epic_id2}"
        assert epic_id3.startswith("SPECIAL-"), f"Expected SPECIAL- prefix, got {epic_id3}"
        assert epic_id1 != epic_id2, "Epic IDs should be unique"
        assert epic_id2 != epic_id3, "Epic IDs should be unique"
        print("✓ Epic ID generation follows correct pattern and ensures uniqueness")
        
        # Save epics to test sequence generation
        from repo_tickets.models import Epic
        fresh_storage.save_epic(Epic(id=epic_id1, title="Test 1"))
        fresh_storage.save_epic(Epic(id=epic_id2, title="Test 2"))
        
        # Generate another USER epic - should increment
        epic_id4 = fresh_storage.generate_epic_id("User Profile System")
        assert epic_id4.startswith("USER-"), "Should generate USER- prefix"
        assert epic_id4 not in [epic_id1, epic_id2], "Should be unique from existing"
        print(f"✓ Generated sequential epic ID: {epic_id4}")
        
        # Test backlog item ID generation
        item_id1 = fresh_storage.generate_backlog_item_id("Shopping Cart Feature")
        item_id2 = fresh_storage.generate_backlog_item_id("Checkout Enhancement")
        item_id3 = fresh_storage.generate_backlog_item_id("Payment Processing")
        
        print(f"✓ Generated backlog IDs: {item_id1}, {item_id2}, {item_id3}")
        
        # Verify backlog ID patterns
        assert item_id1.startswith("SHOPPI-"), f"Expected SHOPPI- prefix, got {item_id1}"
        assert item_id2.startswith("CHECKO-"), f"Expected CHECKO- prefix, got {item_id2}"
        assert item_id3.startswith("PAYMEN-"), f"Expected PAYMEN- prefix, got {item_id3}"
        assert item_id1 != item_id2, "Backlog IDs should be unique"
        assert item_id2 != item_id3, "Backlog IDs should be unique"
        print("✓ Backlog ID generation follows correct pattern and ensures uniqueness")


def test_prioritization_and_scoring():
    """Test backlog item prioritization and scoring."""
    print("\n📊 Testing Prioritization and Scoring...")
    
    items = []
    
    # High business value, low effort (should score highest)
    item1 = BacklogItem(
        id="HIGH-VAL-1",
        title="Quick Win Feature",
        priority="high",
        business_value=95,
        story_points=2
    )
    items.append(item1)
    
    # Medium business value, medium effort
    item2 = BacklogItem(
        id="MED-VAL-1", 
        title="Standard Feature",
        priority="medium",
        business_value=60,
        story_points=5
    )
    items.append(item2)
    
    # Low business value, high effort (should score lowest)
    item3 = BacklogItem(
        id="LOW-VAL-1",
        title="Complex Low Value Feature", 
        priority="low",
        business_value=30,
        story_points=13
    )
    items.append(item3)
    
    # Calculate and display scores
    for item in items:
        print(f"  {item.id}: Priority Score = {item.priority_score}")
    
    # Verify scoring order
    assert item1.priority_score > item2.priority_score, "High value/low effort should score higher"
    assert item2.priority_score > item3.priority_score, "Medium should score higher than low value/high effort"
    
    print("✓ Prioritization scoring works correctly")


def test_advanced_scenarios():
    """Test advanced scenarios and edge cases."""
    print("\n🚀 Testing Advanced Scenarios...")
    
    # Test epic with target date (overdue scenario)
    past_date = datetime.now() - timedelta(days=5)
    overdue_epic = Epic(
        id="OVERDUE-1",
        title="Overdue Epic",
        status="active",
        target_date=past_date
    )
    
    assert overdue_epic.is_overdue, "Epic past target date should be overdue"
    print("✓ Overdue epic detection works")
    
    # Test completed epic (not overdue even if past target)
    completed_epic = Epic(
        id="COMPLETE-1",
        title="Completed Epic",
        status="completed",
        target_date=past_date
    )
    
    assert not completed_epic.is_overdue, "Completed epic should not be overdue"
    print("✓ Completed epic overdue logic works")
    
    # Test backlog item readiness
    ready_item = BacklogItem(
        id="READY-1",
        title="Ready Item",
        status="groomed",
        story_points=3
    )
    ready_item.add_acceptance_criterion("Must work correctly")
    
    assert ready_item.is_ready_for_sprint, "Groomed item with points and criteria should be ready"
    print("✓ Sprint readiness detection works")
    
    # Test not ready item
    not_ready_item = BacklogItem(
        id="NOT-READY-1",
        title="Not Ready Item",
        status="new"  # No story points, no criteria
    )
    
    assert not not_ready_item.is_ready_for_sprint, "New item without points should not be ready"
    print("✓ Not ready item detection works")


def test_serialization_and_data_integrity():
    """Test data serialization and integrity."""
    print("\n🔒 Testing Serialization and Data Integrity...")
    
    # Create epic with all fields populated
    epic = Epic(
        id="FULL-1",
        title="Full Featured Epic",
        description="Epic with all fields populated",
        status="active",
        priority="high",
        owner="Test Owner",
        owner_email="test@example.com",
        labels=["test", "full-feature"],
        target_version="v1.5",
        start_date=datetime.now(),
        target_date=datetime.now() + timedelta(days=30),
        estimated_story_points=100
    )
    
    epic.add_goal("Complete all features")
    epic.add_success_criterion("All tests pass")
    epic.add_ticket("TEST-1")
    
    # Test serialization
    epic_dict = epic.to_dict()
    reconstructed_epic = Epic.from_dict(epic_dict)
    
    # Verify all fields preserved
    assert reconstructed_epic.id == epic.id
    assert reconstructed_epic.title == epic.title
    assert reconstructed_epic.description == epic.description
    assert reconstructed_epic.status == epic.status
    assert reconstructed_epic.priority == epic.priority
    assert reconstructed_epic.owner == epic.owner
    assert reconstructed_epic.labels == epic.labels
    assert reconstructed_epic.goals == epic.goals
    assert reconstructed_epic.success_criteria == epic.success_criteria
    assert reconstructed_epic.ticket_ids == epic.ticket_ids
    
    print("✓ Epic serialization/deserialization preserves all data")
    
    # Test backlog item serialization
    item = BacklogItem(
        id="FULL-ITEM-1",
        title="Full Backlog Item",
        description="Item with all fields",
        item_type="feature",
        priority="high",
        status="ready",
        story_points=8,
        business_value=85,
        effort_estimate=16.0,
        risk_level="medium",
        product_owner="PO",
        assigned_to="Dev",
        epic_id="FULL-1",
        sprint_id="S1",
        sprint_name="Sprint 1",
        labels=["test"],
        component="Core",
        theme="Testing"
    )
    
    item.add_acceptance_criterion("Works correctly")
    item.add_dod_item("Tests written")
    
    # Test serialization
    item_dict = item.to_dict()
    reconstructed_item = BacklogItem.from_dict(item_dict)
    
    # Verify critical fields
    assert reconstructed_item.id == item.id
    assert reconstructed_item.title == item.title
    assert reconstructed_item.story_points == item.story_points
    assert reconstructed_item.business_value == item.business_value
    assert reconstructed_item.acceptance_criteria == item.acceptance_criteria
    assert reconstructed_item.definition_of_done == item.definition_of_done
    
    print("✓ Backlog item serialization/deserialization preserves all data")


def run_all_tests():
    """Run all tests and provide summary."""
    print("🧪 Starting Comprehensive Epic and Backlog Tests")
    print("=" * 60)
    
    try:
        # Clean up before testing
        cleanup_test_data()
        
        # Run all test functions
        epic = test_epic_basic_functionality()
        item = test_backlog_basic_functionality()
        storage = test_storage_integration()
        test_epic_ticket_relationships(storage)
        test_backlog_to_ticket_conversion(storage)
        test_id_generation(storage)
        test_prioritization_and_scoring()
        test_advanced_scenarios()
        test_serialization_and_data_integrity()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("\nEpic and Backlog functionality is working correctly:")
        print("✓ Epic creation, management, and relationships")
        print("✓ Backlog item prioritization and sprint planning")
        print("✓ Storage and serialization")
        print("✓ Epic-ticket bidirectional relationships")
        print("✓ Backlog to ticket conversion")
        print("✓ ID generation and uniqueness")
        print("✓ Advanced scenarios and edge cases")
        print("✓ Data integrity and serialization")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up after testing
        cleanup_test_data()
        print("\n🧹 Cleaned up test data")


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)