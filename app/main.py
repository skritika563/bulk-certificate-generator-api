
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.database import Base, engine
from app.routes.certificates import router

# Create database tables if they do not exist.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    description=(
        "An API for generating certificates in bulk, "
        "tracking job progress, and retrieving generated PDFs."
    ),
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}