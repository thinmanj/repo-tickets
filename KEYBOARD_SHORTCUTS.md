# ⌨️ Repo Tickets TUI - Keyboard Shortcuts Reference

The **Repo Tickets TUI** includes comprehensive keyboard shortcuts for maximum efficiency and power-user workflows. This reference guide covers all available shortcuts organized by context.

## 🚀 Main Interface Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| **n** / **N** | New Ticket | Open ticket creation modal |
| **r** / **R** | Refresh | Reload tickets and update display |
| **g** / **G** | Generate Report | Create and open HTML report |
| **/** | Focus Search | Jump to search input box |
| **?** | Help | Show keyboard shortcuts help screen |
| **q** / **Q** | Quit | Exit the TUI application |
| **Esc** | Clear/Back | Clear search or close modals |
| **Enter** | View Details | Open selected ticket details |
| **↑ ↓** | Navigate | Move up/down in ticket table |
| **Tab** | Focus Next | Move focus between UI elements |

## 🔢 Filter Shortcuts (Number Keys)

| Key | Filter | Shows |
|-----|---------|--------|
| **1** | All | All tickets regardless of status |
| **2** | Open | Only open tickets |
| **3** | In Progress | Only in-progress tickets |
| **4** | Blocked | Only blocked tickets |
| **5** | Closed | Only closed tickets |
| **6** | Critical | Only critical priority tickets |
| **7** | High | Only high priority tickets |

## 🔍 Search & Navigation

| Key | Action | Description |
|-----|--------|-------------|
| **/** | Focus Search | Jump cursor to search box |
| **Ctrl+L** | Clear Search | Empty search box and focus it |
| **Esc** | Clear Search | Clear search if box has content |

## 🎫 Ticket Detail View Shortcuts

When viewing a ticket's detailed information:

| Key | Action | Description |
|-----|--------|-------------|
| **j** / **J** | Journal Entry | Add journal/progress entry |
| **t** / **T** | Time Tracking | Open time tracking modal |
| **e** / **E** | Edit Ticket | Edit ticket properties (coming soon) |
| **c** / **C** | Add Comment | Add comment (coming soon) |
| **Esc** | Close Details | Return to main ticket list |

## ⏱️ Time Tracking Modal Shortcuts

When in the time tracking interface:

| Key | Action | Description |
|-----|--------|-------------|
| **s** / **S** | Start Session | Select "Start new session" |
| **x** / **X** | Stop Session | Select "Stop current session" |
| **a** / **A** | Add Time | Select "Add completed time" and focus minutes |
| **Enter** | Execute | Run the selected time tracking action |
| **Esc** | Cancel | Close time tracking without changes |

## 📝 Form Navigation

In all modal forms (Create Ticket, Journal Entry, etc.):

| Key | Action | Description |
|-----|--------|-------------|
| **Tab** | Next Field | Move to next form field |
| **Shift+Tab** | Previous Field | Move to previous form field |
| **Enter** | Submit/Confirm | Submit form (context dependent) |
| **Esc** | Cancel | Close form without saving |

## 🖱️ Mouse Integration

All keyboard shortcuts work alongside mouse interactions:

- **Click** any button to activate it
- **Click** table rows to select tickets
- **Click** in form fields to focus them
- **Scroll** in scrollable areas
- **Right-click** for context menus (where supported)

## ⚡ Power User Workflow Examples

### Quick Ticket Creation
1. Press **n** to open creation form
2. Fill in title and details
3. **Tab** through fields
4. **Enter** to create

### Rapid Filtering
1. Press **6** for critical tickets
2. Press **/** to search within critical
3. Type search terms
4. **Enter** on selected ticket

### Efficient Time Tracking  
1. **Enter** on ticket to view details
2. Press **t** for time tracking
3. Press **s** to select start session
4. **Enter** to begin tracking

### Quick Navigation
1. **↑ ↓** to browse tickets
2. **Enter** to view details
3. **j** to add progress note
4. **Esc** to return to list

## 💡 Tips for Maximum Efficiency

### 🚀 Speed Tips
- **Learn the number filters (1-7)** for instant ticket subsets
- **Use / for search** - faster than clicking search box
- **Memorize n, r, g** for most common actions
- **Use Esc liberally** - it's context-aware and safe

### 🎯 Workflow Tips  
- **Start with filters** to narrow scope before searching
- **Use ? frequently** when learning shortcuts
- **Combine shortcuts** - filter → search → select → action
- **Time tracking shortcuts (s/x/a)** speed up session management

### 🧠 Memory Aids
- **Letters make sense**: **n**ew, **r**efresh, **g**enerate, **j**ournal, **t**ime
- **Numbers follow status order**: 1=all, 2=open, 3=progress, 4=blocked, 5=closed
- **Priority order**: 6=critical, 7=high
- **/ for search** (common across many applications)
- **? for help** (universal convention)

## 🔧 Customization

The keyboard shortcuts are defined using Textual's binding system and can be customized by modifying the `BINDINGS` arrays in:

- `RepoTicketsTUI.BINDINGS` - Main interface shortcuts
- `TicketDetailScreen.BINDINGS` - Detail view shortcuts  
- `TimeTrackingScreen.BINDINGS` - Time tracking shortcuts

## 📚 Learning Path

### Beginner (Learn First)
1. **?** - Help screen
2. **n** - New ticket
3. **r** - Refresh
4. **Enter** - View details
5. **Esc** - Back/Cancel

### Intermediate (Add Next)
1. **/** - Focus search
2. **1-5** - Basic filters  
3. **j** - Journal entries (in details)
4. **t** - Time tracking (in details)

### Advanced (Power User)
1. **6-7** - Priority filters
2. **Ctrl+L** - Clear search
3. **s/x/a** - Time tracking actions
4. **Tab** navigation in forms

Start with the beginner shortcuts and gradually add more as they become muscle memory. The TUI is designed to be fully functional with either keyboard, mouse, or a combination of both!

## 🎊 Happy Ticket Managing!

With these shortcuts, you can navigate the entire TUI without ever reaching for the mouse. Whether you're a terminal power user or just getting started, these shortcuts will significantly speed up your workflow and make ticket management a breeze! 

Remember: Press **?** anytime in the TUI to see the help screen with all shortcuts.