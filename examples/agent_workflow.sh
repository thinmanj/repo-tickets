#!/bin/bash

# Agent Workflow Example for repo-tickets
# This script demonstrates a complete autonomous agent workflow
# for managing tickets, epics, and backlog items.

set -e  # Exit on any error

# Configuration
AGENT_NAME="autonomous-agent-v1"
PROJECT_NAME="AI Features Enhancement"
LOG_FILE="agent_workflow.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
    echo "✅ $1" >> "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    echo "⚠️ $1" >> "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    echo "❌ $1" >> "$LOG_FILE"
}

# Agent workflow functions
check_system() {
    log "Phase 1: System Check"
    
    # Check if tickets CLI is available
    if ! command -v tickets &> /dev/null; then
        error "tickets CLI not found. Please install repo-tickets."
        exit 1
    fi
    
    # Initialize if needed
    if [[ ! -d ".tickets" ]]; then
        log "Initializing ticket system..."
        tickets init
        success "Ticket system initialized"
    else
        success "Ticket system found"
    fi
    
    # Check current status
    local ticket_count=$(tickets list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local epic_count=$(tickets epic list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local backlog_count=$(tickets backlog list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    
    log "Current state: $ticket_count tickets, $epic_count epics, $backlog_count backlog items"
}

create_epic() {
    log "Phase 2: Epic Creation"
    
    # Check if epic already exists
    local existing_epic=$(tickets epic list --format json 2>/dev/null | jq -r ".[] | select(.name == \"$PROJECT_NAME\") | .id" 2>/dev/null || echo "")
    
    if [[ -n "$existing_epic" ]]; then
        warning "Epic '$PROJECT_NAME' already exists with ID: $existing_epic"
        EPIC_ID="$existing_epic"
    else
        log "Creating new epic: $PROJECT_NAME"
        
        local result=$(tickets epic create \
            --name "$PROJECT_NAME" \
            --description "Comprehensive AI features enhancement including smart automation, intelligent analysis, and user experience improvements" \
            --goals "Implement AI-powered ticket analysis,Add intelligent priority scoring,Create automated workflow suggestions,Enhance user experience with smart features" \
            --success-criteria "All AI features functional and tested,Performance benchmarks met,User adoption >80%,Documentation complete" \
            --priority "high" \
            --start-date "$(date +'%Y-%m-%d')" \
            --stakeholders "Product Manager,Engineering Team,QA Team" \
            --format json 2>/dev/null)
        
        if [[ $? -eq 0 ]]; then
            EPIC_ID=$(echo "$result" | jq -r '.id')
            success "Created epic: $EPIC_ID - $PROJECT_NAME"
        else
            error "Failed to create epic"
            exit 1
        fi
    fi
}

populate_backlog() {
    log "Phase 3: Backlog Population"
    
    # Define backlog items
    local backlog_items=(
        "AI Ticket Analysis Engine|Implement machine learning model for automatic ticket classification and priority suggestion|95|high|medium"
        "Smart Priority Scoring|Develop intelligent priority scoring algorithm based on business impact and effort|90|high|low"
        "Automated Workflow Suggestions|Create system to suggest workflow optimizations based on ticket patterns|85|medium|medium"
        "Natural Language Processing for Descriptions|Add NLP to extract key information from ticket descriptions|80|medium|high"
        "Predictive Analytics Dashboard|Build dashboard showing project health and completion predictions|75|high|high"
        "Intelligent Ticket Routing|Implement smart assignment system based on team skills and workload|70|medium|medium"
        "Voice-to-Ticket Conversion|Add capability to create tickets from voice recordings|65|low|high"
        "Automated Testing Recommendations|System to suggest test cases based on ticket content|60|medium|low"
    )
    
    for item in "${backlog_items[@]}"; do
        IFS='|' read -r title description priority_score business_value effort_estimate <<< "$item"
        
        # Check if item already exists
        local existing=$(tickets backlog list --format json 2>/dev/null | jq -r ".[] | select(.title == \"$title\") | .id" 2>/dev/null || echo "")
        
        if [[ -n "$existing" ]]; then
            warning "Backlog item '$title' already exists"
        else
            log "Adding backlog item: $title"
            tickets backlog add \
                --title "$title" \
                --description "$description" \
                --priority-score "$priority_score" \
                --business-value "$business_value" \
                --effort-estimate "$effort_estimate" \
                --tags "ai,enhancement,automation" \
                --format json > /dev/null
            
            if [[ $? -eq 0 ]]; then
                success "Added: $title (Priority: $priority_score)"
            else
                warning "Failed to add: $title"
            fi
        fi
    done
}

convert_high_priority_items() {
    log "Phase 4: High Priority Item Conversion"
    
    # Get high priority backlog items (score > 85)
    local high_priority_items=$(tickets backlog list --format json 2>/dev/null | jq -r '.[] | select(.priority_score > 85) | .id' 2>/dev/null || echo "")
    
    if [[ -z "$high_priority_items" ]]; then
        warning "No high priority backlog items found"
        return
    fi
    
    log "Converting high priority backlog items to tickets..."
    
    while IFS= read -r item_id; do
        if [[ -n "$item_id" ]]; then
            local item_data=$(tickets backlog list --format json 2>/dev/null | jq -r ".[] | select(.id == \"$item_id\")" 2>/dev/null)
            local item_title=$(echo "$item_data" | jq -r '.title')
            
            log "Converting backlog item: $item_title"
            
            # Create ticket from backlog item
            local ticket_result=$(tickets create \
                --title "$item_title" \
                --description "$(echo "$item_data" | jq -r '.description')" \
                --priority "high" \
                --status "todo" \
                --assignee "$AGENT_NAME" \
                --epic-id "$EPIC_ID" \
                --tags "ai,backlog-converted,high-priority" \
                --format json 2>/dev/null)
            
            if [[ $? -eq 0 ]]; then
                local ticket_id=$(echo "$ticket_result" | jq -r '.id')
                success "Created ticket: $ticket_id from backlog item $item_id"
            else
                warning "Failed to create ticket from backlog item: $item_id"
            fi
        fi
    done <<< "$high_priority_items"
}

create_implementation_tickets() {
    log "Phase 5: Implementation Ticket Creation"
    
    # Create standard implementation tickets for the epic
    local ticket_templates=(
        "Architecture Design|Design the overall architecture for AI features including data flow, API structure, and integration points|medium|todo|8"
        "Data Pipeline Setup|Set up data collection and preprocessing pipeline for AI model training|medium|todo|12"
        "ML Model Development|Develop and train machine learning models for ticket analysis and priority scoring|high|todo|20"
        "API Development|Implement REST APIs for AI feature integration with existing ticket system|medium|todo|16"
        "Frontend Integration|Integrate AI features into the user interface with proper UX design|medium|todo|14"
        "Testing Framework|Create comprehensive testing framework for AI features including unit and integration tests|medium|todo|10"
        "Performance Optimization|Optimize AI models and system performance for production deployment|medium|todo|8"
        "Documentation|Create technical documentation, user guides, and API documentation|low|todo|6"
        "Security Review|Conduct security review and implement necessary security measures|high|todo|4"
        "Deployment|Deploy AI features to production with monitoring and rollback capabilities|high|todo|6"
    )
    
    for template in "${ticket_templates[@]}"; do
        IFS='|' read -r title description priority status estimated_hours <<< "$template"
        
        # Check if ticket already exists
        local existing=$(tickets list --format json 2>/dev/null | jq -r ".[] | select(.title == \"$PROJECT_NAME - $title\") | .id" 2>/dev/null || echo "")
        
        if [[ -n "$existing" ]]; then
            warning "Ticket '$PROJECT_NAME - $title' already exists"
        else
            log "Creating implementation ticket: $title"
            
            local ticket_result=$(tickets create \
                --title "$PROJECT_NAME - $title" \
                --description "$description" \
                --priority "$priority" \
                --status "$status" \
                --epic-id "$EPIC_ID" \
                --tags "implementation,ai-features" \
                --estimated-hours "$estimated_hours" \
                --format json 2>/dev/null)
            
            if [[ $? -eq 0 ]]; then
                local ticket_id=$(echo "$ticket_result" | jq -r '.id')
                success "Created: $ticket_id - $title (${estimated_hours}h estimated)"
            else
                warning "Failed to create ticket: $title"
            fi
        fi
    done
}

create_subtasks() {
    log "Phase 6: Subtask Creation"
    
    # Get ML Model Development ticket ID
    local parent_ticket=$(tickets list --format json 2>/dev/null | jq -r ".[] | select(.title | contains(\"ML Model Development\")) | .id" 2>/dev/null | head -1)
    
    if [[ -n "$parent_ticket" ]]; then
        log "Creating subtasks for ML Model Development: $parent_ticket"
        
        local subtasks=(
            "Data Collection and Preparation|Collect and prepare training data from existing tickets|low|todo|4"
            "Feature Engineering|Design and implement feature extraction from ticket data|medium|todo|6"
            "Model Training|Train and validate machine learning models|high|todo|8"
            "Model Evaluation|Evaluate model performance and fine-tune parameters|medium|todo|2"
        )
        
        for subtask in "${subtasks[@]}"; do
            IFS='|' read -r title description priority status estimated_hours <<< "$subtask"
            
            local subtask_result=$(tickets create \
                --title "$title" \
                --description "$description" \
                --priority "$priority" \
                --status "$status" \
                --parent-ticket-id "$parent_ticket" \
                --epic-id "$EPIC_ID" \
                --tags "subtask,ml-model" \
                --estimated-hours "$estimated_hours" \
                --format json 2>/dev/null)
            
            if [[ $? -eq 0 ]]; then
                local subtask_id=$(echo "$subtask_result" | jq -r '.id')
                success "Created subtask: $subtask_id - $title"
            else
                warning "Failed to create subtask: $title"
            fi
        done
    else
        warning "Parent ticket for ML Model Development not found"
    fi
}

simulate_work_progress() {
    log "Phase 7: Simulating Work Progress"
    
    # Get some tickets to simulate progress
    local todo_tickets=$(tickets list --status todo --format json 2>/dev/null | jq -r '.[0:3] | .[] | .id' 2>/dev/null || echo "")
    
    if [[ -n "$todo_tickets" ]]; then
        log "Simulating work progress on selected tickets..."
        
        local counter=1
        while IFS= read -r ticket_id; do
            if [[ -n "$ticket_id" ]]; then
                case $counter in
                    1)
                        log "Starting work on ticket: $ticket_id"
                        tickets update "$ticket_id" \
                            --status "in-progress" \
                            --assignee "$AGENT_NAME" \
                            --add-comment "Agent: Started working on this ticket - analyzing requirements" \
                            --format json > /dev/null
                        success "Ticket $ticket_id moved to in-progress"
                        ;;
                    2)
                        log "Completing work on ticket: $ticket_id"
                        tickets update "$ticket_id" \
                            --status "done" \
                            --assignee "$AGENT_NAME" \
                            --actual-hours "6" \
                            --add-comment "Agent: Completed ticket - all requirements implemented and tested" \
                            --format json > /dev/null
                        success "Ticket $ticket_id completed"
                        ;;
                    3)
                        log "Updating progress on ticket: $ticket_id"
                        tickets update "$ticket_id" \
                            --add-comment "Agent: 50% complete - initial implementation done, testing in progress" \
                            --format json > /dev/null
                        success "Added progress update to ticket $ticket_id"
                        ;;
                esac
                ((counter++))
            fi
        done <<< "$todo_tickets"
    else
        warning "No todo tickets found for progress simulation"
    fi
}

