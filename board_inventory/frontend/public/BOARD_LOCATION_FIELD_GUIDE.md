# Board Location Field - Complete Guide

## Overview

The **Location** field tracks the physical and operational status of each electronic board throughout its lifecycle in the inventory system.

---

## All Possible Location Values

### 1. **In stock** 🟦
- **Badge Color:** Blue
- **Meaning:** Board is physically in the warehouse/storage and available
- **When Set:** 
  - When new boards are added via Inward (New Board workflow)
  - When boards are returned to inventory
- **Available for Issue:** ✅ Yes (if condition is New or Repaired)

---

### 2. **Issued for machine** 🟪
- **Badge Color:** Purple
- **Meaning:** Board has been issued and is being used in a machine/equipment
- **When Set:** 
  - When board is issued through Outward Operations
  - Most common issuance type
- **Available for Issue:** ❌ No (already in use)
- **Additional Fields Set:**
  - `issued_by`: Who issued the board
  - `issued_to`: Person/team receiving the board
  - `project_number`: Project it's being used for
  - `issued_date_time`: When it was issued

---

### 3. **Repairing** 🟠
- **Badge Color:** Orange
- **Meaning:** Board is currently in the repair department/process
- **When Set:**
  - When boards are received via Inward (Repairing/Return workflow)
  - When boards fail and are sent for repair
- **Available for Issue:** 
  - ❌ No (if condition is "Repairing")
  - ✅ Yes (if condition is "Repaired" - repaired and ready)
- **Note:** Once repaired, the condition changes to "Repaired" while location stays "Repairing" until moved back to stock

---

### 4. **Issued for spares** 🟣
- **Badge Color:** Indigo
- **Meaning:** Board has been issued as a spare part (backup/replacement inventory)
- **When Set:**
  - When board is issued through Outward Operations for spare parts inventory
  - Used for maintaining spare parts at different locations
- **Available for Issue:** ❌ No (already allocated as spare)
- **Additional Fields Set:** Same as "Issued for machine"

---

### 5. **At customer site** 🩷
- **Badge Color:** Pink
- **Meaning:** Board has been sent to and is physically located at a customer's site
- **When Set:**
  - When board is issued through Outward Operations for customer use
  - For field installations or customer-owned equipment
- **Available for Issue:** ❌ No (at customer location)
- **Additional Fields Set:** Same as "Issued for machine"

---

## Location Lifecycle Flow

### Typical Board Journey:

```
┌─────────────┐
│  In stock   │ ← New board arrives
│   (Blue)    │
└──────┬──────┘
       │
       ├─→ Issued for machine (Purple) ─→ Used in equipment
       │
       ├─→ Issued for spares (Indigo) ─→ Spare parts inventory
       │
       ├─→ At customer site (Pink) ─→ Customer location
       │
       └─→ Repairing (Orange) ─┐
                                │
                         Board gets fixed
                                │
                                ↓
                    ┌──────────────────┐
                    │ Repaired & Ready  │
                    │  Location: Still  │
                    │    "Repairing"    │
                    │ Condition: Repaired│
                    └─────────┬─────────┘
                              │
                              ↓
                    Can be issued or moved
                    back to "In stock"
```

---

## How Location Relates to Condition

Location and Condition work together:

| Location | Possible Conditions | Available for Issue? |
|----------|-------------------|---------------------|
| In stock | New, Repaired | ✅ Yes |
| In stock | Scrap | ❌ No |
| Issued for machine | Any | ❌ No (in use) |
| Issued for spares | Any | ❌ No (allocated) |
| At customer site | Any | ❌ No (off-site) |
| Repairing | Repairing | ❌ No (being repaired) |
| Repairing | Repaired | ✅ Yes (ready to issue) |
| Repairing | New | ✅ Yes (false alarm/no repair needed) |
| Repairing | Scrap | ❌ No (beyond repair) |

---

## Business Rules

### For Issue Requests:
Only boards meeting ALL criteria are available:
- ✅ Location: "In stock" OR ("Repairing" AND condition "Repaired")
- ✅ Condition: "New" OR "Repaired"
- ❌ Condition: NOT "Scrap"
- ❌ Condition: NOT "Repairing" (unless in Repairing location with Repaired condition)

### For Inward Operations:

**New Board Workflow:**
- Sets location: "In stock"
- Sets condition: "New"

**Repairing/Return Workflow:**
- Sets location: "Repairing"
- Condition can be: "Repairing", "New", "Repaired", or "Scrap"

---

## Where to See Location

### In the System:
1. **Search Page:** Main board listing with location badges
2. **Inward Page:** Recent inward activities show locations
3. **Reports → Serial Number History:** Full location history
4. **Issue Requests:** Available boards filtered by location
5. **Outward Operations:** Shows current location when issuing

### Location Display:
- Color-coded badges for easy identification
- 5 distinct colors for 5 locations
- Shown alongside board serial number and condition

---

## Technical Details

### Database Field:
```python
location: str = "In stock"  # Default value
```

### Valid Values (Case-Sensitive):
- `"In stock"`
- `"Issued for machine"`
- `"Repairing"`
- `"Issued for spares"`
- `"At customer site"`

### API Updates:
Location can be updated via:
- `PUT /api/boards/{board_id}` - Update existing board
- `POST /api/outward` - Issues board and changes location
- Inward workflows automatically set appropriate locations

---

## Summary

The **Location** field is crucial for:
- ✅ Tracking physical board location
- ✅ Determining board availability
- ✅ Managing inventory across multiple uses
- ✅ Audit trail and accountability
- ✅ Preventing double-allocation

**5 Locations | Color-Coded | Lifecycle Tracking | Smart Availability Rules**
