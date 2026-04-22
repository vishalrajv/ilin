# Add User Functionality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Add User functionality fully integrated with admin panel, including backend API, frontend UI, validation, and testing.

**Architecture:**
- Backend API already exists at `POST /api/users` in admin_router.py
- Frontend UI modal already exists in admin.html
- Missing: Delete user endpoint, proper error handling, frontend validation, and test coverage
- All functionality is admin-protected via `require_admin` dependency

**Tech Stack:** FastAPI, SQLAlchemy, Alpine.js, Tailwind CSS, pytest

---

## ✅ Status Audit

### Already Implemented:
- [x] Backend `POST /api/users` endpoint (admin_router.py lines 49-73)
- [x] UserCreate / UserResponse Pydantic models
- [x] Password hashing service
- [x] Frontend user modal form in admin.html
- [x] Frontend `createUser()` javascript handler
- [x] Users list table in admin panel
- [x] Admin authorization guard on all endpoints

---

## Task 1: Add Delete User Endpoint

**Files:**
- Modify: `ilin/api/admin_router.py`

- [ ] **Step 1: Add delete user endpoint**

```python
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Delete all user assignments first
    db.query(TopicAssignment).filter(TopicAssignment.user_id == user_id).delete()
    
    db.delete(user)
    db.commit()
```

- [ ] **Step 2: Add frontend delete handler in adminApp()**

```javascript
async deleteUser(id) {
    if (!confirm('Confirm: Delete this authorized entity?')) return;
    const resp = await apiCall(`/api/users/${id}`, { method: 'DELETE' });
    if (resp.ok) await this.loadUsers();
},
```

- [ ] **Step 3: Wire delete button in user table**

```html
<button @click="deleteUser(user.id)" class="text-slate-500 hover:text-red-400 transition-colors">
```

---

## Task 2: Add Frontend Validation & Error Handling

**Files:**
- Modify: `ilin/frontend/templates/admin.html`

- [ ] **Step 1: Add username validation rules**
- [ ] **Step 2: Add password strength requirements**
- [ ] **Step 3: Add error message display in user modal**
- [ ] **Step 4: Handle duplicate username error from API**

---

## Task 3: Add Edit User Functionality

**Files:**
- Modify: `ilin/api/admin_router.py`
- Modify: `ilin/frontend/templates/admin.html`

- [ ] **Step 1: Add PATCH /api/users/{user_id} endpoint**
- [ ] **Step 2: Add edit button in user table**
- [ ] **Step 3: Reuse user modal for edit mode**
- [ ] **Step 4: Allow password reset by admin**

---

## Task 4: Test Coverage

**Files:**
- Create: `tests/test_users_admin.py`

- [ ] **Step 1: Write test for create user success**
- [ ] **Step 2: Write test for duplicate username failure**
- [ ] **Step 3: Write test for delete user**
- [ ] **Step 4: Write test for admin self-delete protection**
- [ ] **Step 5: Write test for non-admin access forbidden**

---

## Task 5: Final Verification

- [ ] **Step 1: Run full test suite**
- [ ] **Step 2: Manual test flow: login as admin → create user → verify appears in list → delete user**
- [ ] **Step 3: Verify non-admin users cannot access user management endpoints**
- [ ] **Step 4: Verify password hashes are never returned in API responses**

---

## ✅ Plan Complete

Plan saved to `tasks/add-user-functionality-plan.md`.

Two execution options:

**1. Subagent-Driven (Recommended)** - I dispatch a fresh subagent per task, review between tasks, fast parallel execution

**2. Inline Execution** - Execute tasks sequentially in this session with checkpoints

Which approach would you prefer?
