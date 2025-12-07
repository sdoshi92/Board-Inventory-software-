# Bulk Issue Request Workflow Changes

## Summary of Changes

This update simplifies the bulk issue request workflow by removing the requirement for users to select specific serial numbers during request creation. Instead:

1. **Users requesting boards**: Only specify the quantity needed per category
2. **Admin approval/issuance**: Specific boards are automatically assigned when the request is issued

---

## Files Modified

### 1. Frontend Changes

#### `/app/board_inventory/frontend/src/components/IssueRequests.js`

**Changes Made:**
- Removed "Selection Mode" dropdown (quantity vs specific boards)
- Removed "Preview" button and auto-select preview functionality
- Removed specific board selection interface
- Simplified form to only ask for category and quantity
- Updated bulk request submission to send only `category_id` and `quantity`
- Updated display logic to show "To be assigned" for requests without serial numbers
- Updated total boards calculation to use quantity field

**Key Updates:**
- Lines 55-66: Simplified `bulkFormData` state (removed mode, selected_boards, auto_select_preview)
- Lines 118-138: Simplified `resetForm()` and `addCategory()`
- Lines 165-192: Simplified `updateCategory()` to handle only quantity changes
- Lines 258-266: Updated `getTotalBoardsRequested()` to use quantity
- Lines 297-338: Simplified bulk submit validation (removed specific board checks)
- Lines 1038-1061: Replaced mode selection and preview UI with simple quantity input
- Lines 566-600: Updated request display to show quantity when boards not assigned

#### `/app/board_inventory/frontend/src/components/Outward.js`

**Changes Made:**
- Updated bulk request display to show total boards based on quantity
- Added display logic for quantity-based requests (without serial numbers)
- Fixed confirmation dialog to properly route bulk requests

**Key Updates:**
- Lines 80-92: Calculate total boards using quantity field
- Lines 529-543: Show "Qty: X - to be assigned" for requests without serial numbers
- Line 622: Fixed onClick handler to include bulk-request type

---

### 2. Backend Changes

#### `/app/board_inventory/backend/server.py`

**Changes Made:**
- Updated `BoardRequest` model to support optional serial numbers and quantity
- Modified bulk request creation endpoint to store quantity without assigning boards
- Updated outward endpoint to support both old format (with serial numbers) and new format (with quantity)
- Boards are now assigned during issuance based on availability at that time

**Key Updates:**
- Lines 174-178: Updated `BoardRequest` model
  - `serial_number`: Made optional (assigned during issuance)
  - `condition`: Made optional (assigned during issuance)
  - `quantity`: Added field to store requested quantity

- Lines 179-192: Updated `BulkIssueRequest` model comments

- Lines 563-620: Completely rewrote `create_bulk_issue_request()` endpoint
  - Only validates category exists and checks availability
  - Stores category_id and quantity (no serial numbers)
  - Boards assigned later during issuance

- Lines 838-906: Updated outward endpoint `issue_board()`
  - Added backward compatibility for old requests (with serial numbers)
  - Added new logic to assign boards during issuance based on quantity
  - Finds available boards when issuing and assigns them automatically
  - Calculates expected total correctly for both formats

---

## Backward Compatibility

✅ **Existing Data Supported:**
- Old bulk requests with pre-assigned serial numbers will continue to work
- The outward endpoint checks if `serial_number` exists (old format) or `quantity` exists (new format)
- Both workflows are supported simultaneously

✅ **Migration Not Required:**
- No database migration needed
- Old pending requests can still be issued
- New requests use the simplified workflow

---

## Testing Recommendations

1. **Create New Bulk Request:**
   - Go to Issue Requests → New Request → Multiple Boards
   - Select categories and quantities only
   - Verify no serial numbers are shown
   - Submit request

2. **Approve & Issue:**
   - Admin approves the request
   - Go to Outward Operations → Approved Requests
   - Click "Issue Board"
   - Boards should be automatically assigned during issuance

3. **Verify Display:**
   - Check that pending requests show "Quantity: X - To be assigned"
   - After issuance, boards should show specific serial numbers

4. **Test Old Data:**
   - If you have existing approved requests, they should still work
   - Issue them normally through the Outward workflow

---

## Benefits

✅ **Simplified User Experience**: Users don't need to select specific boards
✅ **Faster Request Creation**: No preview or manual board selection needed
✅ **Admin Control**: Admins see which boards will be assigned at issuance time
✅ **Flexible Inventory**: Boards assigned based on real-time availability
✅ **Backward Compatible**: Works with existing data

---

## Technical Notes

- Frontend validation ensures sufficient boards are available
- Backend validates availability at both request creation and issuance
- Serial numbers assigned automatically using FIFO (first available boards)
- Supports both "New" and "Repaired" condition boards
- Boards in "Repairing" location with "Repaired" condition are also eligible
