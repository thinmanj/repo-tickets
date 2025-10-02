# 🎫 Repo Tickets TUI - Interactive Terminal Interface

The **Repo Tickets TUI** provides a modern, interactive terminal user interface for managing tickets, built using the [Textual framework](https://textual.textualize.io/). This interface offers a rich, responsive experience with advanced features like real-time filtering, detailed ticket views, and comprehensive project metrics.

## 🚀 Features

### Core Interface
- **Modern Terminal UI**: Built with Textual for rich, responsive terminal experiences
- **Real-time Search**: Search across ticket titles, descriptions, and IDs as you type
- **Advanced Filtering**: Filter by status (Open, In Progress, Blocked, Closed) or priority (Critical, High)
- **Interactive Tables**: Click-to-select ticket rows for detailed views
- **Live Metrics**: Real-time project metrics including completion rates, time tracking, and risk assessment

### Ticket Management
- **Detailed Ticket Views**: Modal screens showing complete ticket information with collapsible sections
- **Create New Tickets**: Full-featured form for creating tickets with validation
- **Journal Entries**: Add progress updates, blockers, milestones, decisions, risk assessments, and meeting notes
- **Time Tracking**: Start/stop sessions or add completed time with work type classification
- **Status Updates**: Change ticket status and other properties (coming soon)

### Project Insights
- **Project Metrics Panel**: Shows total tickets, open/closed counts, and completion percentages
- **Time Tracking Panel**: Displays logged time, estimates, active sessions, and remaining work
- **Risk Assessment Panel**: Automated risk scoring based on blocked tickets, critical issues, and stale tickets

## 🎮 Usage

### Launching the TUI
```bash
# From any repository with initialized tickets
tickets tui

# Or from the repo-tickets directory
python demo_tui.py
```

### Interface Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🎫 Repo Tickets TUI                                  │
├─────────────────┬───────────────────────────────────────────────────────────┤
│   🔍 Search &   │                    📊 Project Metrics                     │
│     Filter      │  ┌─────────────────────────────────────────────────────┐  │
│                 │  │ Total: 15        ⏱️ Time Tracking      ⚠️ Risk     │  │
│ [Search Box]    │  │ Open: 8          Logged: 45.5h         Level: 🟡   │  │
│                 │  │ Closed: 7        Estimated: 60h        Medium      │  │
│ Filters:        │  │ Complete: 46.7%  Active: 2             Score: 35   │  │
│ [All Tickets]   │  └─────────────────────────────────────────────────────┘  │
│ [ Open      ]   │                                                           │
│ [In Progress]   │  ┌───────────────────────────────────────────────────────┐ │
│ [ Blocked   ]   │  │ ID    │ Title           │ Status    │ Priority │ Age │ │
│ [ Closed    ]   │  ├───────┼─────────────────┼───────────┼──────────┼─────┤ │
│                 │  │ TUI-1 │ 🔵 Implement... │ 🟡 prog   │ 🟠 high  │ 2d  │ │
│ Priority:       │  │ BUG-2 │ 🔴 Fix form...  │ 🔴 block  │ 🔥 crit  │ 1d  │ │
│ [Critical  ]    │  └───────────────────────────────────────────────────────┘ │
│ [ High     ]    │                                                           │
│                 │                                                           │
│ Actions:        │                                                           │
│ [➕ New Ticket] │                                                           │
│ [🔄 Refresh   ] │                                                           │
│ [📊 Report    ] │                                                           │
└─────────────────┴───────────────────────────────────────────────────────────┘
│ Navigation: ↑↓ Select | Enter: View Details | Esc: Back | Tab: Focus Next │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Controls

#### Keyboard Shortcuts ⌨️

**Main Interface:**
- **n / N**: Create new ticket
- **r / R**: Refresh tickets list  
- **g / G**: Generate HTML report
- **/ (slash)**: Focus search box
- **?**: Show help screen
- **q / Q**: Quit application
- **Esc**: Close modals / clear search
- **Enter**: View selected ticket details
- **↑ ↓**: Navigate ticket table rows
- **Tab**: Move focus between interface elements

**Filters (Number Keys):**
- **1**: Show all tickets
- **2**: Show open tickets
- **3**: Show in-progress tickets
- **4**: Show blocked tickets
- **5**: Show closed tickets
- **6**: Show critical priority
- **7**: Show high priority

**Search:**
- **Ctrl+L**: Clear search box

**In Ticket Details:**
- **j / J**: Add journal entry
- **t / T**: Time tracking
- **e / E**: Edit ticket
- **c / C**: Add comment
- **Esc**: Close ticket details

**Time Tracking Modal:**
- **s / S**: Start time session
- **x / X**: Stop time session
- **a / A**: Add completed time
- **Enter**: Execute selected action
- **Esc**: Cancel operation

#### Mouse Controls
- Click buttons, select table rows, interact with forms
- All keyboard shortcuts also work with mouse

#### Search & Filtering
- Type in search box to filter tickets in real-time
- Use **/** to quickly focus search box
- Click filter buttons or use number keys for status/priority filters
- Filters are combinable (e.g., search + status filter)
- Use **Ctrl+L** to quickly clear search

#### Ticket Details Modal
When you select a ticket, a detailed modal shows:

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎫 TUI-1: Implement TUI Interface            │
├─────────────────────────────────────────────────────────────────┤
│ Status: in-progress     │ Reporter: Test User                   │
│ Priority: high          │ Created: 2024-01-15 10:30             │
│ Assignee: Test User     │ Age: 2 days                          │
├─────────────────────────────────────────────────────────────────┤
│ Description                                                     │
│ Build a modern, interactive terminal interface using...         │
├─────────────────────────────────────────────────────────────────┤
│ ⏱️ Time Tracking                                                │
│ ┌─────────────────┬──────────────────┬─────────────────────────┐ │
│ │ Total: 3.5h     │ Estimated: 8h    │ Remaining: 4.5h        │ │
│ │ 🔄 Active: 1.2h │                  │                        │ │
│ └─────────────────┴──────────────────┴─────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ 📝 Journal Entries                                              │
│ ▼ PROGRESS - 2024-01-15 14:20                                  │
│   Started implementing modal screens for ticket details...      │
│   Completion: 25% | Milestone: MVP Complete                    │
├─────────────────────────────────────────────────────────────────┤
│ 💬 Comments                                                     │
│ ▼ Test User - 2024-01-15 09:45                                 │
│   This is a high-priority feature for the next release...      │
├─────────────────────────────────────────────────────────────────┤
│ [Close] [Edit Ticket] [Add Journal] [Track Time]               │
└─────────────────────────────────────────────────────────────────┘
```

### Creating New Tickets

The "New Ticket" button opens a comprehensive form:

```
┌─────────────────────────────────────────────────────────────────┐
│                        🆕 Create New Ticket                     │
├─────────────────────────────────────────────────────────────────┤
│ Title * ┌─────────────────────────────────────────────────────┐  │
│         │ Enter ticket title...                               │  │
│         └─────────────────────────────────────────────────────┘  │
│                                                                 │
│ Description ┌─────────────────────────────────────────────────┐ │
│             │ Detailed description of the ticket...           │ │
│             │                                                 │ │
│             │                                                 │ │
│             └─────────────────────────────────────────────────┘ │
│                                                                 │
│ Priority      │ Assignee                                        │
│ ┌───────────┐ │ ┌─────────────────────────────────────────────┐ │
│ │ [Medium ▼]│ │ │ Assign to...                                │ │
│ └───────────┘ │ └─────────────────────────────────────────────┘ │
│                                                                 │
│ Est. Hours    │ Story Points                                    │
│ ┌───────────┐ │ ┌─────────────────────────────────────────────┐ │
│ │ 0.0       │ │ │ 0                                           │ │
│ └───────────┘ │ └─────────────────────────────────────────────┘ │
│                                                                 │
│ Labels (comma-separated)                                        │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ bug, feature, urgent...                                     │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                          [Cancel] [Create Ticket]              │
└─────────────────────────────────────────────────────────────────┘
```

### Journal Entry Form

Adding journal entries through the TUI:

```
┌─────────────────────────────────────────────────────────────────┐
│                  📝 Add Journal Entry - TUI-1                   │
├─────────────────────────────────────────────────────────────────┤
│ Entry Type                                                      │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Progress Update ▼]                                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Content *                                                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Describe the progress, blocker, or update...                │ │
│ │                                                             │ │
│ │                                                             │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Hours Spent     │ Completion %                                  │
│ ┌─────────────┐ │ ┌─────────────────────────────────────────────┐ │
│ │ 0.0         │ │ │ 0-100                                       │ │
│ └─────────────┘ │ └─────────────────────────────────────────────┘ │
│                                                                 │
│ Milestone                                                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Milestone name...                                           │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Dependencies (ticket IDs) | Risks                              │
│ ┌─────────────────────────┐ │ ┌─────────────────────────────────┐ │
│ │ TICKET-1, TICKET-2...   │ │ │ Risk 1, Risk 2...               │ │
│ └─────────────────────────┘ │ └─────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                           [Cancel] [Add Entry]                 │
└─────────────────────────────────────────────────────────────────┘
```

### Time Tracking Interface

```
┌─────────────────────────────────────────────────────────────────┐
│                    ⏱️ Time Tracking - TUI-1                     │
├─────────────────────────────────────────────────────────────────┤
│ Action                                                          │
│ ○ Start new session                                             │
│ ○ Stop current session                                          │
│ ● Add completed time                                            │
│                                                                 │
│ Work Type                                                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ [Work ▼]                                                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Description                                                     │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ What are you working on?                                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ Minutes (for 'Add completed time')                              │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ 120                                                         │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                            [Cancel] [Execute]                  │
└─────────────────────────────────────────────────────────────────┘
```

## 📊 Metrics & Analytics

The TUI provides three key metric panels:

### Project Metrics
- **Total tickets**: Complete count of all tickets
- **Open/Closed breakdown**: Current ticket distribution
- **Completion rate**: Percentage of resolved tickets

### Time Tracking Metrics
- **Total logged time**: Sum of all time entries across tickets
- **Total estimated time**: Sum of all time estimates
- **Active sessions**: Number of currently running time tracking sessions
- **Remaining time**: Difference between estimates and logged time

### Risk Assessment
- **Risk Level**: Automated assessment (Low 🟢 / Medium 🟡 / High 🔴)
- **Risk Score**: Numerical score (0-100) based on:
  - Blocked tickets (20 points each)
  - Critical open tickets (15 points each)
  - Stale tickets >30 days (5 points each)
- **Blocked count**: Number of tickets in blocked status
- **Stale count**: Tickets older than 30 days and still open

## ⚡ Performance & Responsiveness

- **Real-time updates**: All data refreshes automatically when changes are made
- **Efficient filtering**: Instant search results as you type
- **Responsive design**: Adapts to terminal window size
- **Keyboard shortcuts**: Full keyboard navigation support
- **Mouse support**: Click interactions for modern terminal environments

## 🎨 Visual Design

- **Modern styling**: Glass-morphism effects and smooth animations
- **Color coding**: Status and priority indicators with emoji icons
- **Rich formatting**: Tables, panels, progress bars, and collapsible sections
- **Consistent theming**: Professional appearance across all screens
- **Accessibility**: High contrast and clear visual hierarchy

## 🔗 Integration

The TUI seamlessly integrates with the existing repo-tickets ecosystem:

- **CLI Compatibility**: All TUI operations sync with CLI commands
- **VCS Integration**: Respects git/hg/jj repository settings and user info
- **Report Generation**: Direct access to HTML report generation
- **Storage Backend**: Uses the same JSON storage as CLI operations

## 🛠️ Technical Details

- **Framework**: [Textual](https://textual.textualize.io/) for rich terminal UIs
- **Rendering**: [Rich](https://rich.readthedocs.io/) for advanced text formatting
- **Architecture**: Event-driven with modal screens and reactive widgets
- **Performance**: Efficient data handling with lazy loading and caching
- **Compatibility**: Python 3.8+ with cross-platform terminal support

## 🚦 Getting Started

1. **Prerequisites**: Ensure you have `textual` and `rich` installed
   ```bash
   pip install textual rich
   ```

2. **Initialize tickets** in your repository:
   ```bash
   tickets init
   ```

3. **Launch the TUI**:
   ```bash
   tickets tui
   ```

4. **Navigate and explore** using mouse clicks or keyboard controls

The TUI provides a comprehensive, modern interface for all your ticket management needs, combining the power of the CLI with the convenience of an interactive visual interface!