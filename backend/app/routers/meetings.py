import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlmodel import Session, select

from app.config import settings
from app.db import get_session
from app.models import Meeting, MeetingDetail, MeetingRead
from app.pipeline import process_meeting

router = APIRouter(prefix="/meetings", tags=["meetings"])

# Audio/video formats Whisper accepts, plus .txt for uploading an existing transcript.
ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".wav", ".webm", ".ogg", ".flac", ".txt"}

UPLOAD_DIR = settings.data_dir / "uploads"


@router.post("", response_model=MeetingRead, status_code=201)
def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str | None = Form(None),
    session: Session = Depends(get_session),
):
    """Save the uploaded recording, create a meeting, and start processing in the background."""
    filename = file.filename or "recording"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}")

    # Store under a random name so two uploads called "meeting.mp3" don't overwrite each other.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    meeting = Meeting(
        title=title or Path(filename).stem,
        original_filename=filename,
        file_path=str(dest),
    )
    session.add(meeting)
    session.commit()
    session.refresh(meeting)

    # Runs after the response is sent, so the upload request returns immediately.
    background_tasks.add_task(process_meeting, meeting.id)
    return meeting


@router.get("", response_model=list[MeetingRead])
def list_meetings(session: Session = Depends(get_session)):
    return session.exec(select(Meeting).order_by(Meeting.created_at.desc())).all()


@router.get("/{meeting_id}", response_model=MeetingDetail)
def get_meeting(meeting_id: int, session: Session = Depends(get_session)):
    meeting = session.get(Meeting, meeting_id)
    if meeting is None:
        raise HTTPException(404, "Meeting not found")
    return meeting
