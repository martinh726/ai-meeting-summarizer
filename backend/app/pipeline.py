import time

from sqlmodel import Session

from app.db import engine
from app.models import Meeting, MeetingStatus, utcnow

# Phase 1 placeholder: how long each fake step "takes". Replaced by real work in Phases 2-3.
FAKE_STEP_SECONDS = 2.0


def _set_status(session: Session, meeting: Meeting, status: MeetingStatus) -> None:
    meeting.status = status
    meeting.updated_at = utcnow()
    session.add(meeting)
    session.commit()


def process_meeting(meeting_id: int) -> None:
    """Run the full pipeline for one meeting. Runs as a background task after upload.

    Opens its own DB session because the request's session is closed once the
    response has been sent.
    """
    with Session(engine) as session:
        meeting = session.get(Meeting, meeting_id)
        if meeting is None:
            return

        try:
            _set_status(session, meeting, MeetingStatus.transcribing)
            start = time.perf_counter()
            time.sleep(FAKE_STEP_SECONDS)  # TODO Phase 2: compress, chunk, transcribe
            meeting.transcript = "(placeholder transcript)"
            meeting.transcribe_seconds = time.perf_counter() - start

            _set_status(session, meeting, MeetingStatus.summarizing)
            start = time.perf_counter()
            time.sleep(FAKE_STEP_SECONDS)  # TODO Phase 3: extract summary with Claude
            meeting.summary = {"summary": "(placeholder summary)", "decisions": [], "action_items": []}
            meeting.summarize_seconds = time.perf_counter() - start

            _set_status(session, meeting, MeetingStatus.done)
        except Exception as exc:
            meeting.error = str(exc)
            _set_status(session, meeting, MeetingStatus.failed)
