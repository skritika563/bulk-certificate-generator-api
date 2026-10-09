# Bulk Certificate Generator API

A REST API built with **FastAPI** that generates certificates in bulk from a recipient details list. It validates input data, generates PDF certificates using a predefined template, tracks generation progress, handles individual certificate failures, and allows generated certificates to be downloaded.

The API supports both **JSON** requests and **Excel (.xlsx)** uploads, making it suitable for generating certificates for workshops, seminars, training programs, and other events.

## Features

- **Bulk generation :** Create certificates for multiple recipients through a single API request.
- **Input validation :** Validate recipient names, email addresses, event details, and dates.
- **Excel upload :** Upload an Excel file containing recipient names and email addresses.
- **PDF generation :** Generate individual PDF certificates using a predefined template.
- **Background processing :** Process certificate generation after accepting a job request.
- **Job tracking :** Monitor job status, total recipients, successful certificates, failed certificates, and completed work.
- **Individual error handling :** A failure while generating one certificate does not stop the remaining recipients from being processed.
- **Certificate retrieval :** View the results of a generation job and download individual PDF certificates.
- **Automated testing :** Includes tests for job creation, input validation, certificate generation, progress tracking, failure handling, and certificate retrieval.

## Technology Stack

| Technology | Purpose                                            |
| ---------- | -------------------------------------------------- |
| Python     | Backend programming language                       |
| FastAPI    | REST API framework                                 |
| Uvicorn    | Runs the API server                                |
| SQLAlchemy | Database operations and ORM                        |
| SQLite     | Stores generation jobs and certificate records     |
| Pydantic   | Request validation and data schemas                |
|OpenPyXL    | Reading Excel recipient files                      |
| ReportLab  | Generates PDF certificates                         |
| pytest     | Automated testing                                  |
| HTTPX      | Supports API testing through FastAPI's test client |


## Project Structure

```text
bulk-certificate-generator-api/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   └── certificates.py
│   │
│   └── services/
│       └── certificate_generator.py
│
├── tests/
│   ├── __init__.py
│   └── test_certificates.py
│
├── generated_certificates/
│
├── requirements.txt
├── README.md
└── .gitignore
```

### Folder and File Description

- `app/main.py`: Initializes the FastAPI application and creates the database tables.
- `app/database.py`: Configures the SQLite database and SQLAlchemy sessions.
- `app/models.py`: Defines database models for generation jobs and certificates.
- `app/schemas.py`: Defines request validation rules and API response structures.
- `app/routes/certificates.py`: Implements the API endpoints, job processing, Excel upload, and certificate retrieval.
- `app/services/certificate_generator.py`: Generates individual PDF certificates using the predefined template.
- `tests/test_certificates.py`: Contains automated tests for the main API features.
- `generated_certificates/`: Stores the generated PDF files.
- `requirements.txt`: Lists the Python dependencies required to run the application.

The SQLite database file and generated PDFs are created locally when the application runs.

## 1. Project Setup

### Prerequisites

* Python 3.11 or later recommended.
* pip, the Python package installer.

### Create a virtual environment

On Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

The virtual environment keeps the project's Python dependencies separate from other Python projects.

## 2. Run the Application

Start the development server from the project root:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

### Interactive API documentation

Open the following URL in a browser:

`http://127.0.0.1:8000/docs`

Swagger UI allows you to submit requests, inspect responses, and test endpoints without building a frontend.

### Health check

Send a GET request to:

`http://127.0.0.1:8000/health`

Expected response:

```json
{
  "status": "healthy"
}
```

#### Overall 
The API will be available at:

- **API base URL:** http://127.0.0.1:8000
- **Interactive API documentation:** http://127.0.0.1:8000/docs
- **Alternative API documentation:** http://127.0.0.1:8000/redoc
- **Health check:** http://127.0.0.1:8000/health

## 3. API Endpoints

All certificate-related endpoints use the `/api` prefix.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check whether the API is running |
| GET | `/health` | Check application health |
| POST | `/api/jobs` | Create a bulk certificate generation job using JSON |
| POST | `/api/jobs/upload` | Create a job by uploading an Excel file |
| GET | `/api/jobs/{job_id}` | Retrieve job status and progress |
| GET | `/api/jobs/{job_id}/certificates` | Retrieve certificate results for a job |
| GET | `/api/certificates/{certificate_id}` | Download an individual PDF certificate |

You can try these endpoints through the interactive Swagger documentation at `http://127.0.0.1:8000/docs`.

## Using API Endpoints

### 1. Submit a Certificate Generation Request Using JSON

**Endpoint:** `POST /api/jobs`

Send a JSON request containing the event details and recipient list.

Example request:

```json
{
  "event_name": "Python Workshop",
  "event_date": "2026-10-15",
  "organization": "ABC College",
  "recipients": [
    {
      "name": "Aarav Sharma",
      "email": "aarav@example.com"
    },
    {
      "name": "Ananya Rao",
      "email": "ananya@example.com"
    },
    {
      "name": "Rohan Kumar",
      "email": "rohan@example.com"
    }
  ]
}
```

Example response:

```json
{
  "job_id": 1,
  "status": "PENDING",
  "total_recipients": 3
}
```

The API creates a job record and recipient certificate records, then schedules certificate generation in the background. The response includes the job ID, which can be used to check progress and retrieve results.

#### Validation Rules

- Event name and organization must not be empty.
- The event date must be a valid date.
- Each recipient must have a name and a valid email address.
- Recipient names must contain between 1 and 100 characters.
- A job must contain at least one recipient.
- A maximum of 500 recipients is allowed per job.

