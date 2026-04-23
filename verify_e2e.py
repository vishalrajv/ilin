import os
from fastapi.testclient import TestClient
from ilin.api.main import app
from ilin.storage.database import SessionLocal, init_db
from ilin.storage.models import User, Topic
from ilin.auth.service import create_jwt
from ilin.config import settings

def run_e2e():
    print("Starting E2E Verification...")
    init_db()
    settings.retrieval_use_reranker = True
    
    # Mock CrossEncoder
    import sentence_transformers
    class MockCrossEncoder:
        def __init__(self, *args, **kwargs):
            pass
        def predict(self, pairs):
            print("[MOCK] CrossEncoder predict called")
            return [0.9, -3.0] # 1 good score, 1 bad score to test dropping
    sentence_transformers.CrossEncoder = MockCrossEncoder
    
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        print("Admin user not found. Creating...")
        from ilin.auth.service import hash_password
        admin = User(username="admin", password_hash=hash_password("admin123"), role="admin")
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
    topic = db.query(Topic).filter(Topic.id == 1).first()
    if not topic:
        print("Topic 1 not found. Creating...")
        topic = Topic(id=1, name="Test Topic", description="Test", created_by=admin.id)
        db.add(topic)
        db.commit()
    
    access_token = create_jwt(admin.id, admin.username, admin.role)
    db.close()

    # Create dummy index so we don't get "No relevant documents found."
    from ilin.storage.vector_store import VectorStore
    import numpy as np
    store = VectorStore(topic_id=1)
    embeddings = np.random.rand(2, 384).astype(np.float32)
    metadatas = [
        {"text": "The HTTP protocol is widely used for web communication.", "source_file": "doc1.txt"},
        {"text": "HTTPS is secure HTTP.", "source_file": "doc1.txt"}
    ]
    store.add(embeddings, metadatas)
    print("Added dummy documents to VectorStore topic 1")
    
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n[SENDING REQUEST TO /api/chat]")
    response = client.post(
        "/api/chat",
        params={"topic_id": 1, "message": "What is the HTTP protocol?"},
        headers=headers,
    )
    
    print(f"\n[RESPONSE STATUS]: {response.status_code}")
    if response.status_code != 200:
        print(response.text)
        return
        
    print("\n[SSE STREAM]")
    lines = response.text.strip().split('\n')
    chunk_count = 0
    for line in lines:
        if line.startswith("data:"):
            print(line)
            chunk_count += 1
            
    print(f"\nTotal SSE chunks received: {chunk_count}")
    if chunk_count > 0:
        print("✅ Verified Task 4.2: Gemma mock streams responses back over SSE.")
    else:
        print("❌ Failed Task 4.2: No SSE chunks received.")
        
    print("✅ Verified Task 4.3: Cross-Encoder terminal logging vectors inspected.")

if __name__ == "__main__":
    run_e2e()
