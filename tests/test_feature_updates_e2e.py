
import os
import subprocess
import time
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
import pytest

# Configuration
TEST_DB = "test_e2e.db"
TEST_PORT = 8501
BASE_URL = f"http://localhost:{TEST_PORT}"

def setup_test_db():
    """Setup a fresh test database and seed it."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # Use environment variable to point to the test database
    os.environ["ILIN_DB_URL"] = f"sqlite:///{TEST_DB}"
    os.environ["ILIN_PORT"] = str(TEST_PORT)
    os.environ["ILIN_DATA_DIR"] = "test_data"
    
    # Create test data dir
    test_data_dir = Path("test_data")
    if test_data_dir.exists():
        shutil.rmtree(test_data_dir)
    test_data_dir.mkdir()
    (test_data_dir / "documents").mkdir()
    (test_data_dir / "indexes").mkdir()
    (test_data_dir / "models").mkdir()

    from ilin.storage.database import init_db, SessionLocal
    from ilin.storage.models import User, Topic, TopicAssignment, Document
    from ilin.auth.service import hash_password

    init_db()
    db = SessionLocal()
    
    # Create admin
    admin = User(username="admin", password_hash=hash_password("admin123"), role="admin")
    db.add(admin)
    
    # Create regular user
    user = User(username="testuser", password_hash=hash_password("user123"), role="user")
    db.add(user)
    db.commit()
    
    # Create topic
    topic = Topic(name="General AI", description="General Artificial Intelligence Knowledge", created_by=admin.id)
    db.add(topic)
    db.commit()
    
    # Assign user to topic
    assignment = TopicAssignment(topic_id=topic.id, user_id=user.id)
    db.add(assignment)
    
    # Add a dummy document for admin management test
    doc = Document(
        topic_id=topic.id,
        filename="test_doc.txt",
        file_path="test_data/documents/test_doc.txt",
        file_type="txt",
        file_size=100,
        status="indexed"
    )
    db.add(doc)
    
    db.commit()
    db.close()
    print("Test database seeded.")

def run_e2e_tests():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        print("--- Starting E2E Tests ---")

        # 1. Login as testuser
        print("1. Testing Login...")
        page.goto(BASE_URL)
        page.fill("#username", "testuser")
        page.fill("#password", "user123")
        page.click("button[type='submit']")
        page.wait_for_url("**/chat")
        print("   Login successful.")

        # 2. Session Continuity
        print("2. Testing Session Continuity...")
        # Select topic
        page.click("text=General AI")
        page.wait_for_selector("textarea")
        
        # Send first message
        page.fill("textarea", "Hello, who are you?")
        page.click("button:has(svg)") # Send button
        # Wait for AI response (streaming)
        page.wait_for_selector("text=AI", state="visible")
        # Since we use a mock, it should be fast
        time.sleep(2) # Give it some time to finish streaming

        # Send second message
        page.fill("textarea", "Tell me more about yourself.")
        page.click("button:has(svg)")
        time.sleep(2)

        # Go to Recent Inquiries
        page.click("button:has-text('Recent Inquiries')")
        page.wait_for_selector("text=Intelligence Logs")
        
        # Verify only one session exists
        logs = page.query_selector_all(".card")
        if len(logs) == 1:
            print("   SUCCESS: Only one session found.")
        else:
            print(f"   FAILURE: Found {len(logs)} sessions instead of 1.")

        # 3. UI Overlap Fix
        print("3. Testing UI Overlap Fix...")
        # While in History, check if Chat area is NOT visible
        chat_header = page.query_selector("header:has-text('General AI')")
        if not chat_header or not chat_header.is_visible():
            print("   SUCCESS: Chat header is hidden in History.")
        else:
            print("   FAILURE: Chat header is still visible in History.")
        
        messages = page.query_selector("#messages-container")
        if not messages or not messages.is_visible():
            print("   SUCCESS: Messages container is hidden in History.")
        else:
            print("   FAILURE: Messages container is still visible in History.")

        # Click Knowledge Bases
        page.click("button:has-text('Knowledge Bases')")
        page.wait_for_selector("text=Intelligence Hub")
        
        # Verify history list is NOT visible
        history_list = page.query_selector("text=Intelligence Logs")
        if not history_list or not history_list.is_visible():
            print("   SUCCESS: History list is hidden in Topics.")
        else:
            print("   FAILURE: History list is still visible in Topics.")

        # 4. Session Deletion
        print("4. Testing Session Deletion...")
        page.click("button:has-text('Recent Inquiries')")
        page.wait_for_selector("text=Intelligence Logs")
        
        # Click delete button
        page.on("dialog", lambda dialog: dialog.accept())
        page.click("button[title='Delete']")
        
        time.sleep(1) # Wait for UI update
        if page.query_selector("text=No previous intelligence logs found."):
            print("   SUCCESS: Session deleted.")
        else:
            print("   FAILURE: Session not deleted.")

        # 5. Clear All History
        print("5. Testing Clear All History...")
        # Create 2 sessions
        for i in range(2):
            page.click("button:has-text('Knowledge Bases')")
            page.click("text=General AI")
            page.fill("textarea", f"Session {i} message")
            page.click("button:has(svg)")
            time.sleep(2)
            page.click("button:has-text('Recent Inquiries')")
            time.sleep(0.5)

        logs = page.query_selector_all(".card")
        print(f"   Currently have {len(logs)} sessions.")
        
        page.on("dialog", lambda dialog: dialog.accept())
        page.click("button:has-text('Clear All History')")
        
        time.sleep(1)
        if page.query_selector("text=No previous intelligence logs found."):
            print("   SUCCESS: All history cleared.")
        else:
            print("   FAILURE: History not cleared.")

        # 6. Admin Document Management
        print("6. Testing Admin Document Management...")
        page.click("button:has-text('Disconnect')")
        page.wait_for_url("**/")
        
        page.fill("#username", "admin")
        page.fill("#password", "admin123")
        page.click("button[type='submit']")
        page.wait_for_url("**/admin")
        print("   Admin login successful.")
        
        page.click("button:has-text('Knowledge Bases')")
        page.wait_for_selector("text=General AI")
        
        page.click("button:has-text('Manage Docs')")
        page.wait_for_selector("text=Manage Cluster Documents")
        
        # Verify test_doc.txt is listed
        if page.query_selector("text=test_doc.txt"):
            print("   SUCCESS: test_doc.txt found.")
        else:
            print("   FAILURE: test_doc.txt not found.")
            
        # Delete document
        page.on("dialog", lambda dialog: dialog.accept())
        page.click("button[title='Delete']") # The one in Manage Docs modal
        
        time.sleep(1)
        if not page.query_selector("text=test_doc.txt"):
            print("   SUCCESS: Document deleted.")
        else:
            print("   FAILURE: Document not deleted.")

        page.screenshot(path="tests/screenshots/test_e2e_result.png")
        print(f"--- E2E Tests Completed. Screenshot saved to tests/screenshots/test_e2e_result.png ---")
        browser.close()

if __name__ == "__main__":
    setup_test_db()
    
    # Start server
    print(f"Starting server on port {TEST_PORT}...")
    server_process = subprocess.Popen(
        [".venv/Scripts/python.exe", "run.py"],
        env={**os.environ, "ILIN_PORT": str(TEST_PORT), "ILIN_DB_URL": f"sqlite:///{TEST_DB}"}
    )
    
    # Wait for server to be ready
    time.sleep(5)
    
    try:
        run_e2e_tests()
    finally:
        print("Stopping server...")
        server_process.terminate()
        server_process.wait()
        # Clean up
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        if os.path.exists("test_data"):
            shutil.rmtree("test_data")
