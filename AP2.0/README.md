# Arunachal Schemes Backend

A FastAPI backend application that uses Google Gemini LLM for extracting structured data from scheme documents related to Arunachal Pradesh, stores all extracted data district-wise in a local SQLite3 database, and allows users to chat/query the information naturally.

## Features

- **File Upload**: Accept PDF, DOCX, and TXT files with district metadata
- **Gemini-Powered Extraction**: Automatically extract structured data using Google Gemini LLM
- **SQLite3 Database**: Local database with district-wise schema and version management
- **Chat Interface**: Natural language querying of scheme data
- **Supporting Endpoints**: Districts, categories, history, and re-extraction

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The API configuration is in `config.py`. The Gemini API key is already configured, but you can modify it if needed.

## Database

The SQLite database (`arunachal_schemes.db`) is automatically created on first run with the following schema:
- `districts`: District information
- `documents`: Uploaded documents metadata
- `extractions`: Extracted structured data with version management

## Running the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Upload Document
- **POST** `/upload`
  - Upload PDF, DOCX, or TXT files
  - Required form fields: `file`, `district_name`, `uploaded_by`, `upload_date` (optional)

### Chat Interface
- **POST** `/chat`
  - Query district-wise scheme information
  - Request body: `district_name`, optional `sector_name`, `sub_category`, `question`

### Re-extract Document
- **POST** `/extract/{document_id}`
  - Trigger re-extraction for a specific document

### List Districts
- **GET** `/districts`
  - Get all districts with document counts

### List Categories
- **GET** `/categories`
  - Get all sectors and sub-categories

### District History
- **GET** `/history/{district_name}`
  - Get version history for a district

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
/app
  /routes
    upload.py
    chat.py
    extract.py
    districts.py
    categories.py
    history.py
  /services
    gemini_client.py
    parser_service.py
    extraction_service.py
    db_service.py
  /models
    schemas.py
  main.py
  config.py
  requirements.txt
```

## Notes

- The extraction schema enforces consistency across all uploads
- Version management automatically marks previous extractions as outdated when new data is uploaded
- The chat interface uses Gemini to query the SQLite database and provide conversational responses