### 2. Creating a Generation Request Using Excel

**Endpoint:** `POST /api/jobs/upload`

The API accepts an `.xlsx` Excel file along with the event details.

The first worksheet must contain columns named `Name` and `Email`. Column matching is case-insensitive.

Example:

| Name | Email |
|---|---|
| Aarav Sharma | aarav@example.com |
| Ananya Rao | ananya@example.com |
| Rohan Kumar | rohan@example.com |

Include these additional form fields in the request:

- `event_name`
- `event_date`
- `organization`

The file must be no larger than 5 MB. The API validates the recipient rows and rejects invalid recipient data before creating the job.

You can test this endpoint in Swagger by selecting `POST /api/jobs/upload`, clicking **Try it out**, entering the event details, selecting an Excel file, and executing the request.

### 3. Checking Job Status and Progress

**Endpoint:** `GET /api/jobs/{job_id}`

Replace `{job_id}` with the ID returned when creating the job.

Example response:

```json
{
  "job_id": 1,
  "status": "COMPLETED",
  "total": 3,
  "successful": 3,
  "failed": 0,
  "completed": 3
}
```

The response provides:

- `total`: Total number of recipients in the job.
- `successful`: Number of certificates generated successfully.
- `failed`: Number of certificates that failed to generate.
- `completed`: Total number of recipients processed, including successes and failures.

The job status indicates the current or final state of the generation process.

### 4. Retrieving Certificate Results

**Endpoint:** `GET /api/jobs/{job_id}/certificates`

This endpoint returns the certificate records associated with a generation job, including recipient details, certificate status, and error messages when applicable.

Example response:

```json
{
  "job_id": 1,
  "certificates": [
    {
      "certificate_id": 1,
      "recipient_name": "Aarav Sharma",
      "recipient_email": "aarav@example.com",
      "status": "SUCCESS",
      "error_message": null
    },
    {
      "certificate_id": 2,
      "recipient_name": "Ananya Rao",
      "recipient_email": "ananya@example.com",
      "status": "SUCCESS",
      "error_message": null
    }
  ]
}
```

### 5. Downloading a Certificate

**Endpoint:** `GET /api/certificates/{certificate_id}`

Replace `{certificate_id}` with the ID of the certificate you want to download.

The endpoint returns the generated PDF file when the certificate is available. If the certificate does not exist or has not been generated successfully, the API returns an appropriate error response.

## Job and Certificate Processing

The application follows this workflow:

1. The client submits a bulk generation request through JSON or Excel.
2. The API validates the event details and recipient information.
3. A generation job and individual certificate records are stored in SQLite.
4. The API schedules the generation task and returns the job ID.
5. The background task generates a PDF for each recipient.
6. Each certificate record is updated with its status and generated file path, or an error message if generation fails.
7. The job's success count, failure count, final status, and completion time are updated.
8. The client checks job progress, retrieves certificate results, and downloads available PDFs.

Each recipient is processed independently. If one certificate fails, the application continues processing the other recipients.

## Running Automated Tests

Make sure the virtual environment is activated and the project dependencies are installed.

Run:

```bash
python -m pytest -v
```

The test suite covers the following cases:

1. Creating a generation job.
2. Rejecting an invalid email address.
3. Rejecting an invalid date.
4. Generating a certificate.
5. Checking job status and progress.
6. Handling an individual certificate generation failure.
7. Retrieving a generated certificate.

### Latest Test Results

**7 passed, 0 failed.**

The tests completed successfully in 2.38 seconds. A deprecation warning related to the Starlette test client and `httpx` was displayed; it did not cause any test failures.

## Design Decisions

### 1. FastAPI

FastAPI was selected to build the REST API because it supports request validation, clear endpoint definitions, and automatic interactive documentation.

### 2. SQLite and SQLAlchemy

SQLite provides persistent local storage without requiring a separate database server. SQLAlchemy manages the database models, relationships, and queries.

### 3. Background Processing

Certificate generation is scheduled as a background task so the client receives a job ID without waiting for every PDF to be generated. This implementation uses FastAPI's in-process background tasks.

### 4. Individual Failure Handling

Each certificate is generated within its own error-handling block. This allows the application to record failures for individual recipients while continuing with the remaining certificates.

### 5. PDF Generation

ReportLab generates certificates using a single predefined template. Each PDF is personalized with the relevant recipient and event details.

### 6. Excel Support

OpenPyXL reads recipient data from `.xlsx` files. This makes the application convenient for users who already maintain recipient lists in spreadsheets.

## Limitations and Future Improvements

- The application currently uses one predefined certificate template.
- SQLite is intended for a simple local deployment, a production deployment may require a more suitable database configuration.
- FastAPI's in-process background tasks are not a durable job queue. A task queue could be introduced for larger workloads and recovery after server restarts.
- Generated PDFs are stored on the local filesystem, so persistent object storage could be added for deployment across multiple servers.
- Authentication, authorization, rate limiting, and additional production security controls could be added before exposing the API publicly.
- The current Excel upload supports `.xlsx` files, rather than CSV or legacy `.xls` files.


## Conclusion

The Bulk Certificate Generator API provides a simple way to submit one request for multiple recipients, generate PDF certificates, track processing progress, handle individual failures, and retrieve completed certificates. The design keeps the implementation manageable while demonstrating API development, input validation, database modelling, background processing, PDF generation, and automated testing.
