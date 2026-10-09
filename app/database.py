
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database file will be created in the project root.
DATABASE_URL = "sqlite:///./certificates.db"

# Create a connection to the database.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create database sessions.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for our database models.
Base = declarative_base()


# Provides a database session to API endpoints.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()