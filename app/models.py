
from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.database import Base


def current_time():
    return datetime.now(timezone.utc)

class Status(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    COMPLETED_WITH_ERRORS = "COMPLETED_WITH_ERRORS"
    
class GenerationJob(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PENDING", nullable=False)

    event_name = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    organization = Column(String, nullable=False)

    total_count = Column(Integer, default=0, nullable=False)
    success_count = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime(timezone=True), default=current_time)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    certificates = relationship(
        "Certificate",
        back_populates="job",
        cascade="all, delete-orphan",
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)

    job_id = Column(
        Integer,
        ForeignKey("jobs.id"),
        nullable=False,
    )

    recipient_name = Column(String, nullable=False)
    recipient_email = Column(String, nullable=False)

    status = Column(String, default="PENDING", nullable=False)
    file_path = Column(String, nullable=True)
    error_message = Column(String, nullable=True)

    job = relationship(
        "GenerationJob",
        back_populates="certificates",
    )