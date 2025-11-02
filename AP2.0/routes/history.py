from fastapi import APIRouter, HTTPException

from services.db_service import DatabaseService
from models.schemas import HistoryEntry

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/{district_name}", response_model=list[HistoryEntry])
async def get_district_history(district_name: str):
    """
    Retrieve version history for a specific district
    
    Returns all document uploads and extractions for the district,
    including both latest and historical versions.
    """
    db_service = DatabaseService()
    history = db_service.get_district_history(district_name)
    
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"No history found for district: {district_name}"
        )
    
    return [
        HistoryEntry(
            document_id=entry["document_id"],
            file_name=entry["file_name"],
            upload_date=entry["upload_date"],
            uploaded_by=entry["uploaded_by"],
            sector_name=entry["sector_name"],
            sub_category=entry["sub_category"],
            version_date=entry["version_date"],
            is_latest=entry["is_latest"]
        )
        for entry in history
    ]

