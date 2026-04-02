"""Chat API endpoints: chat query (SSE streaming), history, export."""

# Developer: Vishal Raj V, Senior Engineer

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ilin.api.dependencies import get_current_user, get_db
from ilin.storage.models import ChatMessage, ChatSession, TopicAssignment, User


router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat_query(
    topic_id: int,
    message: str,
    session_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Chat with a topic. Returns streaming SSE response."""
    if current_user.role != "admin":
        assignment = (
            db.query(TopicAssignment)
            .filter(
                TopicAssignment.topic_id == topic_id,
                TopicAssignment.user_id == current_user.id,
            )
            .first()
        )
        if assignment is None:
            raise HTTPException(status_code=403, detail="No access to this topic")

    if session_id:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    else:
        session = ChatSession(user_id=current_user.id, topic_id=topic_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    user_msg = ChatMessage(session_id=session.id, role="user", content=message)
    db.add(user_msg)
    db.commit()

    history_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at)
        .all()
    )
    chat_history = "\n".join(f"{m.role}: {m.content}" for m in history_msgs[:-1])

    from ilin.core.rag_engine import RAGEngine

    engine = RAGEngine()
    context = engine.retrieve_context(topic_id, message)
    if not context:

        async def no_context_stream():
            yield (
                "data: "
                + json.dumps(
                    {
                        "content": "I don't have enough information to answer that. No relevant documents found.",
                        "sources": [],
                    }
                )
                + "\n\n"
            )
            yield "data: [DONE]\n\n"

        return StreamingResponse(no_context_stream(), media_type="text/event-stream")

    prompt = engine.build_prompt(message, context, chat_history)

    async def generate():
        full_response = ""
        sources = [
            {
                "text": r["metadata"]["text"][:200] + "...",
                "source_file": r["metadata"].get("source_file", ""),
                "page_number": r["metadata"].get("page_number"),
                "score": r["score"],
            }
            for r in context
        ]
        try:
            async for chunk in engine.generate_response(prompt):
                full_response += chunk
                yield "data: " + json.dumps({"content": chunk, "sources": []}) + "\n\n"
        except Exception as e:
            yield "data: " + json.dumps({"error": str(e)}) + "\n\n"

        yield (
            "data: "
            + json.dumps({"content": "", "sources": sources, "done": True})
            + "\n\n"
        )
        yield "data: [DONE]\n\n"

        assistant_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=full_response,
            sources=sources,
        )
        db.add(assistant_msg)
        session.updated_at = datetime.now(timezone.utc)
        db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/history")
def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all chat sessions for current user."""
    sessions = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == current_user.id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "topic_id": s.topic_id,
            "topic_name": s.topic.name if s.topic else "Unknown",
            "created_at": str(s.created_at),
            "updated_at": str(s.updated_at),
            "message_count": len(s.messages),
        }
        for s in sessions
    ]


@router.get("/history/{session_id}")
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all messages in a chat session."""
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": m.sources,
            "created_at": str(m.created_at),
        }
        for m in session.messages
    ]


@router.get("/history/{session_id}/export")
def export_chat(
    session_id: int,
    format: str = Query(default="txt"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export chat session as TXT or JSON."""
    if format not in ("txt", "json"):
        raise HTTPException(status_code=400, detail="Format must be 'txt' or 'json'")

    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if format == "json":
        messages = [
            {
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "created_at": str(m.created_at),
            }
            for m in session.messages
        ]
        return {
            "session_id": session.id,
            "topic": session.topic.name if session.topic else "",
            "messages": messages,
        }
    else:
        text = f"Chat Session: {session.topic.name if session.topic else 'Unknown'}\n"
        text += f"Date: {session.created_at}\n" + "=" * 50 + "\n\n"
        for m in session.messages:
            text += f"{m.role.upper()}: {m.content}\n\n"
        return {"content": text}