generate_reports() {
    log "Phase 8: Generating Reports"
    
    # Generate comprehensive status report
    log "Generating status report..."
    local total_tickets=$(tickets list --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local todo_tickets=$(tickets list --status todo --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local in_progress_tickets=$(tickets list --status "in-progress" --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local done_tickets=$(tickets list --status done --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    local epic_tickets=$(tickets list --epic-id "$EPIC_ID" --format json 2>/dev/null | jq length 2>/dev/null || echo "0")
    
    # Generate epic progress report
    log "Epic Progress Report:"
    echo "==================="
    echo "Epic: $PROJECT_NAME ($EPIC_ID)"
    echo "Total Tickets: $total_tickets"
    echo "Epic Tickets: $epic_tickets"
    echo "Todo: $todo_tickets"
    echo "In Progress: $in_progress_tickets"
    echo "Done: $done_tickets"
    echo "==================="
    
    # Calculate completion percentage
    if [[ $epic_tickets -gt 0 ]]; then
        local completion=$((done_tickets * 100 / epic_tickets))
        success "Epic completion: ${completion}%"
    fi
    
    # Generate JSON report
    cat > "agent_report.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "agent": "$AGENT_NAME",
  "epic": {
    "id": "$EPIC_ID",
    "name": "$PROJECT_NAME",
    "total_tickets": $epic_tickets,
    "completion_percentage": $((done_tickets * 100 / epic_tickets))
  },
  "tickets": {
    "total": $total_tickets,
    "todo": $todo_tickets,
    "in_progress": $in_progress_tickets,
    "done": $done_tickets
  },
  "workflow_completed": true
}
EOF
    
    success "Generated agent_report.json"
}

cleanup() {
    log "Phase 9: Cleanup"
    
    # Archive completed workflow
    local archive_dir="workflow_archives/$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$archive_dir"
    
    cp "$LOG_FILE" "$archive_dir/"
    cp "agent_report.json" "$archive_dir/" 2>/dev/null || true
    
    success "Workflow archived to: $archive_dir"
    
    # Reset agent assignment on remaining tickets (optional)
    log "Cleaning up agent assignments..."
    local agent_tickets=$(tickets list --assignee "$AGENT_NAME" --format json 2>/dev/null | jq -r '.[] | select(.status != "done") | .id' 2>/dev/null || echo "")
    
    if [[ -n "$agent_tickets" ]]; then
        while IFS= read -r ticket_id; do
            if [[ -n "$ticket_id" ]]; then
                tickets update "$ticket_id" --assignee "" --add-comment "Agent: Workflow complete - unassigning for human review" --format json > /dev/null 2>&1 || true
            fi
        done <<< "$agent_tickets"
    fi
}

# Main execution
main() {
    log "=== Agent Workflow Started ==="
    log "Agent: $AGENT_NAME"
    log "Project: $PROJECT_NAME"
    
    check_system
    create_epic
    populate_backlog
    convert_high_priority_items
    create_implementation_tickets
    create_subtasks
    simulate_work_progress
    generate_reports
    cleanup
    
    success "=== Agent Workflow Complete ==="
    
    # Final summary
    echo ""
    echo "🤖 Agent Workflow Summary:"
    echo "- Epic created and managed"
    echo "- Backlog populated with AI feature ideas"
    echo "- High priority items converted to tickets"
    echo "- Implementation plan created with subtasks"
    echo "- Work progress simulated"
    echo "- Comprehensive reports generated"
    echo ""
    echo "📁 Generated files:"
    echo "- $LOG_FILE (detailed log)"
    echo "- agent_report.json (summary report)"
    echo "- workflow_archives/ (archived results)"
    echo ""
    echo "🎯 Next steps:"
    echo "- Review generated tickets and epic"
    echo "- Assign real team members to tickets"
    echo "- Begin implementation of AI features"
    echo "- Monitor progress through ticket system"
}

# Run main function
main "$@"