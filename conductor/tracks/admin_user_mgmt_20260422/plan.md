# Implementation Plan: Admin User Management and 'Add User' Functionality

## Phase 1: Backend API Enhancements
- [x] Task: Implement Delete User Endpoint e52d72b
    - [ ] Write failing test for \DELETE /api/users/{user_id}\ in \	ests/test_users_admin.py\
    - [ ] Implement \delete_user\ in \ilin/api/admin_router.py\ (ensure TopicAssignment cleanup and self-delete protection)
    - [ ] Verify tests pass and coverage >50%
- [x] Task: Implement Edit User Endpoint 3442cc9
    - [ ] Write failing test for \PATCH /api/users/{user_id}\ in \	ests/test_users_admin.py\
    - [ ] Implement \update_user\ in \ilin/api/admin_router.py\ (allow password reset)
    - [ ] Verify tests pass and coverage >50%
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Backend API Enhancements' (Protocol in workflow.md)

## Phase 2: Frontend Integration
- [ ] Task: Wire Delete Functionality
    - [ ] Implement \deleteUser\ javascript handler in \dminApp()\ in \dmin.html\ (or separate JS file)
    - [ ] Add delete button and confirmation dialog to users table in \dmin.html\
- [ ] Task: Wire Edit Functionality
    - [ ] Implement \editUser\ javascript handler to populate modal
    - [ ] Update user modal to support both Create and Edit modes
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Frontend Integration' (Protocol in workflow.md)

## Phase 3: Validation & Error Handling
- [ ] Task: Client-side Validation
    - [ ] Add username and password strength validation in \dmin.html\
- [ ] Task: API Error Handling
    - [ ] Display actionable error messages in the user modal (e.g., duplicate username)
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Validation & Error Handling' (Protocol in workflow.md)

## Phase 4: Final Testing & Documentation
- [ ] Task: Comprehensive Test Suite
    - [ ] Ensure all scenarios (success, duplicate username, self-delete, unauthorized access) are covered in \	ests/test_users_admin.py\
    - [ ] Run full test suite and verify 50% coverage
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Final Testing & Documentation' (Protocol in workflow.md)