
from datetime import date
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RecipientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr


class GenerationJobInput(BaseModel):
    event_name: str = Field(min_length=1, max_length=200)
    event_date: date
    organization: str = Field(min_length=1, max_length=200)

    recipients: list[RecipientInput] = Field(
        min_length=1,
        max_length=500
    )

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")


class GenerationJobResponse(BaseModel):
    job_id: int
    status: str
    total_recipients: int


class CertificateResponse(BaseModel):
    certificate_id: int
    recipient_name: str
    recipient_email: str
    status: str
    error_message: str | None = None


class JobStatusResponse(BaseModel):
    job_id: int
    status: str
    total: int
    successful: int
    failed: int
    completed: int


class CertificateResultList(BaseModel):
    job_id: int
    certificates: list[CertificateResponse]