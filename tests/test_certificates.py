
from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Certificate, GenerationJob
from app.services.certificate_generator import generate_certificate

client = TestClient(app)


def test_create_generation_job():
    """A valid request should create a bulk generation job."""

    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-10",
            "organization": "ABC Technologies",
            "recipients": [
                {
                    "name": "Aarav Kumar",
                    "email": "aarav@example.com",
                },
                {
                    "name": "Priya Nair",
                    "email": "priya@example.com",
                },
            ],
        },
    )

    assert response.status_code == 202

    data = response.json()
    assert "job_id" in data
    assert data["total_recipients"] == 2
    assert data["status"] == "PENDING"


def test_invalid_email_is_rejected():
    """An invalid email should be rejected before a job is created."""

    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-10",
            "organization": "ABC Technologies",
            "recipients": [
                {
                    "name": "Aarav Kumar",
                    "email": "not-an-email",
                },
            ],
        },
    )

    assert response.status_code == 422


def test_invalid_date_is_rejected():
    """A date that is not in the expected format should be rejected."""

    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "not-a-date",
            "organization": "ABC Technologies",
            "recipients": [
                {
                    "name": "Aarav Kumar",
                    "email": "aarav@example.com",
                },
            ],
        },
    )

    assert response.status_code == 422


def test_certificate_generation():
    """The generator should create a non-empty PDF file."""

    file_path = generate_certificate(
        certificate_id=987654,
        recipient_name="Test Recipient",
        event_name="Python Workshop",
        event_date="2026-10-10",
        organization="ABC Technologies",
    )

    try:
        pdf_path = Path(file_path)

        assert pdf_path.is_file()
        assert pdf_path.stat().st_size > 0
        assert pdf_path.read_bytes().startswith(b"%PDF")
    finally:
        Path(file_path).unlink(missing_ok=True)


def test_job_status_and_progress():
    """The status endpoint should report the correct job progress."""

    db = SessionLocal()

    try:
        job = GenerationJob(
            status="PROCESSING",
            total_count=3,
            success_count=2,
            failed_count=1,
            event_name="Python Workshop",
            event_date=date(2026, 10, 10),
            organization="ABC Technologies",
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        job_id = job.id
    finally:
        db.close()

    response = client.get(f"/api/jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["job_id"] == job_id
    assert data["total"] == 3
    assert data["successful"] == 2
    assert data["failed"] == 1
    assert data["completed"] == 3


def test_individual_certificate_failure(monkeypatch):
    """One failed certificate should not stop other recipients."""

    from app.routes import certificates as certificate_routes

    original_generator = certificate_routes.generate_certificate

    def sometimes_fail(**kwargs):
        if kwargs["recipient_name"] == "Failure Recipient":
            raise RuntimeError("Simulated PDF generation failure")

        return original_generator(**kwargs)

    monkeypatch.setattr(
        certificate_routes,
        "generate_certificate",
        sometimes_fail,
    )

    response = client.post(
        "/api/jobs",
        json={
            "event_name": "Python Workshop",
            "event_date": "2026-10-10",
            "organization": "ABC Technologies",
            "recipients": [
                {
                    "name": "Success Recipient",
                    "email": "success@example.com",
                },
                {
                    "name": "Failure Recipient",
                    "email": "failure@example.com",
                },
            ],
        },
    )

    assert response.status_code == 202

    job_id = response.json()["job_id"]

    status_response = client.get(f"/api/jobs/{job_id}")

    assert status_response.status_code == 200

    data = status_response.json()
    assert data["successful"] == 1
    assert data["failed"] == 1
    assert data["completed"] == 2
    assert data["status"] == "COMPLETED_WITH_ERRORS"


def test_retrieve_generated_certificate():
    """A successful certificate should be downloadable as a PDF."""

    db = SessionLocal()
    file_path = None

    try:
        job = GenerationJob(
            status="COMPLETED",
            total_count=1,
            success_count=1,
            failed_count=0,
            event_name="Python Workshop",
            event_date=date(2026, 10, 10),
            organization="ABC Technologies",
        )

        db.add(job)
        db.flush()

        file_path = generate_certificate(
            certificate_id=987655,
            recipient_name="Download Test",
            event_name="Python Workshop",
            event_date="2026-10-10",
            organization="ABC Technologies",
        )

        certificate = Certificate(
            job_id=job.id,
            recipient_name="Download Test",
            recipient_email="download@example.com",
            status="SUCCESS",
            file_path=file_path,
        )

        db.add(certificate)
        db.commit()
        db.refresh(certificate)

        certificate_id = certificate.id
    finally:
        db.close()

    try:
        response = client.get(
            f"/api/certificates/{certificate_id}"
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content.startswith(b"%PDF")
    finally:
        if file_path:
            Path(file_path).unlink(missing_ok=True)