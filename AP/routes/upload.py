from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import os
import shutil
from datetime import datetime
from pathlib import Path

from services.parser_service import ParserService
from services.db_service import DatabaseService
from services.extraction_service import ExtractionService
from models.schemas import UploadResponseModel
from config import settings

router = APIRouter(prefix="/upload", tags=["upload"])

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=UploadResponseModel)
async def upload_document(
    file: UploadFile = File(...),
    district_name: str = Form(...),
    uploaded_by: str = Form(...),
    upload_date: Optional[str] = Form(None)
):
    """
    Upload a document (PDF, DOCX, or TXT) and extract structured data
    
    **Note: District must exist before uploading. Use POST /districts/ to create a district first.**
    
    Required form fields:
    - file: The document file
    - district_name: Name of the district (must exist - create it first using POST /districts/)
    - uploaded_by: Name/ID of the person uploading
    - upload_date: Optional date in YYYY-MM-DD format (defaults to today)
    
    Example:
    1. First create district: POST /districts/ {"district_name": "Tawang"}
    2. Then upload: POST /upload/ with file and district_name="Tawang"
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    # Try to get file size from the UploadFile object
    file_size = 0
    try:
        # Some UploadFile implementations have a size attribute
        if hasattr(file, 'size') and file.size:
            file_size = file.size
        else:
            # Fallback: try to read size by seeking
            current_pos = file.file.tell()
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(current_pos)  # Reset to original position
    except (AttributeError, OSError):
        # If we can't determine size, we'll check after saving
        pass
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size ({file_size / (1024*1024):.2f} MB) exceeds maximum allowed size ({settings.MAX_FILE_SIZE / (1024*1024)} MB)"
        )
    
    # Set upload date if not provided
    if not upload_date:
        upload_date = datetime.now().strftime("%Y-%m-%d")
    
    # Validate date format
    try:
        datetime.strptime(upload_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="upload_date must be in YYYY-MM-DD format"
        )
    
    # Validate that district exists before allowing upload
    db_service = DatabaseService()
    existing_districts = db_service.get_district_names_list()
    
    if district_name not in existing_districts:
        raise HTTPException(
            status_code=404,
            detail=f"District '{district_name}' does not exist. Please create the district first using POST /districts/ with district_name: '{district_name}'"
        )
    
    # Save file
    file_path = os.path.join(settings.UPLOAD_DIR, f"{datetime.now().timestamp()}_{file.filename}")
    
    try:
        # Write file and check size as we write
        written_size = 0
        with open(file_path, "wb") as buffer:
            # Read in chunks to avoid memory issues with large files
            chunk_size = 1024 * 1024  # 1MB chunks
            while True:
                chunk = file.file.read(chunk_size)
                if not chunk:
                    break
                buffer.write(chunk)
                written_size += len(chunk)
                
                # Check size during write to prevent exceeding limit
                if written_size > settings.MAX_FILE_SIZE:
                    buffer.close()
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise HTTPException(
                        status_code=400,
                        detail=f"File size exceeds maximum allowed size ({settings.MAX_FILE_SIZE / (1024*1024)} MB)"
                    )
        
        # Reset file pointer for later use if needed
        file.file.seek(0)
        
        # Extract text from file
        parser = ParserService()
        document_text = parser.extract_text(file_path)
        
        if not document_text:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract text from document"
            )
        
        # Get district ID (district already exists, so we can safely get it)
        district_id = db_service.get_or_create_district(district_name)
        
        document_id = db_service.create_document(
            district_id=district_id,
            file_name=file.filename,
            file_path=file_path,
            upload_date=upload_date,
            uploaded_by=uploaded_by,
            raw_text=document_text
        )
        
        # Extract and store structured data
        extraction_service = ExtractionService()
        extraction_result = extraction_service.extract_and_store(
            document_id=document_id,
            district_name=district_name,
            document_text=document_text,
            upload_date=upload_date
        )
        
        if not extraction_result.get("success"):
            # Document is saved but extraction failed
            return {
                "status": "partial_success",
                "message": f"Document uploaded but extraction failed: {extraction_result.get('error', 'Unknown error')}"
            }
        
        return {
            "status": "success",
            "message": f"Data extracted and stored for {district_name}"
        }
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

