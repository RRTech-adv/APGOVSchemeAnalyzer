from fastapi import APIRouter, HTTPException
from typing import Optional

from services.db_service import DatabaseService
from services.extraction_service import ExtractionService

router = APIRouter(prefix="/extract", tags=["extract"])

@router.post("/{document_id}")
async def re_extract(document_id: int):
    """
    Trigger re-extraction for a specific document
    
    This will re-process the document and update extractions,
    marking previous versions as not latest.
    """
    db_service = DatabaseService()
    extraction_service = ExtractionService()
    
    # Get document details
    conn = db_service.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, district_id, file_path, upload_date, uploaded_by
        FROM documents
        WHERE id = ?
    """, (document_id,))
    
    doc_row = cursor.fetchone()
    conn.close()
    
    if not doc_row:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get district name
    conn = db_service.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM districts WHERE id = ?", (doc_row[1],))
    district_row = cursor.fetchone()
    conn.close()
    
    if not district_row:
        raise HTTPException(status_code=404, detail="District not found")
    
    district_name = district_row[0]
    file_path = doc_row[2]
    upload_date = doc_row[3]
    
    # Read document text
    from services.parser_service import ParserService
    parser = ParserService()
    
    try:
        document_text = parser.extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading document: {str(e)}")
    
    if not document_text:
        raise HTTPException(status_code=500, detail="Failed to extract text from document")
    
    # Re-extract and store
    result = extraction_service.extract_and_store(
        document_id=document_id,
        district_name=district_name,
        document_text=document_text,
        upload_date=upload_date
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {result.get('error', 'Unknown error')}"
        )
    
    return {
        "message": f"Re-extraction completed successfully. {result.get('stored_extractions', 0)} extractions stored/updated.",
        "document_id": document_id,
        "stored_extractions": result.get("stored_extractions", 0),
        "errors": result.get("errors", [])
    }

