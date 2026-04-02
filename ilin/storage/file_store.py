"""Document file storage management."""

# Developer: Vishal Raj V, Senior Engineer

import shutil
from pathlib import Path

from fastapi import UploadFile

from ilin.config import settings


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".pptx", ".xlsx", ".md", ".markdown"}


def save_upload_file(upload_file: UploadFile, topic_id: int, document_id: int) -> Path:
    """Save an uploaded file to the documents directory. Returns file path."""
    ext = Path(str(upload_file.filename)).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    dest_dir = settings.data_dir / "documents" / str(topic_id)
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_path = dest_dir / f"{document_id}_{upload_file.filename}"
    with open(dest_path, "wb") as f:
        content = upload_file.file.read()
        f.write(content)
    return dest_path


def delete_file(file_path: Path):
    """Delete a file from disk."""
    if file_path.exists():
        file_path.unlink()


def delete_topic_files(topic_id: int):
    """Delete all files for a topic."""
    topic_dir = settings.data_dir / "documents" / str(topic_id)
    if topic_dir.exists():
        shutil.rmtree(topic_dir)


def get_file_size(file_path: Path) -> int:
    """Get file size in bytes."""
    return file_path.stat().st_size
