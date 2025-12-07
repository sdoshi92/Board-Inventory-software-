# Bulk Issue Request Workflow Changes - V2

## Summary of Changes

**VERSION 2 UPDATE**: Added board assignment during approval step

### Workflow:
1. **Users requesting boards**: Specify only quantity needed per category
2. **Admin approval**: **SELECT SPECIFIC SERIAL NUMBERS** for each category
3. **Admin issuance**: Issue the pre-assigned boards through Outward page

---

## What's New in V2

### Frontend Changes

#### `/app/board_inventory/frontend/src/components/IssueRequests.js`

**NEW FEATURES:**
- **Board Assignment Dialog** when admin clicks "Approve & Issue" on bulk requests
- Admin must select specific serial numbers for each category
- Visual board selection with checkboxes
- Validation to ensure correct quantity selected
- Shows available boards with condition and location badges
- Prevents approval without complete board assignment

**Implementation Details:**
- Added state: `approvalDialog`, `requestToApprove`, `boardAssignments`
- New function: `confirmApprovalWithBoards()` - saves assigned boards
- New function: `toggleBoardAssignment()` - handles board selection
- Updated `handleApprove()` - opens dialog for new-format bulk requests
- New Dialog UI - shows categories, available boards, selection progress

**Lines Modified:**
- Lines 40-48: Added new state variables
- Lines 362-398: Completely rewrote `handleApprove()` to detect and handle board assignment
- Lines 400-450: Added `confirmApprovalWithBoards()` and `toggleBoardAssignment()`
- Lines 1232-1340: Added complete Board Assignment Dialog UI

---

### Backend Changes

#### `/app/board_inventory/backend/server.py`

**NEW API ENDPOINT:**
```
PUT /api/bulk-issue-requests/{request_id}/assign-boards
```

**Purpose**: Accept admin-selected boards and approve the request

**Request Body:**
```json
{
  "boards": [
    {
      "category_id": "...",
      "serial_number": "...",
      "condition": "..."
    }
  ],
  "status": "approved"
}
```

**Implementation:**
- New model: `BoardAssignmentUpdate` - validates assignment data
- Validates all boards are available before accepting
- Updates bulk request with assigned boards
- Sets approved status and approval metadata
- Returns updated request

**Lines Added:**
- Lines 787-798: Added `BoardAssignmentUpdate` model
- Lines 800-855: New endpoint `assign_boards_to_bulk_request()`

---

## Complete Workflow

### 1. User Creates Request
- Selects categories
- Enters quantities (e.g., 3 boards from Category A, 2 from Category B)
- Submits request
- **Result**: Request saved with quantities only (no serial numbers)

### 2. Admin Reviews & Approves
- Sees pending request with quantities
- Clicks "Approve & Issue"
- **NEW**: Board Assignment Dialog opens
- Admin sees available boards for each category
- Admin selects specific serial numbers (3 for Category A, 2 for Category B)
- Clicks "Approve with Assigned Boards"
- **Result**: Request marked as "approved" with specific boards assigned

### 3. Admin Issues Boards
- Goes to Outward Operations
- Sees approved request with assigned boards
- Clicks "Issue Board"
- Confirms issuance
- **Result**: Selected boards are issued to user/project

---

## User Interface

### Request Creation (User)
```
Category: Electronics Board A
Quantity: [3]  ← Just enter number
         
Category: Electronics Board B  
Quantity: [2]  ← Just enter number

[Submit Request]
```

### Approval Dialog (Admin)
```
┌─────────────────────────────────────────┐
│ Assign Boards for Approval              │
├─────────────────────────────────────────┤
│ Issued To: John Doe                     │
│ Project: PRJ-2024-001                   │
├─────────────────────────────────────────┤
│                                         │
│ Electronics Board A          2/3 ✓      │
│ Select 3 boards:                        │
│ ☑ SN-001  [New] [In Stock]            │
│ ☑ SN-002  [New] [In Stock]            │
│ ☑ SN-003  [Repaired] [In Stock]       │
│ ☐ SN-004  [New] [In Stock]            │
│                                         │
│ Electronics Board B          2/2 ✓      │
│ Select 2 boards:                        │
│ ☑ SN-101  [New] [In Stock]            │
│ ☑ SN-102  [New] [In Stock]            │
│                                         │
│     [Cancel]  [Approve with Boards]     │
└─────────────────────────────────────────┘
```

---

## API Flow

### 1. Create Request
```
POST /api/issue-requests/bulk
{
  "categories": [
    {"category_id": "cat-1", "quantity": 3},
    {"category_id": "cat-2", "quantity": 2}
  ],
  "issued_to": "user@example.com",
  "project_number": "PRJ-2024-001"
}

Response: Request created with status "pending"
```

### 2. Assign Boards & Approve (NEW)
```
PUT /api/bulk-issue-requests/{id}/assign-boards
{
  "boards": [
    {"category_id": "cat-1", "serial_number": "SN-001", "condition": "New"},
    {"category_id": "cat-1", "serial_number": "SN-002", "condition": "New"},
    {"category_id": "cat-1", "serial_number": "SN-003", "condition": "Repaired"},
    {"category_id": "cat-2", "serial_number": "SN-101", "condition": "New"},
    {"category_id": "cat-2", "serial_number": "SN-102", "condition": "New"}
  ],
  "status": "approved"
}

Response: Request updated with assigned boards, status "approved"
```

### 3. Issue Boards
```
POST /api/outward
{
  "request_id": "req-123"
}

Response: Boards issued successfully
```

---

## Backward Compatibility

✅ **Old Requests Still Work:**
- Requests with pre-assigned serial numbers skip the assignment dialog
- They are approved directly (old workflow)
- No changes to existing data needed

✅ **New Requests Use New Flow:**
- Requests with quantities trigger the assignment dialog
- Admin must assign boards before approval

---

## Testing

1. **Create Bulk Request** with quantities only
2. **Admin clicks "Approve & Issue"** → Dialog opens
3. **Select specific boards** for each category
4. **Click "Approve with Assigned Boards"**
5. **Go to Outward** → See approved request with assigned boards
6. **Issue boards** → Boards issued successfully

---

## Benefits

✅ **Admin Control**: Admin chooses exactly which boards to assign  
✅ **Transparency**: Admin sees all available options before deciding  
✅ **Flexibility**: Can choose based on board condition, age, etc.  
✅ **Validation**: Cannot approve without selecting correct quantity  
✅ **User Simplicity**: Users still only enter quantities  

---

## Files Modified

1. **IssueRequests.js** - Added board assignment dialog
2. **Outward.js** - No changes in V2 (already working)
3. **server.py** - Added board assignment endpoint

**Total Changes**: ~150 lines added
