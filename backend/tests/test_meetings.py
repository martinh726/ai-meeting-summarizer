def test_upload_runs_pipeline_to_done(client):
    resp = client.post(
        "/meetings",
        files={"file": ("standup.mp3", b"fake audio bytes", "audio/mpeg")},
    )
    assert resp.status_code == 201
    created = resp.json()
    assert created["title"] == "standup"
    assert created["status"] == "uploaded"

    # TestClient runs background tasks before returning, so processing is already finished.
    detail = client.get(f"/meetings/{created['id']}").json()
    assert detail["status"] == "done"
    assert detail["summary"] is not None
    assert detail["transcribe_seconds"] is not None

    listed = client.get("/meetings").json()
    assert any(m["id"] == created["id"] for m in listed)
    assert "transcript" not in listed[0]


def test_rejects_unsupported_file_type(client):
    resp = client.post("/meetings", files={"file": ("notes.pdf", b"%PDF", "application/pdf")})
    assert resp.status_code == 400


def test_missing_meeting_returns_404(client):
    assert client.get("/meetings/99999").status_code == 404
