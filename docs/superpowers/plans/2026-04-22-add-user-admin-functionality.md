# Add User Functionality (Admin Linked) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete working Add User functionality fully integrated with admin panel, including validation, role assignment, proper error handling and UI integration.

**Architecture:** Extend existing admin user endpoint, add proper validation, password hashing, role enforcement, and connect frontend modal to backend API. Follow existing repository patterns.

**Tech Stack:** FastAPI, SQLAlchemy, Pydantic, bcrypt, Jinja2, vanilla JS

---

## File Mapping

| File | Action | Responsibility |
|------|--------|----------------|
| `ilin/auth/models.py` | Modify | Extend UserCreate schema with validation rules |
| `ilin/auth/service.py` | Verify | Confirm password hashing is correctly implemented |
| `ilin/storage/models.py` | Verify | Confirm User model has all required fields |
| `ilin/api/admin_router.py` | Modify | Complete POST /api/users endpoint implementation |
| `ilin/frontend/templates/admin.html` | Modify | Connect Add User modal form to backend API |
| `tests/test_admin_users.py` | Create | Integration tests for admin user creation |

---

### Task 1: Validate and extend UserCreate schema

**Files:**
- Modify: `ilin/auth/models.py`

- [ ] **Step 1: Update UserCreate schema with proper validation**

```python
from pydantic import BaseModel, Field, validator
import re

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, description="Username must be 3-50 characters")
    password: str = Field(min_length=8, max_length=128, description="Password must be at least 8 characters")
    role: str = Field(default="user", description="User role: user or admin")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username may only contain letters, numbers and underscores')
        return v.lower()

    @validator('role')
    def valid_role(cls, v):
        if v not in ['user', 'admin']:
            raise ValueError('Role must be either "user" or "admin"')
        return v
```

- [ ] **Step 2: Run existing auth tests**
Run: `pytest tests/test_auth.py -v`
Expected: All existing tests pass

---

### Task 2: Complete admin user creation endpoint

**Files:**
- Modify: `ilin/api/admin_router.py`

- [ ] **Step 1: Implement complete POST /api/users endpoint**

```python
@admin_router.post("/users", status_code=201, response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """Create new user (admin only)"""
    # Developer: Vishal Raj V, Senior Engineer
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail=f"Username '{user_data.username}' is already taken"
        )
    
    # Hash password
    password_hash = hash_password(user_data.password)
    
    # Create user
    new_user = User(
        username=user_data.username,
        password_hash=password_hash,
        role=user_data.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
```

- [ ] **Step 2: Verify endpoint exists and is protected**
Run: `python -c "from ilin.api.main import app; print([route.path for route in app.routes if '/users' in route.path])"`
Expected: `/api/users` listed with POST method

---

### Task 3: Connect frontend admin modal to API

**Files:**
- Modify: `ilin/frontend/templates/admin.html`

- [ ] **Step 1: Add form submission handler for Add User modal**

```javascript
async function handleCreateUser(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const userData = {
        username: formData.get('username'),
        password: formData.get('password'),
        role: formData.get('role')
    };

    try {
        const response = await fetch('/api/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData),
            credentials: 'same-origin'
        });

        if (response.ok) {
            event.target.reset();
            document.getElementById('addUserModal').classList.add('hidden');
            await loadUsersList(); // Refresh user table
            showNotification('User created successfully', 'success');
        } else {
            const error = await response.json();
            showNotification(error.detail || 'Failed to create user', 'error');
        }
    } catch (err) {
        showNotification('Connection error. Please try again.', 'error');
    }
}

// Attach handler on page load
document.addEventListener('DOMContentLoaded', () => {
    const createUserForm = document.getElementById('createUserForm');
    if (createUserForm) {
        createUserForm.addEventListener('submit', handleCreateUser);
    }
});
```

- [ ] **Step 2: Verify form exists in template**
Confirm form has id `createUserForm` with fields: `username`, `password`, `role` select

---

### Task 4: Create integration tests

**Files:**
- Create: `tests/test_admin_users.py`

- [ ] **Step 1: Write admin user creation tests**

```python
# Developer: Vishal Raj V, Senior Engineer
import pytest
from fastapi.testclient import TestClient
from ilin.api.main import app

client = TestClient(app)

def test_admin_create_user(admin_auth_headers):
    """Test admin can successfully create new user"""
    response = client.post(
        "/api/users",
        json={
            "username": "testnewuser",
            "password": "testpass123",
            "role": "user"
        },
        headers=admin_auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testnewuser"
    assert data["role"] == "user"
    assert "password_hash" not in data

def test_non_admin_cannot_create_user(user_auth_headers):
    """Test regular users cannot access user creation endpoint"""
    response = client.post(
        "/api/users",
        json={"username": "hacker", "password": "badpass"},
        headers=user_auth_headers
    )
    
    assert response.status_code == 403

def test_duplicate_username_rejected(admin_auth_headers):
    """Test duplicate usernames return proper 409 error"""
    # Create first user
    client.post("/api/users", json={"username": "duplicate", "password": "test123"}, headers=admin_auth_headers)
    
    # Try create same user again
    response = client.post("/api/users", json={"username": "duplicate", "password": "test123"}, headers=admin_auth_headers)
    
    assert response.status_code == 409
```

- [ ] **Step 2: Run tests**
Run: `pytest tests/test_admin_users.py -v`
Expected: All 3 tests pass

---

### Task 5: End-to-end verification

- [ ] **Step 1: Start application**
Run: `python run.py`

- [ ] **Step 2: Login as admin**
Navigate to `http://localhost:8000/login`
Login with admin credentials

- [ ] **Step 3: Test Add User functionality**
1. Open Add User modal
2. Enter valid username, password, select role
3. Submit form
4. Verify user appears in user list
5. Verify error messages show correctly for invalid inputs

- [ ] **Step 4: Run full test suite**
Run: `pytest`
Expected: All tests pass

---

## Plan Complete

Plan saved to `docs/superpowers/plans/2026-04-22-add-user-admin-functionality.md`. Two execution options:

1. **Subagent-Driven (Recommended)** - I dispatch a fresh subagent per task, review between tasks, fast parallel execution
2. **Inline Execution** - Execute tasks in this session sequentially with checkpoints

Which approach would you like to use?
